#!/usr/bin/env python3
"""
CLI script to list all users.
"""
import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src'))

from data_manager import get_all_users


def main():
    """List all users."""
    users = get_all_users()
    
    if not users:
        print("No users found.")
        return
    
    print(f"Found {len(users)} user(s):")
    print("=" * 50)
    
    for i, user in enumerate(users, 1):
        print(f"{i}. {user['name']}")
        print(f"   Phone: {user['phone_number']}\n")


if __name__ == "__main__":
    main()

