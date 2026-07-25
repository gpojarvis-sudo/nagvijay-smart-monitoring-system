"""
NagVijay Smart Monitoring System - Configuration
Production-ready settings with validation
"""
from __future__ import annotations

import os
from functools import lru_cache
from typing import List, Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings - validated via Pydantic v2"""
    
    model_config = SettingsConfigDict(
        env_file=(".env","/etc/secrets/.env"),
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )
    
    # Core App
    APP_NAME: str = Field(default="NagVijay Smart Monitoring System")
    APP_ENV: str = Field(default="development")  # development, staging, production
    APP_VERSION: str = Field(default="1.0.0-MVP")
    API_V1_PREFIX: str = Field(default="/api/v1")
    DEBUG: bool = Field(default=False)
    HOST: str = Field(default="0.0.0.0")
    BACKEND_PORT: int = Field(default=8000)
    FRONTEND_PORT: int = Field(default=5173)
    FRONTEND_URL: str = Field(default="http://localhost:5173")
    BACKEND_URL: str = Field(default="http://localhost:8000")
    CORS_ORIGINS: str = Field(default="http://localhost:5173,http://localhost:3000")
    
    # Database / Supabase
    DATABASE_URL: str = Field(default="postgresql+asyncpg://postgres:postgres@localhost:5432/nagvijay_db")
    SUPABASE_URL: str = Field(default="")
    SUPABASE_ANON_KEY: str = Field(default="")
    SUPABASE_SERVICE_ROLE_KEY: str = Field(default="")
    SUPABASE_JWT_SECRET: str = Field(default="")
    
    # Security / JWT
    JWT_SECRET_KEY: str = Field(default="change-me-32-char-minimum-secret-key!")
    JWT_ALGORITHM: str = Field(default="HS256")
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=15)
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = Field(default=7)
    JWT_ISSUER: str = Field(default="nagvijay-nsms")
    BCRYPT_ROUNDS: int = Field(default=12)
    
    # Google OAuth
    GOOGLE_CLIENT_ID: str = Field(default="")
    GOOGLE_CLIENT_SECRET: str = Field(default="")
    GOOGLE_REDIRECT_URI: str = Field(default="http://localhost:8000/api/v1/auth/google/callback")
    GOOGLE_OAUTH_SCOPES: str = Field(default="openid email profile")
    
    # Google APIs
    GOOGLE_SHEETS_API_ENABLED: bool = Field(default=True)
    GOOGLE_FORMS_API_ENABLED: bool = Field(default=True)
    GOOGLE_SHEETS_CREDENTIALS_JSON: str = Field(default="")
    GOOGLE_FORMS_WEBHOOK_SECRET: str = Field(default="")
    
    # AI / Gemini
    GEMINI_API_KEY: str = Field(default="")
    GEMINI_MODEL: str = Field(default="gemini-1.5-flash")
    GEMINI_TEMPERATURE: float = Field(default=0.2)
    GEMINI_MAX_TOKENS: int = Field(default=2048)

    # AI Provider
    AI_PROVIDER: str = Field(default="cloudflare")

    # Cloudflare Workers AI
    CLOUDFLARE_ACCOUNT_ID: str = Field(default="")
    CLOUDFLARE_API_TOKEN: str = Field(default="")
    CLOUDFLARE_MODEL: str = Field(default="@cf/openai/gpt-oss-120b")
    AI_FALLBACK_MODEL: str = Field(default="@cf/deepseek-ai/deepseek-r1-distill-qwen-32b")

    # Generic AI Settings
    AI_TEMPERATURE: float = Field(default=0.2)
    AI_MAX_TOKENS: int = Field(default=2048)
    
    # Automation / n8n
    N8N_WEBHOOK_URL: str = Field(default="")
    N8N_API_KEY: str = Field(default="")
    N8N_ENABLED: bool = Field(default=False)
    
    # Email
    SMTP_HOST: str = Field(default="")
    SMTP_PORT: int = Field(default=587)
    SMTP_USER: str = Field(default="")
    SMTP_PASSWORD: str = Field(default="")
    SMTP_FROM: str = Field(default="noreply@nagvijay.india-post")
    
    # Logging & Monitoring
    LOG_LEVEL: str = Field(default="INFO")
    SENTRY_DSN: str = Field(default="")
    ENABLE_AUDIT_LOGS: bool = Field(default=True)
    
    # Railway / Deployment
    RAILWAY_ENVIRONMENT: str = Field(default="")
    RAILWAY_PROJECT_ID: str = Field(default="")
    PORT: int = Field(default=8000)
    
    # Redis / Celery
    REDIS_URL: str = Field(default="redis://localhost:6379/0")
    CELERY_BROKER_URL: str = Field(default="")
    
    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = Field(default=True)
    RATE_LIMIT_REQUESTS_PER_MINUTE: int = Field(default=60)
    
    # Feature Flags
    ENABLE_GOOGLE_FORMS_SYNC: bool = Field(default=True)
    ENABLE_GOOGLE_SHEETS_SYNC: bool = Field(default=True)
    ENABLE_AI_CHATBOT: bool = Field(default=True)
    ENABLE_NOTIFICATIONS: bool = Field(default=True)
    ENABLE_SCHEDULER: bool = Field(default=True)
    
    @field_validator("JWT_SECRET_KEY")
    @classmethod
    def validate_jwt_secret(cls, v: str) -> str:
        if len(v) < 16:
            # Allow short in dev, but warn
            if os.getenv("APP_ENV") == "production":
                raise ValueError("JWT_SECRET_KEY must be at least 32 characters in production")
        return v
    
    @field_validator("CORS_ORIGINS")
    @classmethod
    def validate_cors(cls, v: str) -> str:
        return v
    
    @property
    def is_production(self) -> bool:
        return self.APP_ENV.lower() == "production"
    
    @property
    def cors_origins_list(self) -> List[str]:
        if not self.CORS_ORIGINS:
            return ["*"] if self.DEBUG else []
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]
    
    @property
    def celery_broker(self) -> str:
        return self.CELERY_BROKER_URL or self.REDIS_URL
    
    def get_database_url_sync(self) -> str:
        """Get sync database URL for Alembic"""
        return self.DATABASE_URL.replace("+asyncpg", "").replace("postgresql+asyncpg", "postgresql")


@lru_cache()
def get_settings() -> Settings:
    return Settings()
