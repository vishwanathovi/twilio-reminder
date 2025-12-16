"""
Call Manager Module
Handles Twilio API calls and call status tracking.
"""
import os
import logging
from typing import Tuple
from twilio.rest import Client
from twilio.base.exceptions import TwilioException
from data_manager import get_user_by_name, update_reminder_status


# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def get_twilio_client() -> Client:
    """Initialize and return Twilio client."""
    account_sid = os.environ.get("TWILIO_ACCOUNT_SID")
    auth_token = os.environ.get("TWILIO_AUTH_TOKEN")
    
    if not account_sid or not auth_token:
        raise ValueError("TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN must be set in environment")
    
    return Client(account_sid, auth_token)


def make_reminder_call(reminder: dict, from_number: str) -> Tuple[bool, str]:
    """
    Make a Twilio call for a reminder.
    
    Args:
        reminder: Reminder dictionary with user_name and content
        from_number: Twilio phone number to call from (E.164 format)
    
    Returns:
        Tuple of (success: bool, message: str)
    """
    try:
        # Get user phone number
        user = get_user_by_name(reminder['user_name'])
        if not user:
            error_msg = f"User '{reminder['user_name']}' not found"
            logger.error(error_msg)
            return False, error_msg
        
        to_number = user['phone_number']
        content = reminder.get('content', '')
        
        # Create TwiML response
        twiml = f'<Response><Say>{content}</Say></Response>'
        
        # Initialize Twilio client
        client = get_twilio_client()
        
        # Make the call
        logger.info(f"Making call to {to_number} for reminder: {content[:50]}...")
        call = client.calls.create(
            twiml=twiml,
            to=to_number,
            from_=from_number
        )
        
        logger.info(f"Call initiated successfully. Call SID: {call.sid}")
        return True, f"Call successful. SID: {call.sid}"
        
    except TwilioException as e:
        error_msg = f"Twilio error: {str(e)}"
        logger.error(error_msg)
        return False, error_msg
    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        logger.error(error_msg)
        return False, error_msg


def execute_reminder(reminder: dict, from_number: str) -> bool:
    """
    Execute a reminder: make the call and update status.
    
    Args:
        reminder: Reminder dictionary
        from_number: Twilio phone number to call from
    
    Returns:
        True if call was successful, False otherwise
    """
    from datetime import datetime
    
    success, message = make_reminder_call(reminder, from_number)
    
    # Update reminder status
    status = 'completed' if success else 'failed'
    last_called = datetime.now().isoformat()
    
    update_reminder_status(reminder['id'], status, last_called)
    
    logger.info(f"Reminder {reminder['id']} updated: status={status}, message={message}")
    
    return success

