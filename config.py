"""Configuration management for Document Reader API."""

import os
from typing import Optional

# Required settings
API_KEY = os.getenv("API_KEY")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

# Optional settings with defaults
MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE", "52428800"))  # 50MB
PORT = int(os.getenv("PORT", "8000"))
DEBUG = os.getenv("DEBUG", "false").lower() == "true"
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# Validate required settings
if not API_KEY:
    raise ValueError("API_KEY environment variable required")
if not ADMIN_PASSWORD:
    raise ValueError("ADMIN_PASSWORD environment variable required")
if not ANTHROPIC_API_KEY:
    raise ValueError("ANTHROPIC_API_KEY environment variable required")

# Data storage paths
DATA_DIR = "data"
CONFIG_FILE = os.path.join(DATA_DIR, "config.json")

# File processing settings
SUPPORTED_EXTENSIONS = [".pdf"]
PROCESSING_TIMEOUT = 90  # seconds