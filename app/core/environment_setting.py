from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "FastAPI Example API"
    tz: str = "Asia/Ho_Chi_Minh"
    
    # Database Settings
    db_username: str
    db_password: str
    db_host: str
    db_port: int
    db_name: str
    
    # JWT Settings
    jwt_access_secret: str
    jwt_access_expiration: int
    jwt_refresh_secret: str
    jwt_refresh_expiration: int
    jwt_algorithm: str

    model_config = SettingsConfigDict(env_file=".env")
