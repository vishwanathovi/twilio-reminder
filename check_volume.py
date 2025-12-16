#!/usr/bin/env python3
"""
Diagnostic script to check volume contents on Railway.
Run this to verify the volume mount and CSV files.
"""
import os
import sys

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src'))

from data_manager import DATA_DIR, REMINDERS_CSV, USERS_CSV

print("=" * 70)
print("VOLUME DIAGNOSTICS")
print("=" * 70)
print(f"DATA_DIR: {DATA_DIR}")
print(f"DATA_DIR exists: {os.path.exists(DATA_DIR)}")
print()

if os.path.exists(DATA_DIR):
    print(f"Contents of {DATA_DIR}:")
    try:
        files = os.listdir(DATA_DIR)
        for file in files:
            filepath = os.path.join(DATA_DIR, file)
            size = os.path.getsize(filepath) if os.path.isfile(filepath) else 0
            print(f"  - {file} ({size} bytes)")
    except Exception as e:
        print(f"  Error: {e}")
else:
    print(f"ERROR: {DATA_DIR} does not exist!")
print()

print(f"REMINDERS_CSV: {REMINDERS_CSV}")
print(f"REMINDERS_CSV exists: {os.path.exists(REMINDERS_CSV)}")
if os.path.exists(REMINDERS_CSV):
    with open(REMINDERS_CSV, 'r') as f:
        content = f.read()
        print(f"Content ({len(content)} chars):")
        print(content[:500])  # First 500 chars
print()

print(f"USERS_CSV: {USERS_CSV}")
print(f"USERS_CSV exists: {os.path.exists(USERS_CSV)}")
if os.path.exists(USERS_CSV):
    with open(USERS_CSV, 'r') as f:
        content = f.read()
        print(f"Content ({len(content)} chars):")
        print(content[:500])  # First 500 chars
print("=" * 70)

