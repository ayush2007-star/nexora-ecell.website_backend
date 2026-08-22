from pydantic import BaseModel, EmailStr, Field


class SetPasswordSchema(BaseModel):
    email: EmailStr

    password: str = Field(
        ...,
        min_length=8,
        max_length=72,
    )


class LoginSchema(BaseModel):
    email: str = Field(
        ...,
        min_length=3,
        max_length=150,
    )

    password: str = Field(
        ...,
        min_length=1,
        max_length=72,
    )