import os

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "masfo_ultra_secure_key")

    db_url = os.environ.get("DATABASE_URL")

    if db_url:
        db_url = db_url.replace("postgres://", "postgresql://")

    SQLALCHEMY_DATABASE_URI = db_url or "sqlite:///database.db"

    SQLALCHEMY_TRACK_MODIFICATIONS = False