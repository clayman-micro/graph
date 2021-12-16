from pydantic import BaseSettings


class Settings(BaseSettings):
    sentry_dsn: str = ""
    debug: bool = False


settings = Settings()
