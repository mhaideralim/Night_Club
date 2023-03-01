from datetime import datetime
from typing import Optional
from pydantic import BaseModel, constr


# Model fro database to store registration data
class User(BaseModel):
    user_id: int
    phone_number: int
    email: constr(regex=r"[^@ \t\r\n]+@[^@ \t\r\n]+\.[^@ \t\r\n]+")
    is_verified: bool = False
    otp: str
    otp_created_at: datetime = None

    password: constr(min_length=8, max_length=50,
                     regex=r"^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9])(?=.*?[#?!@$ %^&*-]).{8,}$")


class VerifyEmail(BaseModel):
    email: constr(regex=r"[^@ \t\r\n]+@[^@ \t\r\n]+\.[^@ \t\r\n]+")


class VerifyOTP(BaseModel):
    email: constr(regex=r"[^@ \t\r\n]+@[^@ \t\r\n]+\.[^@ \t\r\n]+")
    otp: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: Optional[str] = None


class VerifyForgotOTP(BaseModel):
    email: constr(regex=r"[^@ \t\r\n]+@[^@ \t\r\n]+\.[^@ \t\r\n]+")
    password: constr(min_length=8, max_length=50,
                     regex=r"^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9])(?=.*?[#?!@$ %^&*-]).{8,}$")
    otp: str


# Message schema
class Message(BaseModel):
    message: str
    phone_number: str
