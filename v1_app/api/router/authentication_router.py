from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from fastapi import APIRouter
from typing import Optional
from datetime import datetime, timedelta
import string
from bson.objectid import ObjectId
from passlib.hash import bcrypt
from jose import jwt
from v1_app.api.database.db_connection import get_database
from v1_app.api.database.db_utils import SECRET_KEY, ALGORITHM, smtp_server, sender_email, port, sender_password
from v1_app.api.model.authentication_model import User, VerifyEmail, VerifyOTP, VerifyForgotOTP
from fastapi.param_functions import Depends
import smtplib
import random
from fastapi import Request
from fastapi.templating import Jinja2Templates

import os

router = APIRouter()

templates = Jinja2Templates(directory="v1_app/api/templete")


# Function to generate 6-Digit OPT
async def generate_otp():
    """
    :return:
    """
    return ''.join(random.choices(string.digits, k=6))


# Function to generate Access Token with expiry limit
async def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """

    :param data:
    :param expires_delta:
    :return:
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# API to register a user in database
@router.post('/register')
async def register(user: User, db=Depends(get_database)):
    """
    :param user:
    :param db:
    :return:
    """
    try:
        # Query to check if email already exists in database
        existing_user = await db.users.find_one({'email': user.email})
        if existing_user:
            response = {
                "code": 0,
                "message": "Email Already Registered!",
                "data": {
                    "validate_errors": [
                        {
                            "message": "Login by This Email or Register by a new Email"
                        }
                    ]
                }
            }
            return response
        # Code to encrypt password
        user.password = bcrypt.hash(user.password)
        # Query to insert data into the database
        await db.users.insert_one(user.dict())
        response = {
            "code": 1,
            "message": "Registration Successfull!",
            "data": {
                "user": user
            }
        }
        return response
    except Exception as e:
        response = {
            "code": 500,
            "message": "Internal Server Error",
            "data": {
                "error": str(e)
            }
        }
        return response


# API for User Login
@router.post('/login')
async def login(email: str, password: str, db=Depends(get_database)):
    """
    :param email:
    :param password:
    :param db:
    :return:
    """
    try:
        # Query to find the user from database
        user = await db.users.find_one({'email': email})
        # Code to decrypt password and check credentials as they exist in database
        if not user or not bcrypt.verify(password, user['password']):
            response = {
                "code": 0,
                "message": "Invalid Email or Password!",
                "data": {
                    "validate error": [
                        {
                            "message": "Email is Incorrect!"
                        },
                        {
                            "message": "Password in Incorrect!"
                        }
                    ]
                }
            }
            return response
        if not user['is_verified']:
            response = {
                "code": 0,
                "message": "Email not verified!",
                "data": {
                    "validate_error": [
                        {
                            "message": "Verify your email to Login!"
                        }
                    ]
                }
            }
            return response
        # Function called here to generate and return access token
        access_token = await create_access_token(data={"sub": email})
        response = {
            "code": 1,
            "message": "Access Token generated",
            "data":
                {
                    "access_token": access_token,
                    "token_type": "bearer"
                }
        }
        return response
    except Exception as e:
        response = {
            "code": 500,
            "message": "Internal Server Error",
            "data": {
                "error": str(e)
            }
        }
        return response


# API to verify user Email.
@router.post('/verify_email')
async def verify_email(data: VerifyEmail, db=Depends(get_database)):
    """
    :param data:
    :param db:
    :return:
    """
    try:
        # Query to find Email from the database
        user = await db.users.find_one({'email': data.email})
        # Code to check that email is valid or not
        if not user:
            response = {
                "code": 0,
                "message": "Invalid Email!",
                "data": {
                    "validate_error": [
                        {
                            "message": "Email is not Correct"
                        }
                    ]
                }
            }
            return response
        # Code to check whether email is verified or not
        if user['is_verified']:
            response = {
                "code": 1,
                "message": "Email Already verified!",
                "data": {
                    "email": data
                }
            }
            return response
        # Function called here to generate OPT and to send it in the database if user email is correct
        otp = await generate_otp()
        user['otp'] = otp
        user['otp_created_at'] = datetime.now()
        # Query to update otp in database
        users = await db.users.update_one({'_id': ObjectId(user['_id'])},
                                  {'$set': {'otp': otp, 'otp_created_at': user['otp_created_at']}})
        # Send email with OTP to the user
        response = {
            "code": 1,
            "message": "OTP Sent!",
            "data": {

                "data": users
            }
        }
        return response
    except Exception as e:
        response = {
            "code": 500,
            "message": "Internal Server Error",
            "data": {
                "error": str(e)
            }
        }
        return response


@router.post("/send_email")
async def send_mail(email: str, request: Request, db=Depends(get_database)):
    """
    :param email:
    :param request:
    :param db:
    :return:
    """
    try:
        # Retrieve the user's email address
        user = await db.users.find_one({"email": email})
        if not user:
            response = {
                "code": 0,
                "message": "User Not Found!",
                "data": {
                    "validate_error": [
                        {
                            "message": "Email not Found"
                        }
                    ]
                }
            }
            return response
        receiver_email = user["email"]

        subject = 'Your OTP'
        otp = random.randint(100000, 999999)
        context = {"request": Request, "otp": otp}
        body = templates.TemplateResponse("email_verification_temp.html", context).body.decode("utf-8")

        # Create the email message
        message = MIMEMultipart()
        message['From'] = sender_email
        message['To'] = receiver_email
        message['Subject'] = subject
        message.attach(MIMEText(body, 'html'))

        # Connect to the SMTP server and send the email
        with smtplib.SMTP(smtp_server, port) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, receiver_email, message.as_string())
        users = await db.users.update_one({'_id': ObjectId(user['_id'])},
                                  {'$set': {'otp': otp, 'otp_created_at': datetime.now()}})

        response = {
            "code": 1,
            "message": "Email with OTP Sent Successfully!",
            "data": {
                "email": email,
                "otp": otp,
                "data": users
            }
        }
        return response

    except Exception as e:
        response = {
            "code": 500,
            "message": "Internal Server Error",
            "data": {
                "error": str(e)
            }
        }
        return response


# API to verify OTP from database and generate token
@router.post('/verify_otp')
async def verify_otp(data: VerifyOTP, db=Depends(get_database)):
    """
    :param data:
    :param db:
    :return:
    """
    try:
        # Query to find email from the database
        user = await db.users.find_one({"email": data.email})
        if not user:
            response = {
                "code": 0,
                "message": "Invalid Email!",
                "data": {
                    "validate_error": [
                        {
                            "message": "Email Not Correct"
                        }
                    ]
                }
            }
            return response
        # Code to check whether OTP created or not
        if not user["email"] or not user["otp_created_at"]:
            response = {
                "code": 0,
                "message": "OTP Not Generated!",
                "data": {
                    "validate_error": [
                        {
                            "message": "Due to invalid Email OTP is not generated"
                        }
                    ]
                }
            }
            return response
        # Code to set OTP expiration time
        otp_expiry_time = user["otp_created_at"] + timedelta(minutes=5)
        if datetime.now() > otp_expiry_time:
            response = {
                "code": 0,
                "message": "OTP Expired!",
                "data": {
                    "validate_error": [
                        {
                            "message": "You are late OTP time is passed"
                        }
                    ]

                }
            }
            return response
        # Code to check whether otp is correct or not
        a = int(data.otp)
        print(type(a), type(user["otp"]))
        if a != user["otp"]:
            response = {
                "code": 0,
                "message": "Invalid OTP!",
                "data": {
                    "validate_error": [
                        {
                            "message": "OTP is fake or Incorrect!"
                        }
                    ]
                }
            }
            return response
        # Function called here to check if otp is correct then generate the access token
        access_token = await create_access_token(data={"sub": data.email})
        # Code to update the status of verified from false to true
        udata = await db.users.update_one({'_id': ObjectId(user['_id'])}, {'$set': {'is_verified': True}})
        response = {
            "code": 1,
            "message": "token_type: bearer",
            "data": {
                "token_type": "bearer",
                "access_token": access_token,
                "data": udata
                }
        }
        return response
    except Exception as e:
        response = {
            "code": 500,
            "message": "Internal Server Error",
            "data": {
                "error": str(e)
            }
        }
        return response


@router.post("/send_forgot_email")
async def send_forgot_mail(email: str, request: Request, db=Depends(get_database)):
    """
    :param email:
    :param request:
    :param db:
    :return:
    """
    try:
        # Retrieve the user's email address
        user = await db.users.find_one({"email": email})
        if not user:
            response = {
                "code": 0,
                "message": "Email Does not Exists!",
                "data": {
                    "validate_error": [
                        {
                            "message": "Invalid or Incorrect Email!"
                        }
                    ]
                }
            }
            return response
        receiver_email = user["email"]

        subject = 'Your OTP'
        otp = random.randint(100000, 999999)
        context = {"request": Request, "otp": otp}
        body = templates.TemplateResponse("email_verification_forgot_temp.html", context).body.decode("utf-8")

        # Create the email message
        message = MIMEMultipart()
        message['From'] = sender_email
        message['To'] = receiver_email
        message['Subject'] = subject
        message.attach(MIMEText(body, 'html'))

        # Connect to the SMTP server and send the email
        with smtplib.SMTP(smtp_server, port) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, receiver_email, message.as_string())
        udata = await db.users.update_one({'_id': ObjectId(user['_id'])},
                                  {'$set': {'otp': otp, 'otp_created_at': datetime.now()}})

        response = {
            "code": 1,
            "message": "Email with OTP Sent Successfully",
            "data": {
                "email": email,
                "otp": otp,
                "data": udata
            }
        }
        return response
    except Exception as e:
        response = {
            "code": 500,
            "message": "Internal Server Error",
            "data": {
                "error": str(e)
            }
        }
        return response


@router.post('/verify_forgot_otp')
async def verify__forgot_otp(data: VerifyForgotOTP, db=Depends(get_database)):
    """
    :param data:
    :param db:
    :return:
    """
    try:
        user = await db.users.find_one({"otp": data.otp})
        # Code to check whether OTP created or not
        if not user["otp_created_at"]:
            response = {
                "code": 0,
                "message": "OTP Not Generated!",
                "data": {
                    "validate_error": [
                        {
                            "message": "OTP creation time is valid or not "
                        }
                    ]
                }
            }
            return response
        # Code to set OTP expiration time
        otp_expiry_time = user["otp_created_at"] + timedelta(minutes=5)
        if datetime.now() > otp_expiry_time:
            response = {
                "code": 0,
                "message": "OTP Expired!",
                "data": {
                    "validate_error": [
                        {
                            "message": "You are late or OTP time is passed"
                        }
                    ]
                }
            }
            return response
        # Code to check whether otp is correct or not
        a = int(data.otp)
        print(type(a), type(user["otp"]))
        if a != user["otp"]:
            response = {
                "code": 0,
                "message": "invalid OTP!",
                "data": {
                    "validate_error": [
                        {
                            "message": "Incorrect or Fake OTP"
                        }
                    ]
                }
            }
            return response
        # Function called here to check if otp is correct then generate the access token
        else:
            await db.users.update_one({"password": data.password})
            response = {
                "code": 1,
                "message": "Password Updated Successfully!",
                "data": {
                    "data": data
                }
            }
            return response
        # Code to update the status of verified from false to true
    except Exception as e:
        response = {
            "code": 500,
            "message": "Internal Server Error",
            "data": {
                "error": str(e)
            }
        }
        return response
