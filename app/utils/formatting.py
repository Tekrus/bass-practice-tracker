"""
Formatting utilities for the bass practice application.
"""
from datetime import datetime

def format_duration(minutes):
    """Format duration in minutes to a human-readable string."""
    if minutes < 60:
        return f"{minutes}m"
    hours = minutes // 60
    remaining_minutes = minutes % 60
    if remaining_minutes == 0:
        return f"{hours}h"
    return f"{hours}h {remaining_minutes}m"

def format_percentage(value, total):
    """Format a ratio as a percentage string."""
    if total == 0:
        return "0%"
    percentage = (value / total) * 100
    return f"{percentage:.1f}%"

def format_date(dt, format_string="%b %d, %Y"):
    """Format a date or datetime object."""
    if not dt:
        return "N/A"
    if isinstance(dt, str):
        try:
            dt = datetime.strptime(dt, "%Y-%m-%d")
        except ValueError:
            return dt
    return dt.strftime(format_string)

def format_currency(amount):
    """Format a numerical value as currency (not really needed for this app, but common utility)."""
    return f"${amount:,.2f}"
