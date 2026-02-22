"""
Configuration management for MindCare AI backend
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Application
    APP_NAME: str = "MindCare AI"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    # Database
    DATABASE_URL: str = "postgresql://mindcare:mindcare123@localhost:5432/mindcare_db"
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # AI Services
    ANTHROPIC_API_KEY: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None
    AI_PROVIDER: str = "anthropic"  # or "openai"
    
    # Model settings
    LLM_MODEL: str = "claude-sonnet-4-20250514"  # or "gpt-4"
    LLM_MAX_TOKENS: int = 2000
    LLM_TEMPERATURE: float = 0.3
    
    # Risk scoring thresholds
    critical_RISK_THRESHOLD: float = 80.0
    high_RISK_THRESHOLD: float = 60.0
    moderate_RISK_THRESHOLD: float = 40.0
    
    # Crisis keywords
    CRISIS_KEYWORDS: list = [
        "suicide", "suicidal", "kill myself", "end my life",
        "self-harm", "hurt myself", "cut myself",
        "no reason to live", "better off dead",
        "worthless", "hopeless"
    ]
    
    # Session settings
    SESSION_DURATION_MINUTES: int = 50
    MAX_THERAPIST_CASELOAD: int = 30
    
    # AWS (for production)
    AWS_REGION: str = "us-west-2"
    S3_BUCKET_NAME: Optional[str] = None
    
    # CORS
    CORS_ORIGINS: list = [
        "http://localhost:3000",
        "http://localhost:8000",
        "https://mindcare-ai.com"
    ]
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Singleton settings instance
settings = Settings()
