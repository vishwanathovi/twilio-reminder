"""
Configuration constants for the reminder system.
"""
import pytz
from datetime import datetime

# Twilio phone number to use for all calls
TWILIO_FROM_NUMBER = "+16108313946"

# Timezone for all reminders (IST - Indian Standard Time)
IST = pytz.timezone('Asia/Kolkata')

def get_ist_now():
    """Get current datetime in IST timezone."""
    return datetime.now(IST)

