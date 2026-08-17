from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class OAuthLoginRequest(BaseModel):
    # The frontend sends the ID token/authorization code it got from the
    # provider's SDK (Google Sign-In button, Apple JS, MSAL, etc.)
    token: str