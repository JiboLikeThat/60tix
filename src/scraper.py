"""
TSV 1860 München Ticket Scraper
Monitors the ticketing website for new games.
"""

import re
import json
import logging
from typing import List, Dict, Set
from pathlib import Path
from datetime import datetime

from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
from bs4 import BeautifulSoup

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

TICKETING_URL = "https://www.tsv1860-ticketing.de/tsv1860/"
STATE_FILE = Path("state.json")


class Game:
    """Represents a game/event."""
    
    def __init__(self, game_id: str, teams: str, matchday: str, date: str, time: str):
        self.game_id = game_id
        self.teams = teams
        self.matchday = matchday
        self.date = date
        self.time = time
    
    def to_dict(self) -> Dict:
        return {
            'game_id': self.game_id,
            'teams': self.teams,
            'matchday': self.matchday,
            'date': self.date,
            'time': self.time
        }
    
    def __str__(self) -> str:
        return f"{self.teams} - {self.date} {self.time} ({self.matchday})"
    
    def __repr__(self) -> str:
        return f"Game({self.game_id}, {self.teams})"


def fetch_page() -> str:
    """
    Fetch the ticketing page HTML using Playwright.
    Handles the waiting room/queue system.
    """
    try:
        with sync_playwright() as p:
            logger.info("Launching browser...")
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            
            logger.info(f"Navigating to {TICKETING_URL}")
            page.goto(TICKETING_URL, wait_until='domcontentloaded', timeout=60000)
            
            # Check if we're in the waiting room
            if 'waiting-room' in page.url or 'Warteraum' in page.title():
                logger.info("Entered waiting room, waiting for queue to pass...")
                
                # Wait for the "Zum Shop" button to appear (max 5 minutes)
                try:
                    # wait for 30 minutes in the queue 
                    page.wait_for_url(TICKETING_URL, wait_until='domcontentloaded', timeout=1800000)
                except PlaywrightTimeout:
                    logger.error("Timeout waiting for page to load")
                    browser.close()
                    raise
            
            logger.info(f"Successfully loaded page: {page.title()}")
            logger.info(f"Current URL: {page.url}")
            
            # Get the page content
            html = page.content()
            
            browser.close()
            return html
            
    except Exception as e:
        logger.error(f"Failed to fetch page: {e}")
        raise


def parse_games(html: str) -> List[Game]:
    """Parse the HTML to extract game information."""
    soup = BeautifulSoup(html, 'lxml')
    games = []
    
    # Debug: Save HTML to file for inspection
    debug_file = Path("debug_page.html")
    with open(debug_file, 'w', encoding='utf-8') as f:
        f.write(html)
    logger.debug(f"Saved HTML to {debug_file} for inspection")
    logger.debug(f"HTML length: {len(html)} characters")
    
    # Find the EventList container first
    event_list = soup.find('div', class_='row eventlist')
    if not event_list:
        logger.warning("EventList div not found on page")
        logger.warning(f"Available divs with 'row' class: {len(soup.find_all('div', class_=re.compile('row')))}")
        logger.warning(f"Available divs with 'eventlist' class: {len(soup.find_all('div', class_=re.compile('eventlist')))}")
        return games
    
    # Find all game divs within EventList, excluding empty items
    all_divs = event_list.find_all('div', class_=re.compile(r'container.*listitem'))
    game_divs = [div for div in all_divs if 'b-item-empty' not in div.get('class', [])]
    logger.debug(f"Found {len(all_divs)} total list items, {len(game_divs)} non-empty")
    
    for div in game_divs:
        try:
            # Find the itemheaderbox within the div
            header_box = div.find('div', class_='itemheaderbox')
            if not header_box:
                continue
            
            # Get all links from the header box
            links = header_box.find_all('a', class_='col')
            if len(links) < 2:
                continue
            
            # Extract game ID from the first link's href
            first_link = links[0]
            href = first_link.get('href', '')
            game_id_match = re.search(r'([a-f0-9\-]{36})', href)
            if not game_id_match:
                continue
            game_id = game_id_match.group(1)
            
            # Extract team names from the nested spans in the first link
            teams_span = first_link.find('span', class_='SmallerGrad1')
            teams = teams_span.get_text(strip=True) if teams_span else "Unknown"
            
            # Extract matchday info from the second link (e.g., "7. Heimspiel")
            matchday = links[1].get_text(strip=True) if len(links) > 1 else ""
            
            # Extract date
            date_span = div.find('span', class_='date')
            date = date_span.get_text(strip=True) if date_span else "Unknown"
            
            # Extract time
            time_span = div.find('span', class_='time')
            time = ""
            if time_span:
                time_text = time_span.get_text(strip=True)
                # Extract just the time (remove icon text)
                time = time_text.replace('Uhr', '').strip()
            
            game = Game(game_id, teams, matchday, date, time)
            games.append(game)
            logger.debug(f"Parsed game: {game}")
            
        except Exception as e:
            logger.warning(f"Failed to parse game div: {e}")
            continue
    
    logger.info(f"Found {len(games)} games")
    return games


def load_state() -> Set[str]:
    """Load the previous game IDs from state file."""
    if not STATE_FILE.exists():
        logger.info("No state file found, creating new one")
        return set()
    
    try:
        with open(STATE_FILE, 'r') as f:
            data = json.load(f)
            
            # Extract IDs from games array
            games = data.get('games', [])
            game_ids = {game['game_id'] for game in games}
            
            logger.info(f"Loaded {len(game_ids)} game IDs from state")
            return game_ids
    except Exception as e:
        logger.error(f"Failed to load state: {e}")
        return set()


def save_state(games: List[Game]):
    """Save the current games to state file."""
    try:
        # Load existing state to preserve 'started' field
        started = None
        if STATE_FILE.exists():
            try:
                with open(STATE_FILE, 'r') as f:
                    existing_data = json.load(f)
                    started = existing_data.get('started')
            except Exception:
                pass
        
        # Set started field if not exists (first run)
        if started is None:
            started = datetime.now().isoformat()
        
        data = {
            'started': started,
            'last_updated': datetime.now().isoformat(),
            'games': [game.to_dict() for game in games]
        }
        
        with open(STATE_FILE, 'w') as f:
            json.dump(data, f, indent=2)
        logger.info(f"Saved state with {len(games)} games")
    except Exception as e:
        logger.error(f"Failed to save state: {e}")


def get_games() -> List[Game]:
    """
    Check the ticketing website for games.
    
    Returns:
        List of games found on the page.
    """
    logger.info("Checking for games...")
    html = fetch_page()
    games = parse_games(html)
    if not games:
        logger.error("No games found")
        return []
    return games

def check_for_new_games(games: List[Game]) -> List[Game]:
    """
    Check for new games compared to the games list.
    
    Returns:
        List of new games.
    """
    previous_games = load_state()
    new_games = [game for game in games if game.game_id not in previous_games]
    return new_games


if __name__ == "__main__":
    # Main function to test the scraper
    print("Testing TSV 1860 München Ticket Scraper")
    print("-" * 60)
    games = get_games()
    new_games = check_for_new_games(games)
    logger.info(f"Found {len(new_games)} new game(s):")
    for game in new_games:
        logger.info(f" - {game}")

