# db/models.py

from sqlalchemy import Column, Integer, String, ForeignKey, Date
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
    comments = Column(String)

    vpn_clients = relationship("VpnClient", back_populates="user")
    routers = relationship("Router", back_populates="user")

class VpnClient(Base):
    __tablename__ = 'vpn_clients'
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    private_key = Column(String, nullable=False)
    public_key = Column(String, nullable=False)
    address = Column(String, nullable=False)  # IP-адрес клиента внутри VPN
    dns = Column(String, nullable=False)  # DNS-серверы, используемые клиентом
    allowed_ips = Column(String, nullable=False)  # Разрешенные IP
    endpoint = Column(String, nullable=False)  # Адрес и порт сервера WireGuard
    persistent_keepalive = Column(Integer)  # Интервал keepalive пакетов
    config_text = Column(String)  # Текст конфигурационного файла (если нужно)
    config_file = Column(String)  # Путь к файлу конфигурации на сервере
    comments = Column(String)

    user = relationship("User", back_populates="vpn_clients")

class Referral(Base):
    __tablename__ = 'referrals'
    
    referrer_id = Column(Integer, ForeignKey('users.id'), primary_key=True)
    referral_id = Column(Integer, ForeignKey('users.id'), primary_key=True)
    bonus = Column(Integer, nullable=False)

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
    comments = Column(String)

    user = relationship("User", back_populates="routers")
