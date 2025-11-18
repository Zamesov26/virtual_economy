from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class RadisSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", env_prefix="RADIS_", extra="ignore"
    )

    host: str = Field("localhost")
    port: int = Field(6379)
    db: int = Field(0)
    password: str | None = Field(default=None)
    decode_responses: bool = Field(True)

    @property
    def url(self) -> str:
        if self.password:
            return f"redis://:{self.password}@{self.host}:{self.port}/{self.db}"
        return f"redis://{self.host}:{self.port}/{self.db}"
