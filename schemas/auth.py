from pydantic import BaseModel

class LoginSchema(BaseModel):
    email: str
    password: str


class RegisterSchema(LoginSchema):
    first_name: str
    last_name: str
    phone: str
    gender: str

    class Config:
        orm_mode = True
