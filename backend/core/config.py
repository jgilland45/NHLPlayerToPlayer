from pydantic_settings import BaseSettings, SettingsConfigDict
import os

class Settings(BaseSettings):
    """
    Defines the application's configuration settings.

    pydantic-settings will automatically attempt to load these values
    from a .env file or from system environment variables.
    """

    # Database configuration
    # The default value points to a local SQLite database file named `nhl_app.db`
    # in the project's root directory.
    DATABASE_URL: str = f"sqlite:///{os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))}/nhl_app.db"

    # Secret key for things like signing JWTs (JSON Web Tokens) in the future.
    # It's critical to set this in your environment for production.
    SECRET_KEY: str = "a-super-secret-key-that-you-should-change"

    # API settings
    # This could be used to configure allowed origins for CORS
    ALLOWED_ORIGINS: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]

    # Model configuration
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding='utf-8')

# Create a single, importable instance of the settings
settings = Settings()
