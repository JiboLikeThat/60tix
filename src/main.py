"""
TSV 1860 München Ticket Monitor
Main entry point - runs the scraper on a schedule.
"""

import os
import logging
from datetime import datetime
from dotenv import load_dotenv
from apscheduler.schedulers.blocking import BlockingScheduler
from .scraper import get_games, check_for_new_games, save_state
from .notifier import notify_new_games, send_health_check, send_shutdown_notification

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
HEALTH_CHECK_HOUR = int(os.getenv("HEALTH_CHECK_HOUR", "9"))  # Default 9 AM

# Bot statistics
bot_start_time = None
check_counter = 0
last_check_time = None


def scheduled_check():
    """Wrapper function for scheduled checks."""
    global check_counter, last_check_time
    
    check_counter += 1
    last_check_time = datetime.now()
    
    try:
        logger.info("=" * 60)
        logger.info(f"Check #{check_counter} - {last_check_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
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


def health_check():
    """Send daily health check message to Telegram."""
    try:
        logger.info("=" * 60)
        logger.info("Performing health check...")
        
        # Calculate uptime
        if bot_start_time:
            uptime = datetime.now() - bot_start_time
            days = uptime.days
            hours, remainder = divmod(uptime.seconds, 3600)
            minutes, _ = divmod(remainder, 60)
            
            if days > 0:
                uptime_str = f"{days}d {hours}h {minutes}m"
            elif hours > 0:
                uptime_str = f"{hours}h {minutes}m"
            else:
                uptime_str = f"{minutes}m"
        else:
            uptime_str = "Unknown"
        
        # Format last check time
        if last_check_time:
            last_check_str = last_check_time.strftime('%Y-%m-%d %H:%M:%S')
        else:
            last_check_str = "No checks yet"
        
        # Send health check
        success = send_health_check(
            start_time=bot_start_time,
            uptime=uptime_str,
            check_count=check_counter,
            last_check=last_check_str
        )
        
        if success:
            logger.info("Health check sent to Telegram")
        else:
            logger.warning("Health check failed or not configured")
            
    except Exception as e:
        logger.error(f"Error during health check: {e}", exc_info=True)


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
    
    # Add ticket checking job
    scheduler.add_job(
        scheduled_check,
        'interval',
        minutes=CHECK_INTERVAL_MINUTES,
        id='ticket_check',
        name='Check for new games',
        max_instances=1
    )
    
    # Add daily health check job
    scheduler.add_job(
        health_check,
        'cron',
        hour=HEALTH_CHECK_HOUR,
        minute=0,
        id='health_check',
        name='Daily health check',
        max_instances=1
    )
    
    logger.info(f"📋 Health check scheduled daily at {HEALTH_CHECK_HOUR:02d}:00")
    
    return scheduler


def run_scheduler(scheduler):
    """Start the scheduler and handle shutdown."""
    logger.info(f"Scheduler started - checking every {CHECK_INTERVAL_MINUTES} minutes")
    logger.info("Press Ctrl+C to stop")
    logger.info("=" * 60)
    
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logger.info("\nShutting down ticket monitor...")
        
        # Calculate final uptime
        if bot_start_time:
            uptime = datetime.now() - bot_start_time
            days = uptime.days
            hours, remainder = divmod(uptime.seconds, 3600)
            minutes, _ = divmod(remainder, 60)
            
            if days > 0:
                uptime_str = f"{days}d {hours}h {minutes}m"
            elif hours > 0:
                uptime_str = f"{hours}h {minutes}m"
            else:
                uptime_str = f"{minutes}m"
        else:
            uptime_str = "Unknown"
        
        # Log final statistics
        logger.info(f"Total checks performed: {check_counter}")
        logger.info(f"Total uptime: {uptime_str}")
        
        # Send shutdown notification to Telegram
        if send_shutdown_notification(bot_start_time, uptime_str, check_counter):
            logger.info("Shutdown notification sent to Telegram")
        
        scheduler.shutdown()


def main():
    """Main function - orchestrates the ticket monitoring system."""
    global bot_start_time
    
    bot_start_time = datetime.now()
    
    logger.info("Starting TSV 1860 München Ticket Monitor")
    logger.info(f"Started at: {bot_start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 60)
    
    # Perform initial check
    initalize_games_state()
    logger.info("=" * 60)
    
    # Setup and run scheduler to check every X minutes
    scheduler = setup_scheduler()
    run_scheduler(scheduler)


if __name__ == "__main__":
    main()
