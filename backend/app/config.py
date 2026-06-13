import os


class Settings:
    DATABASE_URL: str = os.environ.get("DATABASE_URL", "")
    CORS_ALLOWED_ORIGINS: str = os.environ.get("CORS_ALLOWED_ORIGINS", "*")
    TELEGRAM_BOT_TOKEN: str = os.environ.get("TELEGRAM_DB_BOT_TOKEN") or os.environ.get("TELEGRAM_BOT_TOKEN", "")
    TELEGRAM_CHAT_ID: str = os.environ.get("TELEGRAM_DB_CHAT_ID") or os.environ.get("TELEGRAM_CHAT_ID", "")
    DELIVERY_UPLOAD_DIR: str = os.environ.get("DELIVERY_UPLOAD_DIR", "")
    MAX_DELIVERY_PHOTO_MB: int = int(os.environ.get("MAX_DELIVERY_PHOTO_MB", "8"))


settings = Settings()
