"""
Test Telegram notification setup
Run this to verify your bot token and chat ID are working
"""

import os
from dotenv import load_dotenv
from notifier import create_notifier
from scraper import Game

# Load environment variables
load_dotenv()

print("=" * 60)
print("TESTING TELEGRAM NOTIFICATION SETUP")
print("=" * 60)

# Check if environment variables are set
bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
chat_id = os.getenv("TELEGRAM_CHAT_ID")

print("\n1️⃣ Checking environment variables...")
if not bot_token:
    print("   ❌ TELEGRAM_BOT_TOKEN not set")
    print("   💡 Copy .env.example to .env and add your bot token")
    exit(1)
if not chat_id:
    print("   ❌ TELEGRAM_CHAT_ID not set")
    print("   💡 Add your chat ID to .env")
    exit(1)

print(f"   ✅ Bot Token loaded")
print(f"   ✅ Chat ID loaded")

# Create notifier
print("\n2️⃣ Creating Telegram notifier...")
notifier = create_notifier()

if not notifier:
    print("   ❌ Failed to create notifier")
    print("   💡 Check your bot token and chat ID")
    exit(1)

print("   ✅ Notifier created")

# Create a test game
print("\n3️⃣ Creating test game...")
test_game = Game(
    game_id="test-12345-67890",
    teams="TEST TEAM 1 vs. TEST TEAM 2",
    matchday="Test Matchday",
    date="Test Date",
    time="Test Time"
)
print(f"   ✅ Test game: {test_game}")

# Send test notification
print("\n4️⃣ Sending test notification to Telegram...")
success = notifier.notify_new_games([test_game])

if success:
    print("   ✅ Test notification sent!")
else:
    print("   ❌ Failed to send notification")
