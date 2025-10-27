# 60tix - Rust Implementation

High-performance Rust implementation of the TSV 1860 München ticket monitor using headless Chrome for web scraping.

## Requirements

- Rust 1.70+ (Install from [rustup.rs](https://rustup.rs))
- Chrome/Chromium browser (for headless_chrome)

## Installation

1. **Install Rust** (if not already installed):
```bash
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
```

2. **Build the project**:
```bash
cd rust
cargo build --release
```

3. **Configure Telegram notifications**:
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

**Development mode:**
```bash
cd rust
cargo run
```

**Production mode (optimized):**
```bash
cd rust
cargo build --release
./target/release/sixtix
```

### Start Script

```bash
cd rust
chmod +x start.sh
./start.sh
```

## Project Structure

```
rust/
├── src/
│   ├── main.rs          # Entry point & scheduler
│   ├── scraper.rs       # Web scraping with headless Chrome
│   ├── notifier.rs      # Telegram integration
│   └── state.rs         # State management
├── Cargo.toml           # Dependencies
├── .env.example         # Environment template
└── README.md            # This file
```

## Features

- 🦀 **High Performance** - Fast startup, low memory usage
- 🤖 **Headless Chrome** - Full JavaScript support for dynamic content
- 🛡️ **Handles waiting rooms** - Automatic queue detection and waiting
- 📱 **Telegram notifications** - Via reqwest HTTP client
- 💾 **JSON state persistence** - Tracks games between restarts
- ⏰ **Async scheduling** - tokio-cron-scheduler for efficient task management
- 🏥 **Daily health checks** - Automated status reports
- 🛑 **Graceful shutdown** - Sends notification on exit

## Dependencies

Core libraries used:
- **tokio** - Async runtime
- **reqwest** - HTTP client for Telegram API
- **headless_chrome** - Browser automation
- **scraper** - HTML parsing
- **serde/serde_json** - Serialization
- **tokio-cron-scheduler** - Task scheduling
- **chrono** - Date/time handling
- **anyhow** - Error handling
- **dotenv** - Environment variable management
- **log/env_logger** - Logging

## Performance

The Rust implementation is optimized for:
- **Low memory usage** - Typically 20-30MB RAM
- **Fast startup** - ~1-2 seconds to first check
- **Efficient scheduling** - Minimal CPU usage when idle
- **Release builds** - Stripped and LTO-optimized binary

## Comparison with Python

| Feature | Rust | Python |
|---------|------|--------|
| Startup time | ~1-2s | ~3-5s |
| Memory usage | ~25MB | ~80MB |
| CPU (idle) | ~0.1% | ~0.3% |
| Binary size | ~15MB | N/A (interpreted) |
| Dependencies | Compiled in | External packages |

## Building

**Debug build:**
```bash
cargo build
```

**Release build (optimized):**
```bash
cargo build --release
```

**Check without building:**
```bash
cargo check
```

**Run tests:**
```bash
cargo test
```

## Troubleshooting

### Chrome/Chromium not found
- Ensure Chrome or Chromium is installed on your system
- The headless_chrome library will try to auto-detect the browser

### Compilation errors
- Ensure you have the latest stable Rust: `rustup update`
- Check that all system dependencies are installed

### Connection errors
- Verify your Telegram credentials in `.env`
- Check your internet connection
- Ensure the ticketing website is accessible

## License

MIT License - see [LICENSE](../LICENSE) file for details.
