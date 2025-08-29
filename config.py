import os
from typing import Optional

class Config:
    API_KEY: str = os.getenv("API_KEY", "")
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
    MAX_FILE_SIZE: int = int(os.getenv("MAX_FILE_SIZE", "52428800"))  # 50MB
    PORT: int = int(os.getenv("PORT", "8000"))

    @classmethod
    def validate(cls) -> None:
        if not cls.API_KEY:
            raise ValueError("API_KEY environment variable is required")
        if not cls.ANTHROPIC_API_KEY:
            raise ValueError("ANTHROPIC_API_KEY environment variable is required")