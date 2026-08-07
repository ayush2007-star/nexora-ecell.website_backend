from pydantic import BaseModel, EmailStr, Field


class SetPasswordSchema(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=32)


class LoginSchema(BaseModel):
    email: EmailStr
    password: str