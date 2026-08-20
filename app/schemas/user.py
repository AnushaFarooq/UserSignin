import uuid
from typing import Literal
from pydantic import BaseModel, EmailStr, Field, model_validator


class UserBase(BaseModel):
    email: EmailStr


class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=128)
    confirm_password: str = Field(min_length=8, max_length=128)

    # "personal" | "business" — sent by the frontend based on which
    # selection button / form the person used
    account_type: Literal["personal", "business"] = "personal"

    # Required only when account_type == "business"
    business_name: str | None = Field(default=None, max_length=200)

    @model_validator(mode="after")
    def passwords_match(self) -> "UserCreate":
        if self.password != self.confirm_password:
            raise ValueError("Password and confirm password do not match.")
        return self

    @model_validator(mode="after")
    def business_name_required_for_business(self) -> "UserCreate":
        if self.account_type == "business" and not (self.business_name or "").strip():
            raise ValueError("Business name is required for a business account.")
        return self


class UserLogin(UserBase):
    password: str


class UserOut(UserBase):
    id: uuid.UUID
    full_name: str | None = None
    auth_provider: str
    is_verified: bool
    account_type: str
    business_name: str | None = None

    class Config:
        from_attributes = True

