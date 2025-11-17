from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class APISettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_prefix="API_", env_file_encoding="utf-8", extra="ignore"
    )

    name: str = Field("Application name API")
    debug: bool = Field(False)
    version: str = Field("0.1.0")
