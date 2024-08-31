# db/models.py

from sqlalchemy import Column, Integer, String, ForeignKey, Date, Boolean, Float, DateTime, Numeric
from sqlalchemy.orm import relationship
from .database import Base

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(Integer, unique=True, nullable=False)
    username = Column(String)
    full_name = Column(String)
    email = Column(String)
    phone = Column(String)
    is_admin = Column(Boolean, default=False)
    balance = Column(Float, default=0.0)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    comments = Column(String)

    vpn_clients = relationship("VpnClient", back_populates="user")
    routers = relationship("Router", back_populates="user")
    referrals = relationship("Referral", foreign_keys="[Referral.referrer_id]")
    payments = relationship("Payment", back_populates="user")  # Новая связь с платежами

class VpnClient(Base):
    __tablename__ = 'vpn_clients'
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    private_key = Column(String, nullable=False)
    public_key = Column(String, nullable=False)
    address = Column(String, nullable=False)
    dns = Column(String, nullable=False)
    allowed_ips = Column(String, nullable=False)
    endpoint = Column(String, nullable=False)
    persistent_keepalive = Column(Integer)
    config_text = Column(String)
    config_file = Column(String)
    comments = Column(String)

    user = relationship("User", back_populates="vpn_clients")

class Referral(Base):
    __tablename__ = 'referrals'
    
    referrer_id = Column(Integer, ForeignKey('users.id'), primary_key=True)
    referral_id = Column(Integer, ForeignKey('users.id'), primary_key=True)
    bonus = Column(Integer, nullable=False)
    created_at = Column(DateTime)

    referrer = relationship("User", foreign_keys=[referrer_id])
    referral = relationship("User", foreign_keys=[referral_id])

class Router(Base):
    __tablename__ = 'routers'
    
    id = Column(Integer, primary_key=True, index=True)
    serial_number = Column(String, nullable=False)
    model = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'))
    vpn_config = Column(String, nullable=False)
    admin_access = Column(String)
    sale_date = Column(Date)
    warranty_expiration = Column(Date)
    status = Column(String)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    comments = Column(String)

    user = relationship("User", back_populates="routers")

class Payment(Base):
    __tablename__ = 'payments'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))  # Связь с пользователем
    telegram_payment_charge_id = Column(String, unique=True, index=True)  # ID платежа Telegram
    provider_payment_charge_id = Column(String, unique=True, index=True)  # ID платежа ЮKassa
    amount = Column(Numeric, nullable=False)  # Сумма платежа
    currency = Column(String, nullable=False)  # Валюта платежа (например, 'RUB')
    description = Column(String)  # Описание товара или услуги
    created_at = Column(DateTime)  # Дата и время создания платежа
    status = Column(String, default='pending')  # Статус платежа (например, 'pending', 'completed', 'failed')

    user = relationship("User", back_populates="payments")  # Связь с пользователем
