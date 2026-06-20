from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):

    DATABASE_URL: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str


    TEST_DATABASE_URL: str
    TEST_POSTGRES_USER: str
    TEST_POSTGRES_PASSWORD: str
    TEST_POSTGRES_DB: str


    ACCESS_TOKEN_SECRET_KEY: str
    REFRESH_TOKEN_SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRES_MINUTES: int = 20
    REFRESH_TOKEN_EXPIRES_DAYS: int = 14


    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:5173", "http://127.0.0.1:3000"]


    DEBUG: bool = True

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()