from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    APP_NAME: str = "FireFighterDataHub"
    API_V1_PREFIX: str = "/api/v1"

    DATABASE_URL: str

    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440 * 7

    CORS_ORIGINS: str = "*"

    # SES / email settings
    SES_REGION: str = "us-east-1"
    SES_FROM_NAME: str = "Firefighter-DataHub-Team"
    SES_FROM_EMAIL: str

    # Used for email verification tokens
    EMAIL_TOKEN_SECRET: str

    # Current POC uses manual token entry in Flutter app.
    # Later you can switch to frontend link mode after public web frontend/domain exists.
    EMAIL_VERIFICATION_MODE: str = "manual"

    # Optional for later web verification links
    FRONTEND_VERIFY_BASE_URL: str | None = None


settings = Settings()