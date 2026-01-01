#!/usr/bin/env python3
"""
CLI script to list all reminders.
"""
import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src'))

from data_manager import get_all_reminders
from datetime import datetime


def format_reminder(reminder: dict) -> str:
    """Format a reminder for display."""
    status = reminder.get('status', 'pending')
    last_called = reminder.get('last_called', 'Never')
    notification_type = reminder.get('notification_type', 'call')
    
    if last_called:
        try:
            dt = datetime.fromisoformat(last_called.replace('Z', '+00:00'))
            last_called = dt.strftime('%Y-%m-%d %H:%M:%S')
        except:
            pass
    
    return f"""
ID: {reminder['id']}
  User: {reminder['user_name']}
  Date: {reminder['date']}
  Time: {reminder['time']}
  Content: {reminder['content']}
  Repeat: {reminder.get('repeat_frequency', 'none')}
  Type: {notification_type.upper()}
  Status: {status}
  Last Called: {last_called}
  Created: {reminder.get('created_at', 'Unknown')}
"""


def main():
    """List all reminders."""
    reminders = get_all_reminders()
    
    if not reminders:
        print("No reminders found.")
        return
    
    print(f"Found {len(reminders)} reminder(s):")
    print("=" * 70)
    
    for reminder in reminders:
        print(format_reminder(reminder))
    
    # Summary by status
    status_counts = {}
    for reminder in reminders:
        status = reminder.get('status', 'pending')
        status_counts[status] = status_counts.get(status, 0) + 1
    
    print("\nSummary:")
    for status, count in status_counts.items():
        print(f"  {status}: {count}")


if __name__ == "__main__":
    main()

