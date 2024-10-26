from pydantic import BaseModel
from uuid import UUID
from typing import Optional
from fastapi import UploadFile


class UserCreate(BaseModel):
    username: str
    email: str
    hashed_password: str


class User(UserCreate):
    id: UUID


class UserLogin(BaseModel):
    username: str
    hashed_password: str


class OtpRequest(BaseModel):
    otp: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str


class UserDetailsCreate(BaseModel):
    first_name: str
    last_name: str
    phone_number: str
    date_of_birth: str
    gender: str
    annual_income: Optional[str] = None


class UserAddressCreate(BaseModel):
    address: str
    city: str
    state: str
    country: str
    postal_code: str


class UserIncome(BaseModel):
    Annual_Income: str


class UserDocumentCreate(User):
    photo: str
    license: str


class UserCardDetails(BaseModel):
    spending_limit: str
    expiry_date: str
    cvv: str
    card_holder_name: str
    date_issued: str
    card_number: str
