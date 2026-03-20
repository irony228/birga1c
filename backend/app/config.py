import os


class Settings:
    """Читается после load_dotenv() в main."""

    yookassa_shop_id: str = os.getenv("YOOKASSA_SHOP_ID", "").strip()
    yookassa_secret_key: str = os.getenv("YOOKASSA_SECRET_KEY", "").strip()
    public_frontend_url: str = os.getenv("PUBLIC_FRONTEND_URL", "http://localhost:3000").strip().rstrip("/")


settings = Settings()
