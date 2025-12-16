"""
Data Management Module
Handles reading and writing CSV files for reminders and users.
"""
import csv
import os
from datetime import datetime
from typing import List, Dict, Optional
import uuid


# Get the project root directory (parent of src/)
# Check for Railway volume mount first, then use relative path
if os.path.exists("/app/data"):
    # Railway volume is mounted at /app/data
    DATA_DIR = "/app/data"
else:
    # Local development - use relative path
    PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    DATA_DIR = os.path.join(PROJECT_ROOT, "data")

REMINDERS_CSV = os.path.join(DATA_DIR, "reminders.csv")
USERS_CSV = os.path.join(DATA_DIR, "users.csv")


def _ensure_data_dir():
    """Ensure data directory exists."""
    os.makedirs(DATA_DIR, exist_ok=True)


def _ensure_csv_exists(filename: str, headers: List[str]) -> None:
    """Create CSV file with headers if it doesn't exist."""
    _ensure_data_dir()
    if not os.path.exists(filename):
        with open(filename, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()


def _read_csv(filename: str) -> List[Dict[str, str]]:
    """Read all rows from a CSV file."""
    if not os.path.exists(filename):
        return []
    
    with open(filename, 'r', newline='') as f:
        reader = csv.DictReader(f)
        return list(reader)


def _write_csv(filename: str, headers: List[str], data: List[Dict[str, str]]) -> None:
    """Write data to a CSV file."""
    _ensure_data_dir()
    with open(filename, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(data)


# Reminders functions
def get_all_reminders() -> List[Dict[str, str]]:
    """Get all reminders from CSV."""
    headers = ['id', 'user_name', 'date', 'time', 'content', 'repeat_frequency', 'status', 'last_called', 'created_at']
    _ensure_csv_exists(REMINDERS_CSV, headers)
    return _read_csv(REMINDERS_CSV)


def add_reminder(user_name: str, date: str, time: str, content: str, repeat_frequency: str = 'none') -> str:
    """
    Add a new reminder to the CSV.
    Returns the generated reminder ID.
    """
    headers = ['id', 'user_name', 'date', 'time', 'content', 'repeat_frequency', 'status', 'last_called', 'created_at']
    _ensure_csv_exists(REMINDERS_CSV, headers)
    
    reminders = _read_csv(REMINDERS_CSV)
    reminder_id = str(uuid.uuid4())
    
    new_reminder = {
        'id': reminder_id,
        'user_name': user_name,
        'date': date,
        'time': time,
        'content': content,
        'repeat_frequency': repeat_frequency,
        'status': 'pending',
        'last_called': '',
        'created_at': datetime.now().isoformat()
    }
    
    reminders.append(new_reminder)
    _write_csv(REMINDERS_CSV, headers, reminders)
    return reminder_id


def update_reminder_status(reminder_id: str, status: str, last_called: Optional[str] = None) -> bool:
    """
    Update reminder status and optionally last_called timestamp.
    Returns True if reminder was found and updated, False otherwise.
    """
    headers = ['id', 'user_name', 'date', 'time', 'content', 'repeat_frequency', 'status', 'last_called', 'created_at']
    reminders = _read_csv(REMINDERS_CSV)
    
    updated = False
    for reminder in reminders:
        if reminder['id'] == reminder_id:
            reminder['status'] = status
            if last_called:
                reminder['last_called'] = last_called
            updated = True
            break
    
    if updated:
        _write_csv(REMINDERS_CSV, headers, reminders)
    
    return updated


def update_reminder(reminder_id: str, **kwargs) -> bool:
    """
    Update reminder fields (date, time, content, repeat_frequency, etc.).
    Returns True if reminder was found and updated, False otherwise.
    
    Args:
        reminder_id: ID of the reminder to update
        **kwargs: Fields to update (date, time, content, repeat_frequency, etc.)
    """
    headers = ['id', 'user_name', 'date', 'time', 'content', 'repeat_frequency', 'status', 'last_called', 'created_at']
    reminders = _read_csv(REMINDERS_CSV)
    
    updated = False
    for reminder in reminders:
        if reminder['id'] == reminder_id:
            # Update only the fields provided in kwargs
            for key, value in kwargs.items():
                if key in reminder:
                    reminder[key] = value
            updated = True
            break
    
    if updated:
        _write_csv(REMINDERS_CSV, headers, reminders)
    
    return updated


# Users functions
def get_all_users() -> List[Dict[str, str]]:
    """Get all users from CSV."""
    headers = ['name', 'phone_number']
    _ensure_csv_exists(USERS_CSV, headers)
    return _read_csv(USERS_CSV)


def get_user_by_name(name: str) -> Optional[Dict[str, str]]:
    """Get a user by name. Returns None if not found."""
    users = get_all_users()
    for user in users:
        if user['name'].lower() == name.lower():
            return user
    return None


def add_user(name: str, phone_number: str) -> bool:
    """
    Add a new user to the CSV.
    Returns True if added, False if user already exists.
    """
    headers = ['name', 'phone_number']
    _ensure_csv_exists(USERS_CSV, headers)
    
    # Check if user already exists
    if get_user_by_name(name):
        return False
    
    users = _read_csv(USERS_CSV)
    new_user = {
        'name': name,
        'phone_number': phone_number
    }
    users.append(new_user)
    _write_csv(USERS_CSV, headers, users)
    return True


def validate_phone_number(phone_number: str) -> bool:
    """Basic validation for phone number format (E.164)."""
    return phone_number.startswith('+') and phone_number[1:].isdigit() and len(phone_number) >= 10


def validate_date(date_str: str) -> bool:
    """Validate date format (YYYY-MM-DD)."""
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
        return True
    except ValueError:
        return False


def validate_time(time_str: str) -> bool:
    """Validate time format (HH:MM)."""
    try:
        datetime.strptime(time_str, '%H:%M')
        return True
    except ValueError:
        return False


def validate_repeat_frequency(frequency: str) -> bool:
    """Validate repeat frequency value."""
    return frequency.lower() in ['daily', 'weekly', 'monthly', 'none']

