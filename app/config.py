from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str
    neo4j_uri: str
    neo4j_user: str
    neo4j_password: str
    redis_url: str
    openrouter_api_key: str

    class Config:
        env_file = ".env"

settings = Settings()