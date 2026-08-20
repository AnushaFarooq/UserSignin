from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.auth import Token, OAuthLoginRequest
from app.services import oauth_service, auth_service

router = APIRouter(prefix="/auth", tags=["oauth"])


@router.post("/google", response_model=Token)
def google_login(payload: OAuthLoginRequest, db: Session = Depends(get_db)):
    user = oauth_service.verify_google_token(db, payload.token)
    token = auth_service.issue_token_for_user(user)
    return Token(access_token=token)


@router.post("/apple", response_model=Token)
def apple_login(payload: OAuthLoginRequest, db: Session = Depends(get_db)):
    user = oauth_service.verify_apple_token(db, payload.token)
    token = auth_service.issue_token_for_user(user)
    return Token(access_token=token)


@router.post("/microsoft", response_model=Token)
def microsoft_login(payload: OAuthLoginRequest, db: Session = Depends(get_db)):
    user = oauth_service.verify_microsoft_token(db, payload.token)
    token = auth_service.issue_token_for_user(user)
    return Token(access_token=token)
