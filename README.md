# Twilio Reminder Call System

A Python-based reminder system that uses Twilio Voice API to make automated reminder calls based on scheduled dates, times, and repeat frequencies.

## Features

- Schedule reminder calls with specific date and time
- Support for repeat frequencies: daily, weekly, monthly, or one-time
- Store users and their phone numbers
- Track call status (pending, completed, failed)
- Background service that continuously monitors and executes reminders

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Twilio Credentials

Set your Twilio credentials as environment variables. You can either:

**Option A: Use the existing twilio.env file**
```bash
source twilio.env
```

**Option B: Set environment variables directly**
```bash
export TWILIO_ACCOUNT_SID='your_account_sid'
export TWILIO_AUTH_TOKEN='your_auth_token'
export TWILIO_FROM_NUMBER='+1234567890'  # Your Twilio phone number
```

### 3. Add Users

Before creating reminders, add users to the system:

```bash
python scripts/add_user.py
```

This will prompt you for:
- User name
- Phone number (E.164 format, e.g., +1234567890)

### 4. Add Reminders

Create reminders using:

```bash
python scripts/add_reminder.py
```

This will prompt you for:
- User name (or select from list)
- Date (YYYY-MM-DD)
- Time (HH:MM, 24-hour format)
- Content (text to speak in the call)
- Repeat frequency (daily/weekly/monthly/none)

## Usage

### Start the Reminder Service

Run the background service that monitors and executes reminders:

```bash
python run_service.py
```

The service will:
- Check for due reminders every 60 seconds (configurable via `REMINDER_CHECK_INTERVAL` environment variable)
- Make calls when reminders are due
- Update reminder status after each call attempt
- Run continuously until stopped (Ctrl+C)

### View Reminders

List all reminders:

```bash
python scripts/list_reminders.py
```

### View Users

List all users:

```bash
python scripts/list_users.py
```

## Data Files

The system uses two CSV files for data storage in the `data/` directory:

- **data/reminders.csv**: Stores all reminder entries
- **data/users.csv**: Stores user information (name and phone number)

These files are created automatically when you first add a reminder or user.

## Reminder Repeat Logic

- **none**: One-time reminder. Executes once when the scheduled date/time passes.
- **daily**: Executes every day at the scheduled time (checks if at least 1 day has passed since last call).
- **weekly**: Executes every week at the scheduled time (checks if at least 7 days have passed since last call).
- **monthly**: Executes every month at the scheduled time (checks if at least 30 days have passed since last call).

For repeat reminders, the system checks if the scheduled time today has passed and if enough time has elapsed since the last call.

## Configuration

Environment variables:

- `TWILIO_ACCOUNT_SID`: Your Twilio Account SID (required)
- `TWILIO_AUTH_TOKEN`: Your Twilio Auth Token (required)
- `TWILIO_FROM_NUMBER`: Your Twilio phone number (defaults to +16108313946 if not set)
- `REMINDER_CHECK_INTERVAL`: How often to check for due reminders in seconds (defaults to 60)

## File Structure

```
twilio-reminder-app/
├── call_test.py              # Original starter code
├── twilio.env                # Twilio credentials (source this file)
├── run_service.py            # Main entry point for reminder service
├── requirements.txt          # Python dependencies
├── README.md                 # This file
├── src/                      # Core application modules
│   ├── __init__.py
│   ├── data_manager.py       # CSV file operations
│   ├── scheduler.py          # Reminder scheduling logic
│   ├── call_manager.py       # Twilio API integration
│   └── reminder_service.py   # Main background service
├── scripts/                  # CLI utility scripts
│   ├── add_reminder.py       # Add new reminders
│   ├── add_user.py           # Add new users
│   ├── list_reminders.py     # List all reminders
│   └── list_users.py         # List all users
└── data/                     # Data storage
    ├── reminders.csv         # Reminder data
    └── users.csv             # User data
```

## Notes

- The system uses your local system timezone for scheduling
- Failed calls are marked as "failed" but repeat reminders will still attempt to call again on the next scheduled interval
- The service must be running continuously for reminders to be executed
- Phone numbers must be in E.164 format (e.g., +1234567890)

## Troubleshooting

- **No calls being made**: Ensure the reminder service is running and reminders are scheduled for the current time or past time
- **User not found errors**: Make sure users are added before creating reminders
- **Twilio errors**: Verify your Twilio credentials and phone number are correct
- **Permission errors**: Ensure the script has write permissions for the CSV files in the `data/` directory

