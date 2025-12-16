"""
Main Reminder Service
Background service that continuously monitors and executes reminders.
"""
import os
import sys
import time
import signal
import logging
from datetime import datetime

# Add src directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from data_manager import get_all_reminders
from scheduler import get_due_reminders, get_upcoming_reminders
from call_manager import execute_reminder
from config import TWILIO_FROM_NUMBER


# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ReminderService:
    """Background service for executing reminders."""
    
    def __init__(self, from_number: str, check_interval: int = 60):
        """
        Initialize the reminder service.
        
        Args:
            from_number: Twilio phone number to call from (E.164 format)
            check_interval: How often to check for due reminders (seconds)
        """
        self.from_number = from_number
        self.check_interval = check_interval
        self.running = False
        self.last_upcoming_log_time = 0
        self.upcoming_log_interval = 3600  # Log upcoming reminders every hour
        
        # Set up signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals."""
        logger.info(f"Received signal {signum}. Shutting down gracefully...")
        self.running = False
    
    def run(self):
        """Start the reminder service loop."""
        logger.info("Starting Reminder Service...")
        logger.info(f"Checking for reminders every {self.check_interval} seconds")
        logger.info(f"Using Twilio number: {self.from_number}")
        
        # Log upcoming reminders on startup
        self._log_upcoming_reminders()
        
        self.running = True
        
        try:
            while self.running:
                self._check_and_execute_reminders()
                
                # Log upcoming reminders periodically (every hour)
                current_time = time.time()
                if current_time - self.last_upcoming_log_time >= self.upcoming_log_interval:
                    self._log_upcoming_reminders()
                    self.last_upcoming_log_time = current_time
                
                time.sleep(self.check_interval)
        except KeyboardInterrupt:
            logger.info("Service interrupted by user")
        finally:
            logger.info("Reminder Service stopped")
    
    def _check_and_execute_reminders(self):
        """Check for due reminders and execute them."""
        try:
            # Get all reminders
            reminders = get_all_reminders()
            
            if not reminders:
                logger.debug("No reminders found")
                return
            
            # Get due reminders
            due_reminders = get_due_reminders(reminders)
            
            if not due_reminders:
                logger.debug(f"Checked {len(reminders)} reminders, none are due")
                return
            
            logger.info(f"Found {len(due_reminders)} due reminder(s)")
            
            # Execute each due reminder
            for reminder in due_reminders:
                logger.info(f"Executing reminder ID: {reminder['id']} for {reminder['user_name']}")
                success = execute_reminder(reminder, self.from_number)
                
                if success:
                    logger.info(f"Successfully executed reminder {reminder['id']}")
                else:
                    logger.warning(f"Failed to execute reminder {reminder['id']}")
        
        except Exception as e:
            logger.error(f"Error checking reminders: {str(e)}", exc_info=True)
    
    def _log_upcoming_reminders(self):
        """Log upcoming reminders in the next 24 hours."""
        try:
            reminders = get_all_reminders()
            if not reminders:
                logger.info("No reminders found")
                return
            
            upcoming = get_upcoming_reminders(reminders, hours_ahead=24)
            
            if not upcoming:
                logger.info("No upcoming reminders in the next 24 hours")
                return
            
            logger.info("=" * 70)
            logger.info(f"UPCOMING REMINDERS (Next 24 Hours): {len(upcoming)} reminder(s)")
            logger.info("=" * 70)
            
            for item in upcoming:
                reminder = item['reminder']
                hours = item['hours_remaining']
                minutes = item['minutes_remaining']
                next_time = item['next_occurrence'].strftime('%Y-%m-%d %H:%M:%S IST')
                
                # Format time remaining
                if hours > 0 and minutes > 0:
                    time_str = f"{hours} hour(s) and {minutes} minute(s)"
                elif hours > 0:
                    time_str = f"{hours} hour(s)"
                elif minutes > 0:
                    time_str = f"{minutes} minute(s)"
                else:
                    time_str = "less than a minute"
                
                logger.info(f"  • User: {reminder['user_name']}")
                logger.info(f"    Content: {reminder['content']}")
                logger.info(f"    Next occurrence: {next_time}")
                logger.info(f"    Time remaining: {time_str}")
                logger.info(f"    Repeat: {reminder.get('repeat_frequency', 'none')}")
                logger.info("")
            
            logger.info("=" * 70)
        
        except Exception as e:
            logger.error(f"Error logging upcoming reminders: {str(e)}", exc_info=True)


def main():
    """Main entry point for the reminder service."""
    # Get Twilio phone number from environment or use config default
    from_number = os.environ.get("TWILIO_FROM_NUMBER", TWILIO_FROM_NUMBER)
    
    # Get check interval from environment or use default
    check_interval = int(os.environ.get("REMINDER_CHECK_INTERVAL", "60"))
    
    service = ReminderService(from_number, check_interval)
    service.run()


if __name__ == "__main__":
    main()

