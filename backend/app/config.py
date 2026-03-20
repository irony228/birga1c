import os


def _env_bool(key: str, default: bool = False) -> bool:
    v = os.getenv(key, "")
    if not v:
        return default
    return v.lower() in ("1", "true", "yes", "on")


class Settings:
    """Читается после load_dotenv() в main."""

    yookassa_shop_id: str = os.getenv("YOOKASSA_SHOP_ID", "").strip()
    yookassa_secret_key: str = os.getenv("YOOKASSA_SECRET_KEY", "").strip()
    public_frontend_url: str = os.getenv("PUBLIC_FRONTEND_URL", "http://localhost:3000").strip().rstrip("/")
    allow_fake_topup: bool = _env_bool("ALLOW_FAKE_TOPUP", False)


settings = Settings()
