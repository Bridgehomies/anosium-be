from pydantic_settings import BaseSettings, SettingsConfigDict

class Test(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    CORS_ORIGINS: list[str]

print(Test().CORS_ORIGINS)