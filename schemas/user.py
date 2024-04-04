from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    first_name: Optional[str] = None
    last_name: int = 1
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    status: int = 1


class UserCreate(UserBase):
    first_name: str
    email: EmailStr
    status: int = 1
    class Config:
        orm_mode = True

class UserDetails(UserBase):
    gender: str
    class Config:
        orm_mode = True


class UserUpdate(UserBase):
    id: int


class UserDelete(UserBase):
    id: int


class UserInDBBase(UserBase):
    id: Optional[int] = None

    class Config:
        orm_mode = True


class UserOnly(UserInDBBase):
    ...


class UserSearch(BaseModel):
    startAt: int
    pageSize: int
    sortDesc: bool

