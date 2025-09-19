from typing import Optional
from pathlib import Path
from pydantic import Field, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict

# Get the project root directory (3 levels up from this file)
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
ENV_FILE = PROJECT_ROOT / ".env"


class AuthSettings(BaseSettings):
    """Authentication settings"""
    model_config = SettingsConfigDict(
        env_prefix="SETTINGS__",
        env_file=str(ENV_FILE),
        case_sensitive=False,
        extra="ignore"
    )
    
    secret_key: str = Field(..., description="Secret key for JWT token generation")
    algorithm: str = Field(default="HS256", description="JWT algorithm")
    access_token_expire_minutes: int = Field(default=6000, description="Token expiration time in minutes")


class OpenAISettings(BaseSettings):
    """OpenAI API settings"""
    model_config = SettingsConfigDict(
        env_prefix="OPENAI__",
        env_file=str(ENV_FILE),
        case_sensitive=False,
        extra="ignore"
    )
    
    api_key: str = Field(..., description="OpenAI API key")
    embedding_model: str = Field(default="text-embedding-3-large", description="Embedding model name")
    model_name: str = Field(default="gpt-4o", description="GPT model name")
    temperature: float = Field(default=0.2, ge=0.0, le=2.0, description="Model temperature")
    top_p: float = Field(default=1.0, ge=0.0, le=1.0, description="Top-p sampling parameter")


class PostgresSettings(BaseSettings):
    """PostgreSQL database settings"""
    model_config = SettingsConfigDict(
        env_prefix="POSTGRES__",
        env_file=str(ENV_FILE),
        case_sensitive=False,
        extra="ignore"
    )
    
    host: str = Field(default="localhost", description="Database host")
    port: int = Field(default=5432, description="Database port")
    username: str = Field(..., description="Database username")
    password: str = Field(..., description="Database password")
    db: str = Field(..., description="Database name")
    limit: int = Field(default=100, description="Query result limit")

    @computed_field
    @property
    def database_url(self) -> str:
        """Generate database URL for SQLAlchemy"""
        return f"postgresql://{self.username}:{self.password}@{self.host}:{self.port}/{self.db}"

    @computed_field
    @property
    def async_database_url(self) -> str:
        """Generate async database URL for SQLAlchemy"""
        return f"postgresql+asyncpg://{self.username}:{self.password}@{self.host}:{self.port}/{self.db}"


class QdrantSettings(BaseSettings):
    """Qdrant vector database settings"""
    model_config = SettingsConfigDict(
        env_prefix="QDRANT__",
        env_file=str(ENV_FILE),
        case_sensitive=False,
        extra="ignore"
    )
    
    host: str = Field(default="qdrant", description="Qdrant host")
    port: int = Field(default=6333, description="Qdrant port")

    @computed_field
    @property
    def url(self) -> str:
        """Generate Qdrant URL"""
        return f"http://{self.host}:{self.port}"


class MinioSettings(BaseSettings):
    """MinIO object storage settings"""
    model_config = SettingsConfigDict(
        env_prefix="MINIO__",
        env_file=str(ENV_FILE),
        case_sensitive=False,
        extra="ignore"
    )
    
    host: str = Field(..., description="MinIO host")
    public_host: Optional[str] = Field(default=None, description="MinIO public host")
    username: str = Field(..., description="MinIO username")
    password: str = Field(..., description="MinIO password")
    ssl: bool = Field(default=False, description="Use SSL connection")
    debug: bool = Field(default=False, description="Enable debug mode")

    @computed_field
    @property
    def endpoint(self) -> str:
        """Generate MinIO endpoint"""
        protocol = "https" if self.ssl else "http"
        return f"{protocol}://{self.host}"


class RedisSettings(BaseSettings):
    """Redis cache settings"""
    model_config = SettingsConfigDict(
        env_prefix="REDIS__",
        env_file=str(ENV_FILE),
        case_sensitive=False,
        extra="ignore"
    )
    
    host: str = Field(default="localhost", description="Redis host")
    port: int = Field(default=6379, description="Redis port")
    db: int = Field(default=0, description="Redis database number")

    @computed_field
    @property
    def url(self) -> str:
        """Generate Redis URL"""
        return f"redis://{self.host}:{self.port}/{self.db}"


class LangsmithSettings(BaseSettings):
    """LangSmith tracing settings"""
    model_config = SettingsConfigDict(
        env_prefix="LANGSMITH__",
        env_file=str(ENV_FILE),
        case_sensitive=False,
        extra="ignore"
    )
    
    tracing: str = Field(default="true", description="Enable tracing")
    endpoint: str = Field(default="https://api.smith.langchain.com", description="LangSmith endpoint")
    api_key: str = Field(..., description="LangSmith API key")
    project: str = Field(..., description="LangSmith project name")

    @computed_field
    @property
    def is_enabled(self) -> bool:
        """Check if tracing is enabled"""
        return self.tracing.lower() in ("true", "1", "yes", "on")


class Settings(BaseSettings):
    """Main settings class that combines all configuration sections"""
    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    # App settings (direct field for BASE_URL)
    base_url: str = Field(..., description="Application base URL")
    
    # Nested settings (initialized after main settings)
    auth: Optional[AuthSettings] = None
    openai: Optional[OpenAISettings] = None
    postgres: Optional[PostgresSettings] = None
    qdrant: Optional[QdrantSettings] = None
    minio: Optional[MinioSettings] = None
    redis: Optional[RedisSettings] = None
    langsmith: Optional[LangsmithSettings] = None
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Initialize nested settings after main settings
        self.auth = AuthSettings()
        self.openai = OpenAISettings()
        self.postgres = PostgresSettings()
        self.qdrant = QdrantSettings()
        self.minio = MinioSettings()
        self.redis = RedisSettings()
        self.langsmith = LangsmithSettings()


# Global settings instance
settings = Settings()

if __name__ == "__main__":
    import pprint
    pprint.pprint(settings.model_dump())