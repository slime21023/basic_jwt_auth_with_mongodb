from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix='BA_', env_file='.env', env_file_encoding='utf-8')

    MONGODB_URL: str = ""
    MONGODB_DBNAME: str = ""

settings = Settings()