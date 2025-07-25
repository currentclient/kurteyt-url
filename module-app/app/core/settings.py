"""Settings"""

from typing import List, Optional

from pydantic import EmailStr
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Settings"""

    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "kurteyt-url"

    # Cors
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:8000",
        "http://0.0.0.0:8000",
        "https://kurteyt.currentclient.io",
    ]

    # Email
    EMAILS_FROM_EMAIL: Optional[EmailStr] = None
    EMAILS_FROM_NAME: Optional[str] = None

    class Config:
        """Config"""

        case_sensitive = True


settings = Settings()
