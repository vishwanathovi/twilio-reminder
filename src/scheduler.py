"""
Scheduler Module
Handles checking which reminders should be executed based on date, time, and repeat frequency.
"""
from datetime import datetime, timedelta
from typing import List, Dict
from dateutil import parser
from config import IST, get_ist_now


def is_reminder_due(reminder: Dict[str, str]) -> bool:
    """
    Check if a reminder should be executed now.
    Returns True if the reminder is due, False otherwise.
    All times are in IST.
    """
    # Get current time in IST
    current_time = get_ist_now()
    
    # Parse reminder date and time (assumed to be in IST)
    try:
        reminder_date = datetime.strptime(reminder['date'], '%Y-%m-%d').date()
        reminder_time = datetime.strptime(reminder['time'], '%H:%M').time()
        # Create datetime in IST timezone
        reminder_datetime = IST.localize(datetime.combine(reminder_date, reminder_time))
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
            # Ensure last_called is timezone-aware (assume IST if naive)
            if last_called.tzinfo is None:
                last_called = IST.localize(last_called)
            else:
                # Convert to IST if it's in another timezone
                last_called = last_called.astimezone(IST)
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
            scheduled_time_today = IST.localize(datetime.combine(current_time.date(), reminder_datetime.time()))
            if current_time >= scheduled_time_today:
                return True
        return False
    
    elif repeat_frequency == 'weekly':
        # Check if at least 7 days have passed since last call
        if time_diff >= timedelta(days=7):
            # Check if scheduled time today has passed
            scheduled_time_today = IST.localize(datetime.combine(current_time.date(), reminder_datetime.time()))
            if current_time >= scheduled_time_today:
                return True
        return False
    
    elif repeat_frequency == 'monthly':
        # Check if at least 30 days have passed since last call
        if time_diff >= timedelta(days=30):
            # Check if scheduled time today has passed
            scheduled_time_today = IST.localize(datetime.combine(current_time.date(), reminder_datetime.time()))
            if current_time >= scheduled_time_today:
                return True
        return False
    
    return False


def get_due_reminders(reminders: List[Dict[str, str]]) -> List[Dict[str, str]]:
    """
    Filter reminders to get only those that are due now.
    """
    return [reminder for reminder in reminders if is_reminder_due(reminder)]


def get_upcoming_reminders(reminders: List[Dict[str, str]], hours_ahead: int = 24) -> List[Dict[str, Dict[str, str]]]:
    """
    Get reminders that are scheduled in the next N hours.
    Returns a list of dictionaries with reminder info and time remaining.
    
    Args:
        reminders: List of all reminders
        hours_ahead: Number of hours to look ahead (default: 24)
    
    Returns:
        List of dicts with keys: 'reminder', 'next_occurrence', 'hours_remaining', 'minutes_remaining'
    """
    current_time = get_ist_now()
    end_time = current_time + timedelta(hours=hours_ahead)
    upcoming = []
    
    for reminder in reminders:
        try:
            reminder_date = datetime.strptime(reminder['date'], '%Y-%m-%d').date()
            reminder_time = datetime.strptime(reminder['time'], '%H:%M').time()
            reminder_datetime = IST.localize(datetime.combine(reminder_date, reminder_time))
            
            repeat_frequency = reminder.get('repeat_frequency', 'none').lower()
            last_called_str = reminder.get('last_called', '')
            
            # Calculate next occurrence
            next_occurrence = None
            
            if repeat_frequency == 'none':
                # One-time reminder
                if reminder_datetime > current_time and reminder_datetime <= end_time:
                    next_occurrence = reminder_datetime
            else:
                # Repeat reminders - find next occurrence
                if last_called_str:
                    try:
                        last_called = parser.parse(last_called_str)
                        if last_called.tzinfo is None:
                            last_called = IST.localize(last_called)
                        else:
                            last_called = last_called.astimezone(IST)
                    except (ValueError, TypeError):
                        last_called = None
                else:
                    last_called = None
                
                # Start from today's scheduled time
                today_scheduled = IST.localize(datetime.combine(current_time.date(), reminder_datetime.time()))
                
                if repeat_frequency == 'daily':
                    # If last called was today, next occurrence is always tomorrow
                    if last_called and last_called.date() == current_time.date():
                        next_occurrence = today_scheduled + timedelta(days=1)
                    else:
                        # Next occurrence is today if time hasn't passed, otherwise tomorrow
                        if today_scheduled > current_time:
                            next_occurrence = today_scheduled
                        else:
                            next_occurrence = today_scheduled + timedelta(days=1)
                
                elif repeat_frequency == 'weekly':
                    # Find next occurrence within 7 days
                    for days_offset in range(7):
                        candidate = today_scheduled + timedelta(days=days_offset)
                        if candidate > current_time:
                            # Check if enough time has passed since last call
                            if last_called is None or (candidate - last_called) >= timedelta(days=7):
                                next_occurrence = candidate
                                break
                
                elif repeat_frequency == 'monthly':
                    # Find next occurrence within 30 days
                    for days_offset in range(30):
                        candidate = today_scheduled + timedelta(days=days_offset)
                        if candidate > current_time:
                            # Check if enough time has passed since last call
                            if last_called is None or (candidate - last_called) >= timedelta(days=30):
                                next_occurrence = candidate
                                break
                
                # If no last_called, use today if time hasn't passed
                if next_occurrence is None and last_called is None:
                    if today_scheduled > current_time:
                        next_occurrence = today_scheduled
            
            # If we found a next occurrence within the time window
            if next_occurrence and next_occurrence <= end_time and next_occurrence > current_time:
                time_diff = next_occurrence - current_time
                total_seconds = int(time_diff.total_seconds())
                hours_remaining = total_seconds // 3600
                minutes_remaining = (total_seconds % 3600) // 60
                
                upcoming.append({
                    'reminder': reminder,
                    'next_occurrence': next_occurrence,
                    'hours_remaining': hours_remaining,
                    'minutes_remaining': minutes_remaining
                })
        
        except (ValueError, KeyError) as e:
            # Skip invalid reminders
            continue
    
    # Sort by next occurrence time
    upcoming.sort(key=lambda x: x['next_occurrence'])
    return upcoming

