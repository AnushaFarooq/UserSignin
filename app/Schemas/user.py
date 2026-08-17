import uuid
from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    email: EmailStr


class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=128)


class UserLogin(UserBase):
    password: str


class UserOut(UserBase):
    id: uuid.UUID
    full_name: str | None = None
    auth_provider: str
    is_verified: bool

    class Config:
        from_attributes = True
