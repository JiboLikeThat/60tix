# 60tix - TSV 1860 München Ticket Monitor

Automatically monitors the [TSV 1860 München ticketing website](https://www.tsv1860-ticketing.de/tsv1860/) for new games and sends Telegram notifications when new tickets become available.

## ⚠️ Disclaimer

This is a personal project for educational purposes. Please use responsibly and respect the website's terms of service. The bot uses a reasonable check interval (default: 10 minutes) to minimize server load.

## Features

- 🔄 Automatic monitoring with configurable intervals
- 📱 Telegram notifications for new games
- 💾 Persistent state tracking across restarts
- 🏥 Daily health check messages
- 🛡️ Handles website waiting room/queue system
- 🤖 Headless browser automation

## Implementations

This project provides multiple implementations to choose from:

### 🐍 [Python](./python/)
Full-featured implementation using Playwright for web scraping.
- ✅ **Production ready**
- Browser automation with Playwright
- APScheduler for task scheduling
- Comprehensive test suite

**Quick Start:**
```bash
cd python
uv sync
uv run python -m src.main
```

**See [python/README.md](./python/README.md) for full documentation.**

### 🦀 Rust _(Coming Soon)_
High-performance implementation with minimal resource usage.
- 🚧 **In development**
- Planned features: tokio async runtime, headless_chrome
- Lower memory footprint
- Faster startup time

## Notifications

The bot sends Telegram messages for the following events:

### 🎟️ New Games
When new games/tickets become available, you'll receive an instant notification with:
- 🆕 Team matchup (e.g., "TSV 1860 München vs. FC Energie Cottbus")
- 📅 Game date and time
- 🏟️ Matchday information (e.g., "7. Heimspiel")
- 🔗 Direct link to the ticketing page

### 💚 Health Checks
Daily status message showing:
- ✅ Bot status (running/operational)  
- 🕐 Start time
- ⏱️ Uptime
- 🔄 Total checks performed
- 📅 Last check timestamp

### 🛑 Shutdown Notifications
When stopping the bot (Ctrl+C), you'll receive a final notification with:
- 🛑 Shutdown status
- 🕐 Start and stop times
- ⏱️ Total uptime
- 🔄 Total checks performed

## Telegram Setup

To receive notifications, you'll need to create a Telegram bot:

### 1. Create a Bot
1. Open Telegram and search for `@BotFather`
2. Send `/newbot` and follow prompts
3. Save the bot token (looks like `1234567890:ABCdefGHI...`)

### 2. Get Your Chat ID

**For personal notifications:**
- Use `@userinfobot` on Telegram to get your chat ID

**For group notifications:**
- Add `@RawDataBot` to your group temporarily to see the group ID (negative number like `-1001234567890`)
- Or login to Telegram web and copy the ID from the URL

### 3. Configure
Create a `.env` file in your chosen implementation directory with:
```bash
TELEGRAM_BOT_TOKEN=your_bot_token_from_botfather
TELEGRAM_CHAT_ID=your_chat_id_or_group_id
CHECK_INTERVAL_MINUTES=10
HEALTH_CHECK_HOUR=9
```

## Project Structure

```
60tix/
├── python/              # Python implementation
│   ├── src/
│   │   ├── main.py
│   │   ├── scraper.py
│   │   ├── notifier.py
│   │   └── tests/
│   ├── pyproject.toml
│   └── README.md
├── rust/                # Rust implementation (coming soon)
├── LICENSE
└── README.md            # This file
```

## Contributing

Feel free to fork and open issues or PRs! Contributions are welcome for both existing and new implementations.

## License

MIT License - see [LICENSE](LICENSE) file for details.
