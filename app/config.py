import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # MongoDB
    MONGODB_URL: str = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
    DATABASE_NAME: str = os.getenv("DATABASE_NAME", "event_management")
    
    # JWT
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-this-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    
    # Email
    SMTP_SERVER: str = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", 587))
    EMAIL_FROM: str = os.getenv("EMAIL_FROM", "your-email@gmail.com")
    EMAIL_PASSWORD: str = os.getenv("EMAIL_PASSWORD", "your-app-password")
    
    # App
    APP_NAME: str = "Event Management System"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = os.getenv("DEBUG", "True") == "True"
    
    # File paths
    QR_CODE_DIR: str = os.path.join(os.path.dirname(__file__), "static", "qrcodes")

settings = Settings()
