import os
from typing import List, Optional, Union
from pydantic import field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Application Info
    APP_NAME: str = "NexBank Agentic AI Customer Service"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    API_V1_PREFIX: str = "/api/v1"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = "NEXBANK_SUPER_SECRET_JWT_KEY_PROD_2026_CHANGE_ME"

    # CORS Configuration
    CORS_ORIGINS: Union[List[str], str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5500",
        "http://127.0.0.1:5500",
        "http://localhost:8080",
        "http://127.0.0.1:8080",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "null"
    ]

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v):
        if isinstance(v, str):
            if v.startswith("[") and v.endswith("]"):
                try:
                    import json
                    return json.loads(v)
                except Exception:
                    pass
            return [i.strip() for i in v.split(",") if i.strip()]
        return v

    # Database Settings
    POSTGRES_USER: str = "nexbank_user"
    POSTGRES_PASSWORD: str = "nexbank_secure_pass_2026"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "nexbank_ai_db"
    DATABASE_URL: Optional[str] = "sqlite+aiosqlite:///./nexbank_local.db"

    # Redis Cache Settings
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_URL: Optional[str] = "redis://localhost:6379/0"

    # Vector Database Settings
    CHROMA_PERSIST_DIRECTORY: str = "./chroma_data"
    CHROMA_COLLECTION_NAME: str = "nexbank_knowledge_base"

    # Security Lockout Parameters
    MAX_FAILED_LOGIN_ATTEMPTS: int = 5
    LOCKOUT_DURATION_MINUTES: int = 15

    class Config:
        env_file = ".env"
        extra = "ignore"

    def get_database_url(self) -> str:
        db_url = os.getenv("DATABASE_URL") or os.getenv("POSTGRES_URL") or self.DATABASE_URL
        if db_url and "sqlite" not in db_url and "localhost" not in db_url:
            if db_url.startswith("postgres://"):
                return db_url.replace("postgres://", "postgresql+asyncpg://", 1)
            elif db_url.startswith("postgresql://") and not db_url.startswith("postgresql+asyncpg://"):
                return db_url.replace("postgresql://", "postgresql+asyncpg://", 1)
            return db_url

        is_serverless = bool(os.getenv("VERCEL") or os.getenv("VERCEL_ENV") or os.getenv("VERCEL_REGION") or os.getenv("NOW_REGION") or os.getenv("AWS_LAMBDA_FUNCTION_NAME"))
        if is_serverless:
            return "sqlite+aiosqlite:////tmp/nexbank_local.db"
        return db_url or f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    def get_redis_url(self) -> str:
        return self.REDIS_URL or f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"


settings = Settings()
