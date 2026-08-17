import uuid
from sqlalchemy import Column, String, Boolean, DateTime, func
from sqlalchemy.dialects.postgresql import UUID

from app.db.base import Base


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, index=True, nullable=False)

    # Null when the user only ever signed up via OAuth (no password to check)
    hashed_password = Column(String, nullable=True)

    # "local" | "google" | "apple" | "microsoft"
    auth_provider = Column(String, default="local", nullable=False)

    # The unique ID Google/Apple/Microsoft gives this user (their "sub" claim)
    provider_user_id = Column(String, nullable=True, index=True)

    full_name = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
