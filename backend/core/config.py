from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

# Build a path to the .env file in the project root.
# This makes the settings file location-independent.
# The project root is three levels up from this file's directory
# (core/ -> backend/ -> project root).
env_path = Path(__file__).parent.parent.parent / ".env"

class Settings(BaseSettings):
    """
    Defines the application's configuration settings.

    pydantic-settings will automatically attempt to load these values
    from a .env file or from system environment variables.
    """

    # Database configuration
    NEO4J_URI: str = "bolt://localhost:7687"
    NEO4J_USER: str = "neo4j"
    NEO4J_PASSWORD: str = "default_pw"

    # Secret key for things like signing JWTs (JSON Web Tokens) in the future.
    SECRET_KEY: str = "super-secret-key"

    # API settings
    # This could be used to configure allowed origins for CORS
    ALLOWED_ORIGINS: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]

    # Model configuration
    # By providing an absolute path to the .env file, we avoid issues
    # with the current working directory.
    model_config = SettingsConfigDict(env_file=env_path, env_file_encoding='utf-8', extra='ignore')

# Create a single, importable instance of the settings
settings = Settings()
