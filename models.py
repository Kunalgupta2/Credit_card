from sqlalchemy import Column, Integer, String, Boolean, UUID
from pydantic import BaseModel
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import ForeignKey


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)


class UserDetails(Base):
    __tablename__ = "user_details"
    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String)
    last_name = Column(String)
    phone_number = Column(String)
    date_of_birth = Column(String)
    gender = Column(String)
    annual_income = Column(String, nullable=True)


class UserAddress(Base):
    __tablename__ = "user_address"
    id = Column(Integer, primary_key=True, index=True)
    address = Column(String)
    city = Column(String)
    state = Column(String)
    country = Column(String)
    postal_code = Column(String)


class UserVerification(Base):
    __tablename__ = "user_verifications"

    id = Column(Integer, primary_key=True, index=True)
    photo = Column(String)
    license = Column(String)


class UsercardDetails(Base):
    __tablename__ = "user_card_details"
    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(String)
    created_at = Column(String)
    expiry_date = Column(String)
    spending_limit = Column(String)
    cvv = Column(String)
    card_holder_name = Column(String)
    date_issued = Column(String)
    card_number = Column(String)
