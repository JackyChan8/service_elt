from pydantic import SecretStr
from pydantic_settings import BaseSettings


class AppSettings(BaseSettings):
    """
        Settings Class
    """

    # Application
    IS_TEST: bool = True
    APP_NAME: str
    APP_VERSION: str
    APP_SUMMARY: str
    APP_DESCRIPTION: str

    # Elt
    ELT_URL: str
    ELT_USERNAME: str
    ELT_PASSWORD: SecretStr

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'


settings = AppSettings()
