from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

class Settings(BaseSettings):
    APP_NAME: str = "WasteTrack"
    APP_ENV: str = "development"
    APP_DEBUG: bool = False

    DATABASE_URL: str
    DATABASE_URL_SYNC: str

    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    TERMINAL_API_KEY: str = "424b6b4c-7470-47d0-9077-739ea8e19626"

    # Смещение часового пояса ресторана от UTC (Москва = 3).
    # Терминал сохраняет время списаний «по настенным часам» ресторана,
    # поэтому все расчёты периодов на сервере ведутся в том же времени.
    APP_TZ_OFFSET_HOURS: int = 3

    LOG_FILE: Path = Path(__file__).parent / "../logs/log.log"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
