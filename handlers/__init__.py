# ============================================================
# Smm Panel Bot
# Author: LearningBotsOfficial (https://github.com/LearningBotsOfficial) 
# Support: https://t.me/LearningBotsCommunity
# Channel: https://t.me/learning_bots
# YouTube: https://youtube.com/@learning_bots
# License: Open-source (keep credits, no resale)
# ============================================================

from .start import register_start_handler
from .services import register_services_handlers

# ====================================================
# Register all handlers
# ====================================================
def all_handlers(app):
    register_start_handler(app)
    register_services_handlers(app)
    print("✅ Handlers loaded successfully!")
