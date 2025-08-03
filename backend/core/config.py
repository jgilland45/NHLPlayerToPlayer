from pydantic_settings import BaseSettings, SettingsConfigDict
import os

class Settings(BaseSettings):
    """
    Defines the application's configuration settings.

    pydantic-settings will automatically attempt to load these values
    from a .env file or from system environment variables.
    """

    # Database configuration
    NEO4J_URI: str = "bolt://localhost:7687"
    NEO4J_USER: str = "neo4j"
    # It's best practice to load secrets from the environment.
    # The value in your .env file will override this default.
    NEO4J_PASSWORD: str = "password"

    # Secret key for things like signing JWTs (JSON Web Tokens) in the future.
    # It's critical to set this in your environment for production.
    SECRET_KEY: str = "a-super-secret-key-that-should-be-changed"

    # API settings
    # This could be used to configure allowed origins for CORS
    ALLOWED_ORIGINS: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]

    # Model configuration
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding='utf-8')

# Create a single, importable instance of the settings
settings = Settings()
