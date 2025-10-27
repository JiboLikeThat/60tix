# 60tix - TSV 1860 München Ticket Monitor

Automatically monitors the [TSV 1860 München ticketing website](https://www.tsv1860-ticketing.de/tsv1860/) for new games and sends Telegram notifications when new tickets become available.

## ⚠️ Disclaimer

This is a personal project for educational purposes. Please use responsibly and respect the website's terms of service. The bot uses a reasonable check interval (default: 10 minutes) to minimize server load.

## Requirements

- Python 3.13+
- [UV](https://github.com/astral-sh/uv) package manager

## Installation

1. Install dependencies using UV:

```bash
uv sync
```

2. Install Playwright browsers:

```bash
uv run playwright install chromium
```

3. Configure Telegram notifications (optional but recommended):

```bash
# Copy the example env file
cp .env.example .env

# Edit .env and add your Telegram credentials
# See "Telegram Setup" section below for details
```

## Telegram Setup

To receive notifications when new tickets are available:

### 1. Create a Telegram Bot

1. Open Telegram and search for `@BotFather`
2. Send `/newbot`
3. Follow prompts to create your bot
4. **Save the bot token** (looks like `1234567890:ABCdefGHI...`)

### 2. Get Your Chat ID

**For personal notifications:**
1. Search for `@userinfobot` on Telegram
2. Start a chat with it
3. It will reply with your **Chat ID** (e.g., `123456789`)

**For group notifications:**
1. Create a Telegram group
2. Add your bot to the group
3. Make bot admin (or allow all members to post)
4. Add `@RawDataBot` to your group temporarily
5. It will post the group info including **Chat ID** (negative number like `-1001234567890`)
6. Remove @RawDataBot from group

Alternativly:
- Login to the Telegram web app (browser)
- Go to the chat/group you want to add
- Copy the group **Chat ID** out of the URL (the number after #)

### 3. Configure Environment Variables

Edit `.env` file:
```bash
TELEGRAM_BOT_TOKEN=your_bot_token_from_botfather
TELEGRAM_CHAT_ID=your_chat_id_or_group_id
CHECK_INTERVAL_MINUTES=10
HEALTH_CHECK_HOUR=9  # Daily status message at 9 AM
```

### 4. Test Your Setup

```bash
uv run python -m src.tests.test_telegram
```

If successful, you'll receive a test message on Telegram!

## Usage

### Run the Monitor

```bash
uv run python -m src.main
```

Or activate the virtual environment first:

```bash
source .venv/bin/activate  # On macOS/Linux
python -m src.main
```

### Test the Scraper

Test the scraper without starting the scheduler:

```bash
uv run python -m src.scraper
```

## Configuration

Configure via `.env` file:
- `TELEGRAM_BOT_TOKEN`: Your bot token from @BotFather
- `TELEGRAM_CHAT_ID`: Your chat or group ID
- `CHECK_INTERVAL_MINUTES`: How often to check for new tickets (default: 10 minutes)
- `HEALTH_CHECK_HOUR`: Daily health check time in 24h format (default: 9 for 9 AM)


## Notification
#### Health Check

The bot sends a daily status message at the configured time showing


#### Shutdown Notifications

When you stop the bot (Ctrl+C), it automatically sends a final notification with:



## Contributing

Feel free to fork and open issues or PRs

## License

MIT License - see [LICENSE](LICENSE) file for details.

