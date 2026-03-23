from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str = "sqlite:///./app.db"
    influxdb_url: str = "http://localhost:8086"
    influxdb_token: str = "my-token"
    influxdb_org: str = "my-org"
    influxdb_bucket: str = "weather"

settings = Settings()
