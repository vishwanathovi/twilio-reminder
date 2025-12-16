"""
Scheduler Module
Handles checking which reminders should be executed based on date, time, and repeat frequency.
"""
from datetime import datetime, timedelta
from typing import List, Dict
from dateutil import parser


def is_reminder_due(reminder: Dict[str, str]) -> bool:
    """
    Check if a reminder should be executed now.
    Returns True if the reminder is due, False otherwise.
    """
    current_time = datetime.now()
    
    # Parse reminder date and time
    try:
        reminder_date = datetime.strptime(reminder['date'], '%Y-%m-%d').date()
        reminder_time = datetime.strptime(reminder['time'], '%H:%M').time()
        reminder_datetime = datetime.combine(reminder_date, reminder_time)
    except (ValueError, KeyError):
        return False
    
    repeat_frequency = reminder.get('repeat_frequency', 'none').lower()
    status = reminder.get('status', 'pending')
    last_called_str = reminder.get('last_called', '')
    
    # One-time reminders
    if repeat_frequency == 'none':
        # Check if date/time has passed and status is still pending
        if reminder_datetime <= current_time and status == 'pending':
            return True
        return False
    
    # Repeat reminders - check if enough time has passed since last call
    if last_called_str:
        try:
            last_called = parser.parse(last_called_str)
        except (ValueError, TypeError):
            # If last_called is invalid, treat as never called
            last_called = None
    else:
        last_called = None
    
    # If never called, check if the initial scheduled time has passed
    if last_called is None:
        if reminder_datetime <= current_time:
            return True
        return False
    
    # Calculate time difference
    time_diff = current_time - last_called
    
    # Check repeat frequency
    if repeat_frequency == 'daily':
        # Check if at least 1 day has passed since last call
        if time_diff >= timedelta(days=1):
            # Check if scheduled time today has passed
            scheduled_time_today = datetime.combine(current_time.date(), reminder_datetime.time())
            if current_time >= scheduled_time_today:
                return True
        return False
    
    elif repeat_frequency == 'weekly':
        # Check if at least 7 days have passed since last call
        if time_diff >= timedelta(days=7):
            # Check if scheduled time today has passed (or within same day of week)
            scheduled_time_today = datetime.combine(current_time.date(), reminder_datetime.time())
            if current_time >= scheduled_time_today:
                return True
        return False
    
    elif repeat_frequency == 'monthly':
        # Check if at least 30 days have passed since last call
        if time_diff >= timedelta(days=30):
            # Check if scheduled time today has passed
            scheduled_time_today = datetime.combine(current_time.date(), reminder_datetime.time())
            if current_time >= scheduled_time_today:
                return True
        return False
    
    return False


def get_due_reminders(reminders: List[Dict[str, str]]) -> List[Dict[str, str]]:
    """
    Filter reminders to get only those that are due now.
    """
    return [reminder for reminder in reminders if is_reminder_due(reminder)]

