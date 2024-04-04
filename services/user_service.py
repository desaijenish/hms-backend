from typing import Optional
from core.security import get_password_hash
from core.config import settings

from models.user import User
from schemas.auth import RegisterSchema
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from jose import jwt

PREFIX = "Bearer"


def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).all()


def create_user(db: Session, register_schema: RegisterSchema):
    password_hash = get_password_hash(register_schema.password)
    expiry_date = datetime.now() + timedelta(90)
    user = User(
        first_name=(register_schema.first_name),
        last_name=(register_schema.last_name),
        password=password_hash,
        email=(register_schema.email),
        phone=(register_schema.phone),
        gender=(register_schema.gender),
        expiry_date=expiry_date,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def get_user_by_email_active(db: Session, email: str):
    return db.query(User).filter(User.email == email).all()


def create_access_token(claim: dict, expires_delta: Optional[timedelta] = None):

    to_encode = claim.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=60)
    to_encode.update({"exp": expire})
    jwt_token = jwt.encode(to_encode, settings.SECRET_KEY, settings.ALGORITHM)
    return jwt_token


def decode_access_token(token):
    payload = None
    try:
        auth_token = get_token(token)
        print(auth_token)
        payload = jwt.decode(auth_token, settings.SECRET_KEY, settings.ALGORITHM)
    except Exception as e:
        try:
            print("Problem with token decode => ", str(e))
        finally:
            e = None
            del e

    return payload


def get_token(header):
    bearer, _, token = header.partition(" ")
    if bearer != PREFIX:
        raise ValueError("Invalid token")
    return token
