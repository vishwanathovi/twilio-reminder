"""
Message Manager Module
Handles Twilio SMS messages and message status tracking.
"""

import os
import logging
from typing import Tuple
from twilio.rest import Client
from twilio.base.exceptions import TwilioException
from data_manager import get_user_by_name, update_reminder_status
from config import get_ist_now


# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Debug mode - set to True to skip actual Twilio messages
DEBUG_MODE = os.environ.get("DEBUG_MODE", "false").lower() == "true"


def get_twilio_client() -> Client:
    """Initialize and return Twilio client."""
    account_sid = os.environ.get("TWILIO_ACCOUNT_SID")
    auth_token = os.environ.get("TWILIO_AUTH_TOKEN")

    if not account_sid or not auth_token:
        raise ValueError(
            "TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN must be set in environment"
        )

    return Client(account_sid, auth_token)


def send_reminder_message(reminder: dict, from_number: str) -> Tuple[bool, str]:
    """
    Send a Twilio SMS message for a reminder.

    Args:
        reminder: Reminder dictionary with user_name and content
        from_number: Twilio phone number to send from (E.164 format)

    Returns:
        Tuple of (success: bool, message: str)
    """
    try:
        # Get user phone number
        user = get_user_by_name(reminder["user_name"])
        if not user:
            error_msg = f"User '{reminder['user_name']}' not found"
            logger.error(error_msg)
            return False, error_msg

        to_number = user["phone_number"]
        content = reminder.get("content", "")
        
        # Ensure newlines are properly handled (convert literal \n to actual newlines)
        if content:
            content = content.replace("\\n", "\n")

        # Log current IST time for debugging
        current_ist = get_ist_now()
        logger.info(
            f"[DEBUG] Current IST time: {current_ist.strftime('%Y-%m-%d %H:%M:%S %Z')}"
        )
        logger.info(
            f"[DEBUG] Reminder scheduled for: {reminder.get('date')} {reminder.get('time')}"
        )
        logger.info(f"[DEBUG] Repeat frequency: {reminder.get('repeat_frequency')}")
        logger.info(f"[DEBUG] Last called: {reminder.get('last_called', 'Never')}")

        # Debug mode - skip actual message
        if DEBUG_MODE:
            logger.info(
                f"[DEBUG MODE] Would send SMS to {to_number} with message: '{content}'"
            )
            logger.info(f"[DEBUG MODE] From: {from_number}")
            return True, "DEBUG MODE - Message simulated"

        # Initialize Twilio client
        client = get_twilio_client()

        # Send the SMS message
        logger.info(f"Sending SMS to {to_number} for reminder: {content[:50]}...")
        message = client.messages.create(body=content, to=to_number, from_=from_number)

        logger.info(f"Message sent successfully. Message SID: {message.sid}")
        return True, f"Message successful. SID: {message.sid}"

    except TwilioException as e:
        error_msg = f"Twilio error: {str(e)}"
        logger.error(error_msg)
        return False, error_msg
    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        logger.error(error_msg)
        return False, error_msg


def execute_reminder_message(reminder: dict, from_number: str) -> bool:
    """
    Execute a reminder via SMS: send the message and update status.

    Args:
        reminder: Reminder dictionary
        from_number: Twilio phone number to send from

    Returns:
        True if message was successful, False otherwise
    """
    success, message = send_reminder_message(reminder, from_number)

    # Update reminder status
    status = "completed" if success else "failed"
    last_called = get_ist_now().isoformat()

    update_reminder_status(reminder["id"], status, last_called)

    logger.info(
        f"Reminder {reminder['id']} updated: status={status}, message={message}"
    )

    return success
