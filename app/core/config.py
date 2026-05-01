from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "SentinelStream"
    environment: str = "dev"
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/sentinelstream"
    redis_url: str = "redis://localhost:6379/0"
    rabbitmq_url: str = "amqp://guest:guest@localhost:5672//"
    jwt_secret_key: str = "change-me"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60
    request_timeout_ms: int = 200
    ml_model_path: str = "ml/isolation_forest.joblib"
    auto_create_schema: bool = False

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
