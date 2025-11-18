from pydantic import Field
from pydantic_settings import BaseSettings

from app.api.settings import APISettings
from app.database.settings import DBSettings
from app.redis.settings import RadisSettings


class Settings(BaseSettings):
    api: APISettings = Field(default_factory=APISettings)
    db: DBSettings = Field(default_factory=DBSettings)
    redis: RadisSettings = Field(default_factory=RadisSettings)
