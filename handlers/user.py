# handlers/user.py
import os
from aiogram import types, Router
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, LabeledPrice, PreCheckoutQuery, InputFile
from db.database import SessionLocal
from db.models import User, VpnClient, Payment
from utils.vpn_config import generate_vpn_keys, generate_vpn_config, restart_wireguard, add_client_to_wg_config
from utils.ip_manager import get_free_ip
from utils.qr_generator import generate_qr_code
from aiohttp import ClientConnectionError
from aiogram.types import FSInputFile  # замените InputFile на FSInputFile

import asyncio
import logging
from datetime import datetime
import config
from aiogram import F
from db.mongodb import get_mongo_collection
from bson.objectid import ObjectId
from utils.vpn_config import save_config_to_mongodb
import qrcode
from pymongo import MongoClient
from aiogram.types import InputFile
import zipfile

router = Router()

PROVIDER_TOKEN = '381764678:TEST:93797'  # Замените на ваш тестовый токен ЮKassa

async def cmd_start(message: types.Message):
    """Обработчик команды /start."""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Подключить VPN", callback_data="get_vpn_key")],
        [InlineKeyboardButton(text="Оплатить VPN", callback_data="pay_vpn")],
        [InlineKeyboardButton(text="Добавить роутер", callback_data="add_router")]
    ])
    
    await message.answer(
        text="Добро пожаловать в VPN бот! Нажмите кнопку ниже, чтобы подключиться к VPN.",
        reply_markup=keyboard
    )

async def cmd_help(message: types.Message):
    """Обработчик команды /help."""
    await message.answer("/start - Начать работу\n/help - Показать это сообщение\n/status - Проверить статус вашего VPN")

async def cmd_status(message: types.Message):
    """Обработчик команды /status."""
    await message.answer("Ваш VPN активен.")

async def handle_get_vpn_key(callback_query: types.CallbackQuery):
    telegram_id = callback_query.from_user.id
    session = SessionLocal()

    try:
        logging.info("Подключение к базе данных успешно установлено.")
        user = session.query(User).filter(User.telegram_id == telegram_id).first()

        if not user:
            logging.info(f"Пользователь {telegram_id} не найден, создаем нового.")
            user = User(
                telegram_id=telegram_id,
                username=callback_query.from_user.username or '',
                full_name=callback_query.from_user.full_name or '',
            )
            session.add(user)
            session.commit()
            await callback_query.message.answer("Вы были зарегистрированы в системе.")

        client = session.query(VpnClient).filter(VpnClient.user_id == user.id).first()

        if client:
            logging.info(f"Клиент VPN уже существует для пользователя {telegram_id}, проверка наличия конфигурации.")
            if not client.config_file_id:
                logging.info("Конфигурационный файл отсутствует, создаем новый.")
                config_content = generate_vpn_config(client)
                try:
                    config_file_id = save_config_to_mongodb(config_content, telegram_id)
                    logging.info(f"Конфигурация сохранена в MongoDB с ID {config_file_id}")
                    client.config_file_id = str(config_file_id)
                    session.commit()
                    logging.info("Конфигурационный файл успешно создан и сохранен в MongoDB.")
                except Exception as e:
                    logging.error(f"Ошибка при сохранении конфигурации в MongoDB: {e}")
                add_client_to_wg_config(client)
            else:
                logging.info("Конфигурация уже существует.")
                await callback_query.message.answer("VPN клиент уже создан.")
        else:
            logging.info("Создание новой конфигурации VPN...")
            private_key, public_key = generate_vpn_keys()
            ip_address = get_free_ip(session)

            new_client = VpnClient(
                user_id=user.id,
                private_key=private_key,
                public_key=public_key,
                address=ip_address,
                dns=config.VPN_DNS,
                allowed_ips="0.0.0.0/0",
                endpoint=config.VPN_ENDPOINT
            )

            config_content = generate_vpn_config(new_client)
            try:
                config_file_id = save_config_to_mongodb(config_content, telegram_id)
                logging.info(f"Конфигурация сохранена в MongoDB с ID {config_file_id}")
                new_client.config_file_id = str(config_file_id)
                session.add(new_client)
                session.commit()
                logging.info("Новая конфигурация VPN успешно создана и сохранена.")
            except Exception as e:
                logging.error(f"Ошибка при сохранении конфигурации в MongoDB: {e}")
            add_client_to_wg_config(new_client)
            await callback_query.message.answer("VPN клиент успешно создан.")

        # Генерация кнопок для "Скачать конфигурацию" и "QR код"
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Скачать конфигурацию", callback_data="download_config")],
            [InlineKeyboardButton(text="QR код", callback_data="get_qr_code")]
        ])
        await callback_query.message.answer("Выберите действие:", reply_markup=keyboard)

    except Exception as e:
        logging.error(f"Произошла ошибка при обработке запроса VPN: {e}")
        await callback_query.message.answer("Произошла ошибка при обработке вашего запроса. Пожалуйста, попробуйте еще раз.")
    finally:
        session.close()
        logging.info("Сессия базы данных закрыта.")
        await callback_query.answer()


async def handle_get_qr_code(callback_query: types.CallbackQuery):
    """Обработчик для кнопки 'QR код'."""
    telegram_id = callback_query.from_user.id
    session = SessionLocal()

    try:
        user = session.query(User).filter(User.telegram_id == telegram_id).first()
        client = session.query(VpnClient).filter(VpnClient.user_id == user.id).first()
        
        if client:
            logging.info(f"Ищем config_file_id для пользователя {telegram_id}")
            if not client.config_file_id:
                await callback_query.message.answer("Не удалось найти конфигурационный файл.")
                return

            logging.info(f"config_file_id для пользователя {telegram_id}: {client.config_file_id}")

            # Соединение с MongoDB и получение документа конфигурации
            client_mongo = MongoClient("mongodb://localhost:27017/")
            db = client_mongo["vpn_bot"]
            collection = db["vpn_configs"]

            config_document = collection.find_one({"_id": ObjectId(client.config_file_id)})
            if not config_document:
                logging.error(f"Не удалось найти документ в MongoDB по config_file_id: {client.config_file_id}")
                await callback_query.message.answer("Не удалось найти конфигурационный файл.")
                return

            config_content = config_document["config"]

            # Генерация QR-кода
            qr_code_path = generate_qr_code(config_content, client_id=telegram_id)
            
            logging.info(f"QR-код сохранен в: {qr_code_path}")

            # Убедитесь, что файл QR-кода существует
            if os.path.exists(qr_code_path):
                # Использование FSInputFile вместо InputFile
                qr_file = FSInputFile(qr_code_path)
                await callback_query.message.answer_photo(qr_file, caption="Вот ваш QR-код для подключения к VPN.")
            else:
                logging.error(f"Ошибка: QR-код {qr_code_path} не существует.")
                await callback_query.message.answer("Ошибка при создании QR-кода.")
        else:
            await callback_query.message.answer("VPN клиент не найден. Пожалуйста, сначала зарегистрируйтесь.")

    except Exception as e:
        logging.error(f"An error occurred while handling QR code request: {e}")
        await callback_query.message.answer("Произошла ошибка при обработке вашего запроса.")
    finally:
        session.close()
        await callback_query.answer()


async def handle_download_config(callback_query: types.CallbackQuery):
    telegram_id = callback_query.from_user.id
    session = SessionLocal()

    try:
        user = session.query(User).filter(User.telegram_id == telegram_id).first()
        if not user:
            await callback_query.message.answer("Пользователь не найден. Пожалуйста, зарегистрируйтесь сначала.")
            return

        client = session.query(VpnClient).filter(VpnClient.user_id == user.id).first()

        if client:
            logging.info(f"Ищем config_file_id для пользователя {telegram_id}")
            if not client.config_file_id:
                await callback_query.message.answer("Не удалось найти конфигурационный файл.")
                return

            logging.info(f"config_file_id для пользователя {telegram_id}: {client.config_file_id}")

            collection = get_mongo_collection('vpn_configs')
            config_document = collection.find_one({"_id": ObjectId(client.config_file_id)})

            if not config_document:
                logging.error(f"Не удалось найти документ в MongoDB по config_file_id: {client.config_file_id}")
                await callback_query.message.answer("Не удалось найти конфигурационный файл.")
                return

            config_content = config_document["config"]

            # Сохранение конфигурации во временный файл
            temp_file_path = os.path.join("/var/www/html/configs", f"{telegram_id}.conf")
            with open(temp_file_path, 'w') as temp_file:
                temp_file.write(config_content)

            logging.info(f"Файл конфигурации сохранен в: {temp_file_path}")

            # Создание ZIP-архива
            zip_file_path = os.path.join("/var/www/html/configs", f"{telegram_id}.zip")
            with zipfile.ZipFile(zip_file_path, 'w') as zipf:
                zipf.write(temp_file_path, arcname=f"{telegram_id}.conf")
            
            logging.info(f"ZIP-архив создан по адресу: {zip_file_path}")

            # Убедитесь, что файл существует и не пустой
            if os.path.exists(zip_file_path) and os.path.getsize(zip_file_path) > 0:
                # Отправка ссылки пользователю
                base_url = "http://offonika.ru/configs/"
                config_filename = f"{telegram_id}.zip"
                config_url = base_url + config_filename
                await callback_query.message.answer(f"Скачайте ваш конфигурационный файл в архиве по следующей ссылке: {config_url}")
            else:
                logging.error(f"Ошибка: ZIP-архив {zip_file_path} не существует или пуст.")
                await callback_query.message.answer("Ошибка при создании ZIP-архива конфигурационного файла.")
        else:
            await callback_query.message.answer("VPN клиент не найден. Пожалуйста, сначала зарегистрируйтесь.")

    except Exception as e:
        logging.error(f"An error occurred while handling configuration download request: {e}")
        await callback_query.message.answer("Произошла ошибка при обработке вашего запроса.")
    finally:
        session.close()
        await callback_query.answer()

async def handle_get_instruction(callback_query: types.CallbackQuery):
    """Обработчик для кнопки 'Инструкция'."""
    instruction_text = (
        "## Инструкция по подключению к WireGuard VPN\n\n"
        "### 1. Запуск бота\n\n"
        "1. Откройте Telegram и найдите нашего бота по имени: [@OffonikaVPN_bot](https://t.me/OffonikaVPN_bot).\n"
        "2. Нажмите 'Старт' или введите команду `/start`, чтобы начать взаимодействие с ботом.\n\n"
        "### 2. Получение VPN-ключа\n\n"
        "1. После запуска бота вам будет предложено несколько опций. Выберите 'Подключить VPN' или введите команду `/get_vpn_key`.\n"
        "2. Если вы еще не зарегистрированы в системе, бот попросит вас подтвердить вашу регистрацию. Следуйте инструкциям, чтобы завершить регистрацию.\n"
        "3. Бот сгенерирует для вас ключи и конфигурацию VPN. Вы получите сообщение с несколькими кнопками, такими как 'QR код', 'Скачать конфигурацию' и 'Инструкция'.\n\n"
        "### 3. Скачивание конфигурационного файла\n\n"
        "1. Нажмите на кнопку 'Скачать конфигурацию' или используйте соответствующую команду.\n"
        "2. Бот отправит вам конфигурационный файл в формате `.conf`. Сохраните этот файл на своем устройстве.\n\n"
        "### 4. Генерация и получение QR-кода\n\n"
        "1. Нажмите на кнопку 'QR код' или используйте соответствующую команду, чтобы получить QR-код.\n"
        "2. Сохраните изображение QR-кода на вашем устройстве. Он может быть использован для быстрой настройки VPN на мобильных устройствах.\n\n"
        "### 5. Настройка VPN-клиента\n\n"
        "- **Для Windows/Linux/macOS:** Установите WireGuard и импортируйте конфигурационный файл.\n"
        "- **Для мобильных устройств (iOS/Android):** Установите приложение WireGuard и отсканируйте QR-код.\n\n"
        "### 6. Проверка подключения\n\n"
        "1. После настройки VPN-клиента проверьте свое подключение. Убедитесь, что ваше соединение через VPN активно.\n"
        "2. Для проверки вашего IP-адреса вы можете использовать любой онлайн-сервис для определения IP.\n\n"
        "### 7. Дополнительная помощь\n\n"
        "Если у вас возникли проблемы с подключением или настройкой VPN, вы можете обратиться за помощью в службу поддержки. Подробности и контактные данные доступны через команду `/help` в нашем Telegram-боте."
    )
    
    await callback_query.message.answer(instruction_text)
    await callback_query.answer()



async def process_pay_command(callback_query: types.CallbackQuery):
    """Обработчик команды для начала оплаты."""
    prices = [LabeledPrice(label='Подписка на VPN', amount=50000)]  # Цена в копейках (500.00 руб)
    await callback_query.message.bot.send_invoice(
        callback_query.from_user.id,
        title='Подписка на VPN',
        description='Оплатите подписку на VPN на 1 месяц',
        provider_token=PROVIDER_TOKEN,
        currency='RUB',
        prices=prices,
        payload='vpn-subscription-payload'
    )

@router.pre_checkout_query()
async def handle_pre_checkout_query(pre_checkout_query: PreCheckoutQuery):
    await pre_checkout_query.bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)

@router.message(F.content_type == types.ContentType.SUCCESSFUL_PAYMENT)
async def process_successful_payment(message: types.Message):
    """Обработчик успешного платежа."""
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.telegram_id == message.from_user.id).first()
        payment = Payment(
            user_id=user.id,
            telegram_payment_charge_id=message.successful_payment.telegram_payment_charge_id,
            provider_payment_charge_id=message.successful_payment.provider_payment_charge_id,
            amount=message.successful_payment.total_amount / 100,  # Конвертация копеек в рубли
            currency=message.successful_payment.currency,
            description='Подписка на VPN',
            created_at=datetime.utcnow(),
            status='completed'
        )
        db.add(payment)
        db.commit()
        await message.answer('Спасибо за оплату! Ваша подписка активирована.')
    except Exception as e:
        logging.error(f"Ошибка при сохранении платежа: {e}")
        await message.answer('Произошла ошибка при обработке вашего платежа. Пожалуйста, свяжитесь с поддержкой.')
    finally:
        db.close()

def register_handlers_user(router: Router):
    """Регистрация всех хендлеров для пользователя."""
    router.message.register(cmd_start, Command(commands=["start"]))
    router.message.register(cmd_help, Command(commands=["help"]))
    router.message.register(cmd_status, Command(commands=["status"]))
    router.callback_query.register(handle_get_vpn_key, lambda c: c.data == "get_vpn_key")
    router.callback_query.register(handle_get_qr_code, lambda c: c.data == "get_qr_code")
    router.callback_query.register(handle_download_config, lambda c: c.data == "download_config")
    router.callback_query.register(handle_get_instruction, lambda c: c.data == "get_instruction")
    router.callback_query.register(process_pay_command, lambda c: c.data == "pay_vpn")
