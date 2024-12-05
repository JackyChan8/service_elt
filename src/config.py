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

    # Postgres
    POSTGRES_HOST: str
    POSTGRES_PORT: int
    POSTGRES_USER: str
    POSTGRES_NAME: str
    POSTGRES_PASS: SecretStr

    # Elt
    ELT_URL: str
    ELT_USERNAME: str
    ELT_PASSWORD: SecretStr

    # Ресо Гарантия
    RESO_GUARANTEE: str
    RESO_GUARANTEE_USERNAME: str
    RESO_GUARANTEE_PASSWORD: SecretStr

    def build_postgres_url(self, protocol_db: str = 'postgresql+asyncpg') -> str:
        """
            Build Postgres URL
            :param protocol_db protocol database
            :return: str
        """
        return (f"{protocol_db}://"
                f"{self.POSTGRES_USER}:{self.POSTGRES_PASS.get_secret_value()}@"
                f"{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_NAME}")

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'


settings = AppSettings()
