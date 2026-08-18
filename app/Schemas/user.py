import uuid
from pydantic import BaseModel, EmailStr, Field, model_validator


class UserBase(BaseModel):
    email: EmailStr


class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=128)
    confirm_password: str = Field(min_length=8, max_length=128)

    @model_validator(mode="after")
    def passwords_match(self) -> "UserCreate":
        if self.password != self.confirm_password:
            raise ValueError("Password and confirm password do not match.")
        return self


class UserLogin(UserBase):
    password: str


class UserOut(UserBase):
    id: uuid.UUID
    full_name: str | None = None
    auth_provider: str
    is_verified: bool

    class Config:
        from_attributes = True

