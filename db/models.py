from sqlalchemy import Column, Integer, String, ForeignKey, Date, Boolean, Float, DateTime, Numeric
from sqlalchemy.orm import relationship
from .database import Base


from datetime import datetime


class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(Integer, unique=True, nullable=False)  # Integer, не VARCHAR
    username = Column(String(150))  # Указываем длину для String
    full_name = Column(String(255))  # Указываем длину для String
    email = Column(String(255))  # Указываем длину для String
    phone = Column(String(20))  # Указываем длину для String
    is_admin = Column(Boolean, default=False)
    balance = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    comments = Column(String(255))  # Указываем длину для String

    vpn_clients = relationship("VpnClient", back_populates="user")
    routers = relationship("Router", back_populates="user")
    referrals = relationship("Referral", foreign_keys="[Referral.referrer_id]", back_populates="referrer", overlaps="referrer,referral")
    referred_by = relationship("Referral", foreign_keys="[Referral.referral_id]", back_populates="referral", overlaps="referrer,referral")
    payments = relationship("Payment", back_populates="user")  # Связь с платежами

class VpnClient(Base):
    __tablename__ = 'vpn_clients'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    private_key = Column(String(255), nullable=False)
    public_key = Column(String(255), nullable=False)
    address = Column(String(255), nullable=False)
    dns = Column(String(255), nullable=False)
    allowed_ips = Column(String(255), nullable=False)
    endpoint = Column(String(255), nullable=False)
    persistent_keepalive = Column(Integer)
    config_file_id = Column(String(255), nullable=True)  # ID конфигурации в MongoDB
    comments = Column(String(255))

    user = relationship("User", back_populates="vpn_clients")

class Referral(Base):
    __tablename__ = 'referrals'
    
    referrer_id = Column(Integer, ForeignKey('users.id'), primary_key=True)
    referral_id = Column(Integer, ForeignKey('users.id'), primary_key=True)
    bonus = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    referrer = relationship("User", foreign_keys=[referrer_id], back_populates="referrals", overlaps="referrer,referral")
    referral = relationship("User", foreign_keys=[referral_id], back_populates="referred_by", overlaps="referrer,referral")

class Router(Base):
    __tablename__ = 'routers'
    
    id = Column(Integer, primary_key=True, index=True)
    serial_number = Column(String(100), nullable=False, unique=True)
    model = Column(String(100), nullable=False)
    mac_address = Column(String(50), nullable=False, unique=True)
    sku = Column(String(50), nullable=False, index=True)
    barcode = Column(String(100), nullable=True, unique=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    vpn_config = Column(String(255), nullable=True)
    admin_access = Column(String(255))
    sale_date = Column(Date)
    warranty_expiration = Column(Date)
    status = Column(String(50), default="available")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    comments = Column(String(255))
    subdomain = Column(String(255), nullable=True, unique=True)
    dns_record_id = Column(String(255), nullable=True)
    is_for_sale = Column(Boolean, default=False)
    auth_token = Column(String(255), nullable=False, unique=True)  # Добавляем поле для токена
    user = relationship("User", back_populates="routers")

class Payment(Base):
    __tablename__ = 'payments'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    telegram_payment_charge_id = Column(String(255), unique=True, index=True)
    provider_payment_charge_id = Column(String(255), unique=True, index=True)
    amount = Column(Numeric(10, 2), nullable=False)
    currency = Column(String(10), nullable=False, default='RUB')
    description = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    status = Column(String(50), default='pending')

    user = relationship("User", back_populates="payments")
