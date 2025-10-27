"""
Telegram notification service for 60tix
Sends alerts when new games are detected
"""

import os
import logging
from typing import List, Optional
from datetime import datetime
import requests

from .scraper import Game

logger = logging.getLogger(__name__)


class TelegramNotifier:
    """Handles Telegram bot notifications"""
    
    def __init__(self, bot_token: str, chat_id: str):
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.base_url = f"https://api.telegram.org/bot{bot_token}"
    
    def send_message(self, text: str, parse_mode: str = "HTML") -> bool:
        """Send a text message via Telegram"""
        try:
            url = f"{self.base_url}/sendMessage"
            payload = {
                "chat_id": self.chat_id,
                "text": text,
                "parse_mode": parse_mode,
                "disable_web_page_preview": False
            }
            response = requests.post(url, json=payload, timeout=10)
            response.raise_for_status()
            logger.info("✅ Telegram notification sent")
            return True
        except requests.RequestException as e:
            logger.error(f"❌ Failed to send Telegram notification: {e}")
            return False
    
    def notify_new_games(self, games: List[Game]) -> bool:
        """Send notification about new games with formatting"""
        if not games:
            return True
        
        # Build message with HTML formatting
        if len(games) == 1:
            message = "🎉 <b>New Ticket Available!</b>\n\n"
        else:
            message = f"🎉 <b>{len(games)} New Tickets Available!</b>\n\n"
        
        for game in games:
            message += f"⚽ <b>{game.teams}</b>\n"
            message += f"📅 {game.date} • ⏰ {game.time}\n"
            message += f"🏟️ {game.matchday}\n"
            
            # Add direct link to game
            game_url = f"https://www.tsv1860-ticketing.de/tsv1860/data/Veranstaltungen2/{game.game_id}"
            message += f"🎫 <a href='{game_url}'>Buy Tickets</a>\n\n"
        
        message += "🔗 <a href='https://www.tsv1860-ticketing.de/tsv1860/'>Visit Ticket Shop</a>"
        
        return self.send_message(message)
    
    def test_connection(self) -> bool:
        """Test if bot token and chat_id are valid"""
        try:
            url = f"{self.base_url}/getMe"
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            bot_info = response.json()
            if bot_info.get("ok"):
                bot_username = bot_info['result']['username']
                logger.info(f"✅ Connected to Telegram bot: @{bot_username}")
                return True
            return False
        except Exception as e:
            logger.error(f"❌ Telegram connection test failed: {e}")
            return False


def load_telegram_config() -> Optional[dict]:
    """
    Load Telegram config from environment variables.
    Returns dict with bot_token and chat_id, or None if not configured.
    """
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    
    if bot_token and chat_id:
        logger.info("✅ Telegram config loaded from environment variables")
        return {
            "bot_token": bot_token,
            "chat_id": chat_id
        }
    
    logger.warning("⚠️  No Telegram config found in environment variables")
    logger.warning("   Set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID to enable notifications")
    return None


def create_notifier() -> Optional[TelegramNotifier]:
    """Create and return a TelegramNotifier if configured"""
    config = load_telegram_config()
    
    if not config:
        return None
    
    bot_token = config.get("bot_token")
    chat_id = config.get("chat_id")
    
    if not bot_token or not chat_id:
        logger.error("❌ Telegram bot_token or chat_id missing")
        return None
    
    notifier = TelegramNotifier(bot_token, str(chat_id))
    
    # Test connection
    if notifier.test_connection():
        return notifier
    else:
        logger.error("❌ Failed to connect to Telegram")
        return None


def notify_new_games(games: List[Game]) -> bool:
    """
    Send notification about new games (convenience function).
    Returns True if notification sent successfully, False otherwise.
    """
    notifier = create_notifier()
    if notifier:
        return notifier.notify_new_games(games)
    else:
        logger.info("ℹ️  Telegram notifications not configured - skipping")
        return False


def send_health_check(start_time, uptime: str, check_count: int, last_check: str) -> bool:
    """
    Send daily health check status to Telegram.
    Returns True if sent successfully, False otherwise.
    """
    notifier = create_notifier()
    if not notifier:
        logger.info("ℹ️  Telegram notifications not configured - skipping health check")
        return False
    
    # Build health check message
    message = "🏥 <b>Bot Health Check</b>\n\n"
    message += "✅ <b>Status:</b> Running\n\n"
    
    if start_time:
        message += f"🕐 <b>Started:</b> {start_time.strftime('%Y-%m-%d %H:%M:%S')}\n"
    message += f"⏱️ <b>Uptime:</b> {uptime}\n"
    message += f"🔄 <b>Checks performed:</b> {check_count}\n"
    message += f"📅 <b>Last check:</b> {last_check}\n"
    
    return notifier.send_message(message)


def send_shutdown_notification(start_time, uptime: str, check_count: int) -> bool:
    """
    Send shutdown notification to Telegram.
    Returns True if sent successfully, False otherwise.
    """
    notifier = create_notifier()
    if not notifier:
        logger.info("ℹ️  Telegram notifications not configured - skipping shutdown notification")
        return False
    
    # Build shutdown message
    message = "🛑 <b>Bot Shutting Down</b>\n\n"
    
    if start_time:
        message += f"🕐 <b>Started:</b> {start_time.strftime('%Y-%m-%d %H:%M:%S')}\n"
        message += f"🕑 <b>Stopped:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    message += f"⏱️ <b>Total uptime:</b> {uptime}\n"
    message += f"🔄 <b>Total checks:</b> {check_count}\n"
    
    return notifier.send_message(message)

