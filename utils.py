"""
Utility functions for Wayfarer travel concierge
"""
import re
import logging
from typing import Dict, Optional
from datetime import datetime


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