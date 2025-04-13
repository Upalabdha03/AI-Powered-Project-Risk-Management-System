"""Configuration parameters for the risk management system."""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Keys
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Database
CHROMA_DB_PATH = "./data/vector_db"

# Risk thresholds
HIGH_RISK_THRESHOLD = 70
MEDIUM_RISK_THRESHOLD = 40

# Risk weights (adjust as needed)
STATIC_RISK_WEIGHT = 0.6
NEWS_RISK_WEIGHT = 0.4

# Email settings
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
EMAIL_SENDER = os.getenv("EMAIL_SENDER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")