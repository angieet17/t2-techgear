from pymongo import MongoClient
from pymongo.server_api import ServerApi
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    mongodb_uri: str

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8"
    )


settings = Settings()

client = MongoClient(
    settings.mongodb_uri,
    server_api=ServerApi("1"),
    serverSelectionTimeoutMS=5000
)

db = client["techgear"]

productos_collection = db["productos"]
pedidos_collection = db["pedidos"]
