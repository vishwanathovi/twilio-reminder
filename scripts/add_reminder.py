#!/usr/bin/env python3
"""
CLI script to add a new reminder.
"""
import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src'))

from data_manager import (
    add_reminder,
    validate_date,
    validate_time,
    validate_repeat_frequency,
    get_all_users
)


def main():
    """Interactive CLI to add a reminder."""
    print("Add New Reminder")
    print("=" * 50)
    
    # Show available users
    users = get_all_users()
    if not users:
        print("No users found. Please add users first using add_user.py")
        sys.exit(1)
    
    print("\nAvailable users:")
    for i, user in enumerate(users, 1):
        print(f"  {i}. {user['name']} ({user['phone_number']})")
    
    # Get user name
    print("\nEnter user name (or number from list):")
    user_input = input("> ").strip()
    
    # Check if input is a number
    if user_input.isdigit():
        user_index = int(user_input) - 1
        if 0 <= user_index < len(users):
            user_name = users[user_index]['name']
        else:
            print("Invalid user number")
            sys.exit(1)
    else:
        user_name = user_input
        # Verify user exists
        if not any(u['name'].lower() == user_name.lower() for u in users):
            print(f"User '{user_name}' not found")
            sys.exit(1)
    
    # Get date
    print("\nEnter date (YYYY-MM-DD):")
    date = input("> ").strip()
    if not validate_date(date):
        print("Invalid date format. Use YYYY-MM-DD")
        sys.exit(1)
    
    # Get time
    print("\nEnter time (HH:MM, 24-hour format):")
    time_str = input("> ").strip()
    if not validate_time(time_str):
        print("Invalid time format. Use HH:MM")
        sys.exit(1)
    
    # Get content
    print("\nEnter reminder content (text to speak/send):")
    content = input("> ").strip()
    if not content:
        print("Content cannot be empty")
        sys.exit(1)
    
    # Get repeat frequency
    print("\nEnter repeat frequency (daily/weekly/monthly/none):")
    repeat_frequency = input("> ").strip().lower()
    if not validate_repeat_frequency(repeat_frequency):
        print("Invalid repeat frequency. Use: daily, weekly, monthly, or none")
        sys.exit(1)
    
    # Get notification type
    print("\nEnter notification type (call/sms):")
    notification_type = input("> ").strip().lower()
    if notification_type not in ["call", "sms"]:
        print("Invalid notification type. Use: call or sms")
        sys.exit(1)
    
    # Add reminder
    reminder_id = add_reminder(user_name, date, time_str, content, repeat_frequency, notification_type)
    print(f"\n✓ Reminder added successfully!")
    print(f"  Reminder ID: {reminder_id}")
    print(f"  User: {user_name}")
    print(f"  Date: {date}")
    print(f"  Time: {time_str}")
    print(f"  Repeat: {repeat_frequency}")
    print(f"  Type: {notification_type}")


if __name__ == "__main__":
    main()

