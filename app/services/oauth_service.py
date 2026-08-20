"""
Handles the server-side half of "Continue with Google/Apple/Microsoft".

Flow:
1. Frontend uses the provider's JS SDK to get the user to sign in.
2. Frontend sends the resulting ID token to our backend (POST /auth/google etc).
3. We verify that token DIRECTLY WITH THE PROVIDER (never trust it blindly).
4. We find-or-create a local User row keyed on (auth_provider, provider_user_id).
5. We issue OUR OWN JWT for the user, same as the email/password flow.
"""

from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from google.oauth2 import id_token as google_id_token
from google.auth.transport import requests as google_requests

from app.core.config import settings
from app.models.user import User


def _get_or_create_oauth_user(
    db: Session, email: str, provider: str, provider_user_id: str, full_name: str | None
) -> User:
    user = db.query(User).filter(
        User.auth_provider == provider,
        User.provider_user_id == provider_user_id,
    ).first()

    if user:
        return user

    # If an account with this email exists via another method, you may want to
    # link accounts here instead of raising — decide based on your product rules.
    existing_email_user = db.query(User).filter(User.email == email).first()
    if existing_email_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"An account with this email already exists via a different sign-in method.",
        )

    user = User(
        email=email,
        hashed_password=None,
        auth_provider=provider,
        provider_user_id=provider_user_id,
        full_name=full_name,
        is_verified=True,  # provider already verified the email
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def verify_google_token(db: Session, token: str) -> User:
    try:
        payload = google_id_token.verify_oauth2_token(
            token, google_requests.Request(), settings.GOOGLE_CLIENT_ID
        )
    except ValueError:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid Google token.")

    return _get_or_create_oauth_user(
        db,
        email=payload["email"],
        provider="google",
        provider_user_id=payload["sub"],
        full_name=payload.get("name"),
    )


def verify_microsoft_token(db: Session, token: str) -> User:
    # Microsoft ID tokens are JWTs signed by Azure AD; validate against
    # Microsoft's JWKS endpoint. Using msal / python-jose + PyJWKClient in practice.
    from jose import jwt
    import requests as http_requests

    jwks_url = f"https://login.microsoftonline.com/{settings.MICROSOFT_TENANT_ID}/discovery/v2.0/keys"
    jwks = http_requests.get(jwks_url, timeout=5).json()

    try:
        header = jwt.get_unverified_header(token)
        key = next(k for k in jwks["keys"] if k["kid"] == header["kid"])
        payload = jwt.decode(
            token, key, algorithms=["RS256"], audience=settings.MICROSOFT_CLIENT_ID
        )
    except Exception:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid Microsoft token.")

    return _get_or_create_oauth_user(
        db,
        email=payload.get("email") or payload.get("preferred_username"),
        provider="microsoft",
        provider_user_id=payload["sub"],
        full_name=payload.get("name"),
    )


def verify_apple_token(db: Session, token: str) -> User:
    # Apple's identity token is a JWT signed with Apple's public keys.
    from jose import jwt
    import requests as http_requests

    jwks = http_requests.get("https://appleid.apple.com/auth/keys", timeout=5).json()

    try:
        header = jwt.get_unverified_header(token)
        key = next(k for k in jwks["keys"] if k["kid"] == header["kid"])
        payload = jwt.decode(
            token, key, algorithms=["RS256"], audience=settings.APPLE_CLIENT_ID
        )
    except Exception:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid Apple token.")

    return _get_or_create_oauth_user(
        db,
        email=payload["email"],
        provider="apple",
        provider_user_id=payload["sub"],
        full_name=None,  # Apple only sends name on the FIRST login, capture it then
    )
