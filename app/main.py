from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.db.base import Base, engine
from app.Models import user  # noqa: F401  (import ensures table is registered)
from app.api.v1 import auth, oauth

# Creates tables if they don't exist. In real production, use Alembic migrations
# instead of this line.
Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.APP_NAME)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # lock this down to your frontend's domain in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/v1")
app.include_router(oauth.router, prefix="/api/v1")


@app.get("/health")
def health_check():
    return {"status": "ok"}