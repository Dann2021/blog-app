from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Configuration de la database
    database_url: str

    # Configuration de la sécurité jwt
    secret_key: str = "secret_key"
    access_token_expires_minutes: int = 30
    refresh_token_expires_days: int = 14
    algorithm: str = "HS256"
    

settings = Settings()  # type: ignore[call-arg]