"""Configuration settings for the resume builder application."""

import os
from dotenv import load_dotenv
from google import genai

# Load environment variables from .env file
load_dotenv()

# API Configuration
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")

# Retry Configuration
RETRY_CONFIG = genai.types.HttpRetryOptions(
    attempts=5,
    exp_base=7,
    initial_delay=1,
    http_status_codes=[429, 500, 503, 504]
)

# Application Constants
APP_NAME = "resume_parser"
USER_ID = "default"
MODEL_NAME = "gemini-2.5-flash-lite"

# Database Configuration
DATABASE_URL = "sqlite:///resume_sessions.db"

# File Paths
RESUME_FILE_PATH = "Clifford.Resume.2025.pdf"
