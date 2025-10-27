"""
Test health check functionality
Sends a test health check message to Telegram
"""

from datetime import datetime, timedelta
from dotenv import load_dotenv
from ..notifier import send_health_check

# Load environment variables
load_dotenv()

print("=" * 60)
print("TESTING HEALTH CHECK")
print("=" * 60)

# Create test data
test_start_time = datetime.now() - timedelta(hours=2, minutes=30)
test_uptime = "2h 30m"
test_check_count = 15
test_last_check = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

print("\nSending health check with test data:")
print(f"  Start time: {test_start_time.strftime('%Y-%m-%d %H:%M:%S')}")
print(f"  Uptime: {test_uptime}")
print(f"  Checks: {test_check_count}")
print(f"  Last check: {test_last_check}")
print()

success = send_health_check(
    start_time=test_start_time,
    uptime=test_uptime,
    check_count=test_check_count,
    last_check=test_last_check
)

if success:
    print("✅ Health check sent! Check your Telegram.")
else:
    print("❌ Failed to send health check.")
    print("   Make sure Telegram is configured in .env")

print("=" * 60)

