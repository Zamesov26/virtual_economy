from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class CelerySettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="CELERY_",
        extra="ignore",
    )

    broker_host: str = Field("localhost")
    broker_port: int = Field(6379)
    broker_db: int = Field(0)

    backend_host: str = Field("localhost")
    backend_port: int = Field(6379)
    backend_db: int = Field(1)

    password: str | None = Field(default=None)

    timezone: str = Field("UTC")
    enable_utc: bool = Field(True)

    @property
    def broker_url(self) -> str:
        if self.password:
            return f"redis://:{self.password}@{self.broker_host}:{self.broker_port}/{self.broker_db}"
        return f"redis://{self.broker_host}:{self.broker_port}/{self.broker_db}"

    @property
    def backend_url(self) -> str:
        if self.password:
            return f"redis://:{self.password}@{self.backend_host}:{self.backend_port}/{self.backend_db}"
        return f"redis://{self.backend_host}:{self.backend_port}/{self.backend_db}"
