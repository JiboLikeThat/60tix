# 60tix - TSV 1860 München Ticket Monitor

Automatically monitors the [TSV 1860 München ticketing website](https://www.tsv1860-ticketing.de/tsv1860/) for new games and sends email notifications when new tickets become available.

## Features
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

## Usage

### Run the Monitor

Start the ticket monitor (performs initial check, then checks every X minutes):

```bash
uv run python main.py
```

Or activate the virtual environment first:

```bash
source .venv/bin/activate  # On macOS/Linux
python main.py
```

### Test the Scraper

Test the scraper without starting the scheduler:

```bash
uv run python scraper.py
```

## How It Works

1. **Initial Check**: On startup, fetches the current games from the ticketing website
2. **State Tracking**: Saves game data to `state.json` 
3. **Scheduled Checks**: Every 10 minutes, re-fetches the page and compares with saved state
4. **New Game Detection**: Identifies games that weren't present in the previous check
5. **Notifications**: Logs new games (email notifications to be implemented)

## Project Structure

```
60tix/
├── main.py              # Main entry point with scheduler
├── scraper.py           # Web scraper logic
├── pyproject.toml       # UV project configuration
├── state.json           # Current game state (auto-generated)
└── README.md
```

## Configuration

Currently hardcoded values:
- Check interval: 10 minutes
- Target URL: https://www.tsv1860-ticketing.de/tsv1860/

## Upcoming Features

- [ ] Email notifications via SMTP
- [ ] Configurable check intervals
- [ ] Filter games by criteria (date, opponent, etc.)
- [ ] Automatic ticket booking
- [ ] Web dashboard for monitoring

## Game Data Structure

Each game contains:
- `game_id`: Unique identifier (UUID)
- `teams`: Match description (e.g., "TSV 1860 München vs. 1.FC Saarbrücken")
- `matchday`: Home game number (e.g., "8. Heimspiel")
- `date`: Game date (e.g., "So. 23.11.2025")
- `time`: Kickoff time (e.g., "13:30")

State file (`state.json`) structure:
```json
{
  "started": "2025-10-27T08:00:00",
  "last_updated": "2025-10-27T12:00:00",
  "games": [
    {
      "game_id": "abc-123-def-456",
      "teams": "TSV 1860 München vs. FC Energie Cottbus",
      "matchday": "7. Heimspiel",
      "date": "Sa. 01.11.2025",
      "time": "14:00"
    }
  ]
}
```

Fields:
- `started`: Timestamp when bot was first started (set once, never changes)
- `last_updated`: Timestamp of last state update
- `games`: Array of currently available games

## Troubleshooting

### Queue System
The ticketing website uses a queue/waiting room system during high traffic. The scraper uses Playwright to:
1. Detect when in the waiting room
2. Wait for the queue to pass (up to 5 minutes)
3. Automatically click "Zum Shop" button to enter
4. Continue with the scraping

If the queue takes longer than 5 minutes, the scraper will timeout and retry on the next scheduled check.

### No Games Found
If no games are found:
1. Check the website manually to verify games are listed
2. The HTML structure may have changed - check `scraper.py` parsing logic
3. Run with debug logging: modify `logging.basicConfig(level=logging.DEBUG)`

## Development

### Adding Email Notifications

To implement email notifications, edit `main.py` in the `scheduled_check()` function where it says:

```python
# TODO: Send email notification here
```

## License

Personal project - use at your own discretion.

