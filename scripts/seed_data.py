#!/usr/bin/env python3
"""
Seed script to initialize the Railway volume with reminder and user data.
Run this once after deployment to populate the volume.
"""
import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src'))

from data_manager import add_user, add_reminder, get_all_users, get_all_reminders

print("=" * 70)
print("SEEDING DATA TO VOLUME")
print("=" * 70)

# Add users
print("\nAdding users...")
users_to_add = [
    ("Vishwa", "+919743911883"),
    ("Kavya", "+919590425258"),
]

for name, phone in users_to_add:
    try:
        success = add_user(name, phone)
        if success:
            print(f"  ✓ Added user: {name} ({phone})")
        else:
            print(f"  - User already exists: {name}")
    except Exception as e:
        print(f"  ✗ Error adding user {name}: {e}")

# Add reminders
print("\nAdding reminders...")
from datetime import datetime
today = datetime.now().strftime('%Y-%m-%d')

reminders_to_add = [
    ("Vishwa", today, "21:00", "Take your tablet", "daily", "call"),
]

for user, date, time, content, frequency, notification_type in reminders_to_add:
    try:
        reminder_id = add_reminder(user, date, time, content, frequency, notification_type)
        print(f"  ✓ Added reminder for {user}: {content} at {time} ({frequency}, {notification_type})")
        print(f"    ID: {reminder_id}")
    except Exception as e:
        print(f"  ✗ Error adding reminder: {e}")

# Verify
print("\n" + "=" * 70)
print("VERIFICATION")
print("=" * 70)

users = get_all_users()
print(f"\nUsers in database: {len(users)}")
for user in users:
    print(f"  - {user['name']}: {user['phone_number']}")

reminders = get_all_reminders()
print(f"\nReminders in database: {len(reminders)}")
for r in reminders:
    print(f"  - {r['user_name']}: {r['content']} at {r['time']} ({r['repeat_frequency']})")

print("\n" + "=" * 70)
print("SEEDING COMPLETE")
print("=" * 70)

