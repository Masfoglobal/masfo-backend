import os

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "masfo_ultra_secure_key")

    database_url = os.environ.get("DATABASE_URL")

    if database_url:
        # Fix postgres issue on Render
        if database_url.startswith("postgres://"):
            database_url = database_url.replace("postgres://", "postgresql://", 1)

    SQLALCHEMY_DATABASE_URI = database_url or "sqlite:///database.db"

    SQLALCHEMY_TRACK_MODIFICATIONS = False