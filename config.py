import os

class Config:
    SECRET_KEY = "masfo_ultra_secure_key"
    SQLALCHEMY_DATABASE_URI = "sqlite:///database.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False