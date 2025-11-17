from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class DBSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", env_prefix="DB_", extra="ignore"
    )

    host: str = Field("localhost")
    port: int = Field(5432)
    user: str = Field("postgres")
    password: str = Field("postgres")
    driver: str = Field("asyncpg")
    name: str

    @property
    def url(self) -> str:
        """Формирует строку подключения к PostgreSQL."""
        return f"postgresql+{self.driver}://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"
