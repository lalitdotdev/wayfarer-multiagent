"""
Utility functions for Wayfarer travel concierge
"""
import re
import logging
from typing import Dict, Optional, Tuple, List
from datetime import datetime, timedelta


def extract_iata_codes(text: str) -> Dict[str, str]:
    """
    Extract IATA airport codes from text.

    Args:
        text: Input text to search for IATA codes

    Returns:
        Dictionary with 'departure' and/or 'arrival' keys containing IATA codes
    """
    # Look for patterns like "from XXX to YYY" or "XXX to YYY"
    pattern = r'\b([A-Z]{3})\s*(?:to|[-])\s*([A-Z]{3})\b'
    match = re.search(pattern, text.upper())

    if match:
        return {
            'departure': match.group(1),
            'arrival': match.group(2)
        }

    # Look for single codes in common contexts
    single_pattern = r'(?:to|at|in|going\s+to|heading\s+to)\s+([A-Z]{3})\b'
    match = re.search(single_pattern, text.upper())
    if match:
        return {'arrival': match.group(1)}

    single_pattern = r'(?:from|departing\s+from|leaving\s+from)\s+([A-Z]{3})\b'
    match = re.search(single_pattern, text.upper())
    if match:
        return {'departure': match.group(1)}

    return {}


def validate_iata_code(code: str) -> bool:
    """
    Validate if a string is a valid IATA airport code.

    Args:
        code: String to validate

    Returns:
        True if valid IATA code, False otherwise
    """
    if not code or not isinstance(code, str):
        return False
    return bool(re.fullmatch(r'[A-Z]{3}', code.upper()))


def extract_dates_from_text(text: str) -> List[str]:
    """
    Extract potential date strings in YYYY-MM-DD format from text.

    Args:
        text: Input text to search for dates

    Returns:
        List of date strings found in YYYY-MM-DD format
    """
    # Pattern for YYYY-MM-DD dates
    pattern = r'\b(\d{4}-\d{2}-\d{2})\b'
    matches = re.findall(pattern, text)

    # Validate that they are actually valid dates
    valid_dates = []
    for date_str in matches:
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
            valid_dates.append(date_str)
        except ValueError:
            continue  # Skip invalid dates like 2023-13-45

    return list(set(valid_dates))  # Remove duplicates


def extract_travel_dates(text: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Extract departure and return dates from travel-related text.
    Looks for patterns like "departing on 2023-06-15 returning 2023-06-22".

    Args:
        text: Input text to search for travel dates

    Returns:
        Tuple of (departure_date, return_date) as strings in YYYY-MM-DD format,
        or None if not found
    """
    # Look for departure/return patterns
    dep_pattern = r'(?:depart|departing|leave|leaving|from|outbound).*?(\d{4}-\d{2}-\d{2})'
    ret_pattern = r'(?:return|returning|back|arrive|arriving|to|inbound).*?(\d{4}-\d{2}-\d{2})'

    dep_match = re.search(dep_pattern, text, re.IGNORECASE)
    ret_match = re.search(ret_pattern, text, re.IGNORECASE)

    departure_date = None
    return_date = None

    if dep_match:
        try:
            datetime.strptime(dep_match.group(1), "%Y-%m-%d")
            departure_date = dep_match.group(1)
        except ValueError:
            pass

    if ret_match:
        try:
            datetime.strptime(ret_match.group(1), "%Y-%m-%d")
            return_date = ret_match.group(1)
        except ValueError:
            pass

    return departure_date, return_date


def format_currency(amount: float, currency_symbol: str = "₹") -> str:
    """
    Format a number as currency.

    Args:
        amount: Amount to format
        currency_symbol: Currency symbol to use (default: Indian Rupee)

    Returns:
        Formatted currency string
    """
    return f"{currency_symbol}{amount:,.2f}"


def format_duration(minutes: int) -> str:
    """
    Format duration in minutes to a human-readable string.

    Args:
        minutes: Duration in minutes

    Returns:
        Formatted duration string (e.g., "2h 30m", "5h", "45m")
    """
    if minutes < 0:
        return "0m"

    hours = minutes // 60
    mins = minutes % 60

    if hours == 0:
        return f"{mins}m"
    elif mins == 0:
        return f"{hours}h"
    else:
        return f"{hours}h {mins}m"


def validate_date_range(start_date: str, end_date: str) -> bool:
    """
    Validate that start_date is before or equal to end_date.

    Args:
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format

    Returns:
        True if valid date range, False otherwise
    """
    try:
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
        return start <= end
    except ValueError:
        return False


def calculate_trip_duration(start_date: str, end_date: str) -> Optional[int]:
    """
    Calculate the number of days between two dates (inclusive).

    Args:
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format

    Returns:
        Number of days in the trip (inclusive), or None if invalid dates
    """
    try:
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
        if start > end:
            return None
        # Add 1 to make it inclusive (e.g., same day = 1 day)
        return (end - start).days + 1
    except ValueError:
        return None


def extract_travel_duration(text: str) -> Optional[int]:
    """
    Extract trip duration in days from text.

    Args:
        text: Input text to search for duration

    Returns:
        Number of days if found, None otherwise
    """
    # Patterns like "7-day", "5 day", "3 days", etc.
    pattern = r'(\d+)\s*-?\s*day'
    match = re.search(pattern, text.lower())
    if match:
        return int(match.group(1))

    # Pattern like "week"
    if re.search(r'week', text.lower()):
        # Assume 1 week = 7 days for simplicity
        week_match = re.search(r'(\d+)\s*week', text.lower())
        if week_match:
            return int(week_match.group(1)) * 7
        return 7  # Default 1 week

    return None


def clean_travel_text(text: str) -> str:
    """
    Clean and normalize travel-related text input.

    Args:
        text: Raw input text

    Returns:
        Cleaned text string
    """
    if not text:
        return ""

    # Remove extra whitespace
    cleaned = " ".join(text.split())

    # Remove special characters that might cause issues
    # Keep letters, numbers, spaces, and basic punctuation
    cleaned = re.sub(r'[^\w\s\-.,!?:()\'"@#$%&*+=/]', '', cleaned)

    return cleaned.strip()


def setup_logging(log_level: int = logging.INFO) -> logging.Logger:
    """
    Set up logging configuration for the application.

    Args:
        log_level: Logging level (default: INFO)

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger("wayfarer")
    logger.setLevel(log_level)

    # Avoid adding handlers if they already exist
    if not logger.handlers:
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)

        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(formatter)

        logger.addHandler(console_handler)

    return logger