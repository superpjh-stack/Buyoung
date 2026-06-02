from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://buyoung:password@localhost:5432/buyoung_mes"
    DATABASE_URL_SYNC: str = "postgresql://buyoung:password@localhost:5432/buyoung_mes"

    # JWT
    JWT_SECRET_KEY: str = "change-me"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # S3
    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""
    AWS_REGION: str = "ap-northeast-2"
    S3_BUCKET: str = "buyoung-mes-files"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # AI
    OPENAI_API_KEY: str = ""
    CAD_ML_MODEL_PATH: str = "./models/cad_quote_xgboost.json"

    # App
    APP_ENV: str = "development"
    DEBUG: bool = True
    ALLOWED_ORIGINS: list[str] = ["http://localhost:3000"]


settings = Settings()
