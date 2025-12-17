"""
Scheduler Module
Handles checking which reminders should be executed based on date, time, and repeat frequency.
"""

import logging
from datetime import datetime, timedelta
from typing import List, Dict
from dateutil import parser
from config import IST, get_ist_now

logger = logging.getLogger(__name__)


def is_reminder_due(reminder: Dict[str, str]) -> bool:
    """
    Check if a reminder should be executed now.
    Returns True if the reminder is due, False otherwise.
    All times are in IST.
    """
    # Get current time in IST
    current_time = get_ist_now()

    logger.info(f"[is_reminder_due] Checking reminder for {reminder.get('user_name')}")
    logger.info(
        f"[is_reminder_due] Current IST: {current_time.strftime('%Y-%m-%d %H:%M:%S %Z')}"
    )

    # Parse reminder date and time (assumed to be in IST)
    try:
        reminder_date = datetime.strptime(reminder["date"], "%Y-%m-%d").date()
        reminder_time = datetime.strptime(reminder["time"], "%H:%M").time()
        # Create datetime in IST timezone
        reminder_datetime = IST.localize(datetime.combine(reminder_date, reminder_time))
        logger.info(
            f"[is_reminder_due] Reminder scheduled: {reminder_datetime.strftime('%Y-%m-%d %H:%M:%S %Z')}"
        )
    except (ValueError, KeyError) as e:
        logger.error(f"[is_reminder_due] Error parsing date/time: {e}")
        return False

    repeat_frequency = reminder.get("repeat_frequency", "none").lower()
    status = reminder.get("status", "pending")
    last_called_str = reminder.get("last_called", "")

    logger.info(
        f"[is_reminder_due] Repeat: {repeat_frequency}, Status: {status}, Last called: {last_called_str or 'Never'}"
    )

    # One-time reminders
    if repeat_frequency == "none":
        # Check if date/time has passed and status is still pending
        if reminder_datetime <= current_time and status == "pending":
            logger.info(
                f"[is_reminder_due] ONE-TIME reminder is DUE (scheduled time passed, status pending)"
            )
            return True
        logger.info(f"[is_reminder_due] ONE-TIME reminder NOT due")
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
            logger.info(
                f"[is_reminder_due] Last called: {last_called.strftime('%Y-%m-%d %H:%M:%S %Z')}"
            )
        except (ValueError, TypeError):
            # If last_called is invalid, treat as never called
            last_called = None
            logger.info(
                f"[is_reminder_due] Invalid last_called, treating as never called"
            )
    else:
        last_called = None
        logger.info(f"[is_reminder_due] Never called before")

    # If never called, check if TODAY's scheduled time has passed (not the original date)
    if last_called is None:
        scheduled_time_today = IST.localize(
            datetime.combine(current_time.date(), reminder_datetime.time())
        )
        logger.info(
            f"[is_reminder_due] Today's scheduled time: {scheduled_time_today.strftime('%Y-%m-%d %H:%M:%S %Z')}"
        )
        if scheduled_time_today <= current_time:
            logger.info(
                f"[is_reminder_due] REPEAT reminder (never called) is DUE - today's scheduled time has passed"
            )
            return True
        logger.info(
            f"[is_reminder_due] REPEAT reminder (never called) NOT due - today's scheduled time in future"
        )
        return False

    # Calculate time difference
    time_diff = current_time - last_called
    logger.info(f"[is_reminder_due] Time since last call: {time_diff}")

    # Check repeat frequency
    if repeat_frequency == "daily":
        # Check if at least 1 day has passed since last call
        if time_diff >= timedelta(days=1):
            # Check if scheduled time today has passed
            scheduled_time_today = IST.localize(
                datetime.combine(current_time.date(), reminder_datetime.time())
            )
            logger.info(
                f"[is_reminder_due] Scheduled time today: {scheduled_time_today.strftime('%H:%M:%S')}"
            )
            if current_time >= scheduled_time_today:
                logger.info(
                    f"[is_reminder_due] DAILY reminder is DUE - 1 day passed and scheduled time today has passed"
                )
                return True
            logger.info(
                f"[is_reminder_due] DAILY reminder NOT due - scheduled time today not yet passed"
            )
        else:
            logger.info(
                f"[is_reminder_due] DAILY reminder NOT due - less than 1 day since last call"
            )
        return False

    elif repeat_frequency == "weekly":
        # Check if at least 7 days have passed since last call
        if time_diff >= timedelta(days=7):
            # Check if scheduled time today has passed
            scheduled_time_today = IST.localize(
                datetime.combine(current_time.date(), reminder_datetime.time())
            )
            if current_time >= scheduled_time_today:
                logger.info(f"[is_reminder_due] WEEKLY reminder is DUE")
                return True
        logger.info(f"[is_reminder_due] WEEKLY reminder NOT due")
        return False

    elif repeat_frequency == "monthly":
        # Check if at least 30 days have passed since last call
        if time_diff >= timedelta(days=30):
            # Check if scheduled time today has passed
            scheduled_time_today = IST.localize(
                datetime.combine(current_time.date(), reminder_datetime.time())
            )
            if current_time >= scheduled_time_today:
                logger.info(f"[is_reminder_due] MONTHLY reminder is DUE")
                return True
        logger.info(f"[is_reminder_due] MONTHLY reminder NOT due")
        return False

    logger.info(f"[is_reminder_due] Unknown frequency, NOT due")
    return False


def get_due_reminders(reminders: List[Dict[str, str]]) -> List[Dict[str, str]]:
    """
    Filter reminders to get only those that are due now.
    """
    return [reminder for reminder in reminders if is_reminder_due(reminder)]


def get_upcoming_reminders(
    reminders: List[Dict[str, str]], hours_ahead: int = 24
) -> List[Dict[str, Dict[str, str]]]:
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

    logger.info(
        f"[get_upcoming] Current IST: {current_time.strftime('%Y-%m-%d %H:%M:%S %Z')}"
    )
    logger.info(
        f"[get_upcoming] Looking ahead {hours_ahead} hours until: {end_time.strftime('%Y-%m-%d %H:%M:%S %Z')}"
    )
    logger.info(f"[get_upcoming] Total reminders to check: {len(reminders)}")

    for reminder in reminders:
        try:
            logger.info(
                f"[get_upcoming] --- Checking reminder for {reminder.get('user_name')} ---"
            )

            reminder_date = datetime.strptime(reminder["date"], "%Y-%m-%d").date()
            reminder_time = datetime.strptime(reminder["time"], "%H:%M").time()
            reminder_datetime = IST.localize(
                datetime.combine(reminder_date, reminder_time)
            )

            logger.info(
                f"[get_upcoming] Reminder datetime: {reminder_datetime.strftime('%Y-%m-%d %H:%M:%S %Z')}"
            )

            repeat_frequency = reminder.get("repeat_frequency", "none").lower()
            last_called_str = reminder.get("last_called", "")

            logger.info(
                f"[get_upcoming] Repeat: {repeat_frequency}, Last called: {last_called_str or 'Never'}"
            )

            # Calculate next occurrence
            next_occurrence = None

            if repeat_frequency == "none":
                # One-time reminder
                if reminder_datetime > current_time and reminder_datetime <= end_time:
                    next_occurrence = reminder_datetime
                    logger.info(
                        f"[get_upcoming] ONE-TIME: Next occurrence set to {next_occurrence}"
                    )
                else:
                    logger.info(
                        f"[get_upcoming] ONE-TIME: Not in window (reminder_datetime > current: {reminder_datetime > current_time}, <= end: {reminder_datetime <= end_time})"
                    )
            else:
                # Repeat reminders - find next occurrence
                if last_called_str:
                    try:
                        last_called = parser.parse(last_called_str)
                        if last_called.tzinfo is None:
                            last_called = IST.localize(last_called)
                        else:
                            last_called = last_called.astimezone(IST)
                        logger.info(
                            f"[get_upcoming] Last called parsed: {last_called.strftime('%Y-%m-%d %H:%M:%S %Z')}"
                        )
                    except (ValueError, TypeError):
                        last_called = None
                        logger.info(f"[get_upcoming] Failed to parse last_called")
                else:
                    last_called = None

                # Start from today's scheduled time
                today_scheduled = IST.localize(
                    datetime.combine(current_time.date(), reminder_datetime.time())
                )
                logger.info(
                    f"[get_upcoming] Today's scheduled time: {today_scheduled.strftime('%Y-%m-%d %H:%M:%S %Z')}"
                )

                if repeat_frequency == "daily":
                    # If last called was today, next occurrence is always tomorrow
                    if last_called and last_called.date() == current_time.date():
                        next_occurrence = today_scheduled + timedelta(days=1)
                        logger.info(
                            f"[get_upcoming] DAILY: Called today, next is tomorrow: {next_occurrence}"
                        )
                    else:
                        # Next occurrence is today if time hasn't passed, otherwise tomorrow
                        if today_scheduled > current_time:
                            next_occurrence = today_scheduled
                            logger.info(
                                f"[get_upcoming] DAILY: Time hasn't passed, next is today: {next_occurrence}"
                            )
                        else:
                            next_occurrence = today_scheduled + timedelta(days=1)
                            logger.info(
                                f"[get_upcoming] DAILY: Time passed, next is tomorrow: {next_occurrence}"
                            )

                elif repeat_frequency == "weekly":
                    # Find next occurrence within 7 days
                    for days_offset in range(7):
                        candidate = today_scheduled + timedelta(days=days_offset)
                        if candidate > current_time:
                            # Check if enough time has passed since last call
                            if last_called is None or (
                                candidate - last_called
                            ) >= timedelta(days=7):
                                next_occurrence = candidate
                                break

                elif repeat_frequency == "monthly":
                    # Find next occurrence within 30 days
                    for days_offset in range(30):
                        candidate = today_scheduled + timedelta(days=days_offset)
                        if candidate > current_time:
                            # Check if enough time has passed since last call
                            if last_called is None or (
                                candidate - last_called
                            ) >= timedelta(days=30):
                                next_occurrence = candidate
                                break

                # If no last_called, use today if time hasn't passed
                if next_occurrence is None and last_called is None:
                    if today_scheduled > current_time:
                        next_occurrence = today_scheduled

            # If we found a next occurrence within the time window
            logger.info(f"[get_upcoming] Next occurrence calculated: {next_occurrence}")

            if (
                next_occurrence
                and next_occurrence <= end_time
                and next_occurrence > current_time
            ):
                time_diff = next_occurrence - current_time
                total_seconds = int(time_diff.total_seconds())
                hours_remaining = total_seconds // 3600
                minutes_remaining = (total_seconds % 3600) // 60

                logger.info(
                    f"[get_upcoming] ✓ ADDED to upcoming - in {hours_remaining}h {minutes_remaining}m"
                )

                upcoming.append(
                    {
                        "reminder": reminder,
                        "next_occurrence": next_occurrence,
                        "hours_remaining": hours_remaining,
                        "minutes_remaining": minutes_remaining,
                    }
                )
            else:
                if next_occurrence:
                    logger.info(
                        f"[get_upcoming] ✗ NOT added - next_occurrence ({next_occurrence}) not in window"
                    )
                    logger.info(
                        f"[get_upcoming]   <= end_time: {next_occurrence <= end_time}, > current_time: {next_occurrence > current_time}"
                    )
                else:
                    logger.info(
                        f"[get_upcoming] ✗ NOT added - no next_occurrence calculated"
                    )

        except (ValueError, KeyError) as e:
            logger.error(f"[get_upcoming] Error processing reminder: {e}")
            continue

    logger.info(f"[get_upcoming] Total upcoming reminders found: {len(upcoming)}")

    # Sort by next occurrence time
    upcoming.sort(key=lambda x: x["next_occurrence"])
    return upcoming
