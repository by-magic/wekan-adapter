import os

from dotenv import dotenv_values
from pydantic import BaseModel

from scripts.utils import singleton


@singleton
class Config(BaseModel):
    WEKAN_USERNAME: str
    WEKAN_PASSWORD: str
    WEKAN_ADMIN_USER: str
    WEKAN_BASE_URL: str

    MONGO_USER: str
    MONGO_PASSWORD: str
    MONGO_HOST: str
    MONGO_PORT: int
    MONGO_DB: str


config = Config(
    **dotenv_values(".env.shared"),
    **dotenv_values(".env"),
    **os.environ,
)
