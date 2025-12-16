#!/usr/bin/env python3
"""
CLI script to add a new user.
"""
import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src'))

from data_manager import add_user, validate_phone_number, get_user_by_name


def main():
    """Interactive CLI to add a user."""
    print("Add New User")
    print("=" * 50)
    
    # Get user name
    print("\nEnter user name:")
    name = input("> ").strip()
    if not name:
        print("Name cannot be empty")
        sys.exit(1)
    
    # Check if user already exists
    if get_user_by_name(name):
        print(f"User '{name}' already exists")
        sys.exit(1)
    
    # Get phone number
    print("\nEnter phone number (E.164 format, e.g., +1234567890):")
    phone_number = input("> ").strip()
    if not validate_phone_number(phone_number):
        print("Invalid phone number format. Use E.164 format (e.g., +1234567890)")
        sys.exit(1)
    
    # Add user
    success = add_user(name, phone_number)
    if success:
        print(f"\n✓ User added successfully!")
        print(f"  Name: {name}")
        print(f"  Phone: {phone_number}")
    else:
        print("Failed to add user")
        sys.exit(1)


if __name__ == "__main__":
    main()

