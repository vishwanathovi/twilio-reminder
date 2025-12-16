#!/usr/bin/env python3
"""
Main entry point for running the reminder service.
"""
import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src'))

from reminder_service import main

if __name__ == "__main__":
    main()

