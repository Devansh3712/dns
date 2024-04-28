from pydantic_settings import BaseSettings, SettingsConfigDict


class EnvironmentVariables(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    REDIS_HOST: str
    REDIS_PORT: int
    DNS_HOST: str
    DNS_PORT: int


env = EnvironmentVariables()
