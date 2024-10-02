from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr
from redminelib import Redmine


class Settings(BaseSettings):
    bot_token: SecretStr
    login: str
    password: SecretStr
    host: str = ''
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')


config = Settings()
redmine = Redmine(config.host, username=config.login, password=config.password.get_secret_value())