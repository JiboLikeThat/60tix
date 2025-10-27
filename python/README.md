# 60tix - Python Implementation

Python implementation of the TSV 1860 München ticket monitor using Playwright for web scraping.

## Requirements

- Python 3.13+
- [UV](https://github.com/astral-sh/uv) package manager

## Installation

1. Install dependencies using UV:

```bash
cd python
uv sync
```

2. Install Playwright browsers:

```bash
uv run playwright install chromium
```

3. Configure Telegram notifications:

```bash
# Copy the example env file
cp .env.example .env

# Edit .env and add your Telegram credentials
```

## Configuration

Edit `.env` file with your credentials and preferences:

```bash
# Required - Your Telegram bot credentials
TELEGRAM_BOT_TOKEN=your_bot_token_from_botfather
TELEGRAM_CHAT_ID=your_chat_id_or_group_id

# Optional - Check interval in minutes (default: 10)
CHECK_INTERVAL_MINUTES=10

# Optional - Daily health check hour in 24h format (default: 9 for 9 AM)
HEALTH_CHECK_HOUR=9
```

### Getting Telegram Credentials

**Create a Bot:**
1. Search for `@BotFather` on Telegram
2. Send `/newbot` and follow prompts
3. Save the bot token

**Get Chat ID:**
- Personal: Use `@userinfobot`
- Group: Add `@RawDataBot` to get group ID (negative number)

## Usage

### Run the Monitor

```bash
cd python
uv run python -m src.main
```

Or activate the virtual environment:

```bash
cd python
source .venv/bin/activate  # On macOS/Linux
python -m src.main
```

### Test Components

```bash
# Test the scraper
uv run python -m src.scraper

# Test Telegram notifications
uv run python -m src.tests.test_telegram

# Test health check notification
uv run python -m src.tests.test_health_check

# Test shutdown notification
uv run python -m src.tests.test_shutdown

# Test first run behavior
uv run python -m src.tests.test_first_run
```

## Project Structure

```
python/
├── src/
│   ├── main.py           # Entry point & scheduler
│   ├── scraper.py        # Web scraping with Playwright
│   ├── notifier.py       # Telegram integration
│   └── tests/            # Test scripts
├── .env.example          # Environment template
├── pyproject.toml        # Dependencies (UV format)
└── README.md             # This file
```

## Features

- 🤖 Headless browser automation with Playwright
- 🛡️ Handles website waiting room/queue system
- 📱 Telegram notifications via Bot API
- 💾 JSON-based state persistence
- ⏰ APScheduler for interval-based checks
- 🏥 Daily health check messages
- 🛑 Graceful shutdown notifications

## Dependencies

- **playwright** - Browser automation
- **beautifulsoup4** + **lxml** - HTML parsing
- **apscheduler** - Task scheduling
- **requests** - HTTP client for Telegram API
- **python-dotenv** - Environment variable management

