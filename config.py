# ============================================================
# Smm Panel Bot
# Author: LearningBotsOfficial (https://github.com/LearningBotsOfficial) 
# Support: https://t.me/LearningBotsCommunity
# Channel: https://t.me/learning_bots
# YouTube: https://youtube.com/@learning_bots
# License: Open-source (keep credits, no resale)
# ============================================================

from dotenv import load_dotenv
import os

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
API_ID = int(os.getenv("API_ID", 0))
API_HASH = os.getenv("API_HASH")
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME")
OWNER_ID = int(os.getenv("OWNER_ID"))
OWNER_USERNAME = os.getenv("OWNER_USERNAME")
REFERRER_BONUS = int(os.getenv("REFERRER_BONUS", 10))
DAILY_BONUS = int(os.getenv("DAILY_BONUS", 10))
QR_IMAGE = os.getenv("QR_IMAGE")
FORCE_CHANNEL = os.getenv("FORCE_CHANNEL")
SMM_SITE = {
    "name": os.getenv("SMM_SITE"),            
    "api_url": os.getenv("SMM_API_URL"),         
    "api_key": os.getenv("SMM_API_KEY"),       
    "services": {
        "reaction": int(os.getenv("REACTION_SERVICE_ID", 0)),
        "members": int(os.getenv("MEMBERS_SERVICE_ID", 0)),
        "views": int(os.getenv("VIEWS_SERVICE_ID", 0))
    }
}

ORDER_CHANNEL = os.getenv("ORDER_CHANNEL")


# ----------------- Validation -----------------
def validate_config():
    missing = []

    required_vars = [
        "BOT_TOKEN", "API_ID", "API_HASH",
        "MONGO_URI", "DB_NAME",
        "SMM_API_URL", "SMM_API_KEY",
        "REACTION_SERVICE_ID", "MEMBERS_SERVICE_ID", "VIEWS_SERVICE_ID",
        "ORDER_CHANNEL"
    ]

    for var in required_vars:
        if not os.getenv(var):
            missing.append(var)

    if API_ID == 0:
        missing.append("API_ID")

    if missing:
        raise ValueError(
            f"❌ Missing environment variables: {', '.join(missing)}"
        )
