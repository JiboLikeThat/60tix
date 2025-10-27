"""
Test shutdown notification
Sends a test shutdown notification to Telegram
"""

from datetime import datetime, timedelta
from dotenv import load_dotenv
from ..notifier import send_shutdown_notification

# Load environment variables
load_dotenv()

print("=" * 60)
print("TESTING SHUTDOWN NOTIFICATION")
print("=" * 60)

# Create test data
test_start_time = datetime.now() - timedelta(days=1, hours=5, minutes=30)
test_uptime = "1d 5h 30m"
test_check_count = 150

print("\nSending shutdown notification with test data:")
print(f"  Start time: {test_start_time.strftime('%Y-%m-%d %H:%M:%S')}")
print(f"  Uptime: {test_uptime}")
print(f"  Total checks: {test_check_count}")
print()

success = send_shutdown_notification(
    start_time=test_start_time,
    uptime=test_uptime,
    check_count=test_check_count
)

if success:
    print("✅ Shutdown notification sent! Check your Telegram.")
else:
    print("❌ Failed to send shutdown notification.")
    print("   Make sure Telegram is configured in .env")

print("=" * 60)

