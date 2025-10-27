"""
TSV 1860 München Ticket Monitor
Main entry point - runs the scraper on a schedule.
"""

import os
import logging
from dotenv import load_dotenv
from apscheduler.schedulers.blocking import BlockingScheduler
from .scraper import get_games, check_for_new_games, save_state
from .notifier import notify_new_games

# Load environment variables from .env file
load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration
CHECK_INTERVAL_MINUTES = int(os.getenv("CHECK_INTERVAL_MINUTES", "10"))


def scheduled_check():
    """Wrapper function for scheduled checks."""
    try:
        logger.info("=" * 60)
        games = get_games()
        
        if not games:
            logger.warning("No games found on website")
            return
        
        new_games = check_for_new_games(games)
        
        if new_games:
            logger.info(f"🎉 Found {len(new_games)} NEW game(s)!")
            for game in new_games:
                logger.info(f"  NEW: {game}")
            
            # Send Telegram notification
            if notify_new_games(new_games):
                logger.info("Telegram notification sent successfully")
            else:
                logger.warning("Telegram notification failed or not configured")
        else:
            logger.info("No new games found")
        
        # Save current state
        save_state(games)
        
    except Exception as e:
        logger.error(f"Error during scheduled check: {e}", exc_info=True)


def initalize_games_state():
    """Perform the initial check on startup - saves current games as baseline."""
    logger.info("Performing initial check...")
    logger.info("=" * 60)
    try:
        games = get_games()
        
        if not games:
            logger.error("No games found - cannot initialize baseline")
            return False
        
        logger.info(f"Found {len(games)} game(s) - saving as baseline")
        for game in games:
            logger.info(f"  - {game}")
        
        # Save as baseline
        save_state(games)
        logger.info("Initial check complete - baseline saved")
        return True
        
    except Exception as e:
        logger.error(f"Initial check failed: {e}", exc_info=True)
        return False


def setup_scheduler():
    """Configure and return the scheduler."""
    scheduler = BlockingScheduler()
    scheduler.add_job(
        scheduled_check,
        'interval',
        minutes=CHECK_INTERVAL_MINUTES,
        id='ticket_check',
        name='Check for new games',
        max_instances=1
    )
    return scheduler


def run_scheduler(scheduler):
    """Start the scheduler and handle shutdown."""
    logger.info(f"⏰ Scheduler started - checking every {CHECK_INTERVAL_MINUTES} minutes")
    logger.info("Press Ctrl+C to stop")
    logger.info("=" * 60)
    
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logger.info("\n👋 Shutting down ticket monitor...")
        scheduler.shutdown()


def main():
    """Main function - orchestrates the ticket monitoring system."""
    logger.info("🚀 Starting TSV 1860 München Ticket Monitor")
    logger.info("=" * 60)
    
    # Perform initial check
    initalize_games_state()
    logger.info("=" * 60)
    
    # Setup and run scheduler to check every X minutes
    scheduler = setup_scheduler()
    run_scheduler(scheduler)


if __name__ == "__main__":
    main()
