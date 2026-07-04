"""
Utility functions for Wayfarer travel concierge
"""
import re
import logging
import html
import os
from typing import Dict, Optional, Tuple, List, Any
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


def sanitize_html(text: str) -> str:
    """
    Sanitize HTML content to prevent XSS attacks.

    Args:
        text: Input text that may contain HTML

    Returns:
        HTML-escaped string safe for display
    """
    if not text:
        return ""
    return html.escape(str(text))


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename to be safe for filesystem usage.

    Args:
        filename: Original filename

    Returns:
        Sanitized filename safe for filesystem use
    """
    if not filename:
        return "unnamed"

    # Remove or replace unsafe characters
    filename = re.sub(r'[<>:"/\\|?*\x00-\x1f]', '_', filename)
    # Remove leading/trailing spaces and dots
    filename = filename.strip(' .')
    # Limit length
    if len(filename) > 255:
        name, ext = os.path.splitext(filename)
        filename = name[:255-len(ext)] + ext

    return filename or "unnamed"


def validate_email(email: str) -> bool:
    """
    Validate email address format.

    Args:
        email: Email address to validate

    Returns:
        True if email format is valid, False otherwise
    """
    if not email or not isinstance(email, str):
        return False

    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email.strip()))


def sanitize_phone_number(phone: str) -> str:
    """
    Sanitize and format phone number.

    Args:
        phone: Phone number string

    Returns:
        Sanitized phone number with only digits and +
    """
    if not phone:
        return ""

    # Keep only digits, +, -, (, ), and spaces
    cleaned = re.sub(r'[^\d+\-\(\)\s]', '', phone)
    # Remove extra whitespace
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    return cleaned


def validate_currency_code(currency: str) -> bool:
    """
    Validate ISO 4217 currency code.

    Args:
        currency: Currency code to validate

    Returns:
        True if valid currency code, False otherwise
    """
    if not currency or not isinstance(currency, str):
        return False

    # ISO 4217 currency codes are 3 uppercase letters
    return bool(re.fullmatch(r'[A-Z]{3}', currency.upper()))


def format_phone_number(phone: str, country_code: str = "US") -> str:
    """
    Format phone number according to country conventions.

    Args:
        phone: Phone number to format
        country_code: ISO country code (default: US)

    Returns:
        Formatted phone number string
    """
    if not phone:
        return ""

    # Extract digits only
    digits = re.sub(r'\D', '', phone)

    if country_code.upper() == "US" and len(digits) == 10:
        # US format: (XXX) XXX-XXXX
        return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
    elif country_code.upper() == "IN" and len(digits) == 10:
        # India format: +91 XXXXX-XXXXX
        return f"+91 {digits[:5]}-{digits[5:]}"
    else:
        # Return as-is with country prefix if available
        if not digits.startswith('1') and len(digits) == 10 and country_code.upper() == "US":
            return f"+1 ({digits[:3]}) {digits[3:6]}-{digits[6:]}"
        return phone


def extract_names_from_text(text: str) -> List[str]:
    """
    Extract potential person names from text using basic heuristics.
    Note: This is a simple implementation. For production, consider using NER libraries.

    Args:
        text: Input text to search for names

    Returns:
        List of potential names found
    """
    if not text:
        return []

    # Simple pattern for capitalized words that might be names
    # This is a basic implementation - consider using spaCy or NLTK for production
    pattern = r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b'
    potential_names = re.findall(pattern, text)

    # Filter out common non-name words
    common_words = {
        'The', 'This', 'That', 'And', 'Or', 'But', 'In', 'On', 'At', 'To', 'For',
        'Of', 'With', 'By', 'From', 'Up', 'About', 'Into', 'Over', 'After',
        'Before', 'Under', 'Above', 'Below', 'Between', 'Through', 'During',
        'Before', 'After', 'Above', 'Below', 'Under', 'Over', 'Against',
        'Between', 'Into', 'Through', 'Throughout', 'During', 'Throughout'
    }

    filtered_names = [name for name in potential_names
                     if name not in common_words and len(name) > 1]

    return filtered_names[:5]  # Limit to 5 names to avoid noise


def is_travel_related_query(text: str) -> bool:
    """
    Heuristic to determine if a query is travel-related.

    Args:
        text: Input query text

    Returns:
        True if query appears to be travel-related, False otherwise
    """
    if not text:
        return False

    text_lower = text.lower()

    # Travel-related keywords
    travel_keywords = {
        'flight', 'fly', 'airline', 'airport', 'hotel', 'stay', 'accommodation',
        'vacation', 'trip', 'travel', 'journey', 'tour', 'destination', 'city',
        'country', 'visit', 'destination', 'itinerary', 'passport', 'visa',
        'luggage', 'baggage', 'passport', 'customs', 'immigration', 'resort',
        'vacation', 'holiday', 'cruise', 'sailing', 'drive', 'road trip',
        'backpacking', 'hiking', 'camping', 'safari', 'tourist', 'sightseeing',
        'museum', 'beach', 'mountain', 'ski', 'resort', 'spa', 'restaurant',
        'food', 'cuisine', 'local', 'guide', 'tour', 'excursion', 'ticket',
        'booking', 'reservation', 'check-in', 'check-out', 'suite', 'room'
    }

    # Check if any travel keywords are present
    words = set(re.findall(r'\b\w+\b', text_lower))
    return bool(words & travel_keywords)


class StructuredLogger:
    """
    Structured logger for adding contextual information to log entries.
    """

    def __init__(self, name: str = "wayfarer"):
        self.logger = logging.getLogger(name)
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)

    def info(self, message: str, **kwargs):
        """Log info message with structured context."""
        if kwargs:
            message = f"{message} | {self._format_context(kwargs)}"
        self.logger.info(message)

    def warning(self, message: str, **kwargs):
        """Log warning message with structured context."""
        if kwargs:
            message = f"{message} | {self._format_context(kwargs)}"
        self.logger.warning(message)

    def error(self, message: str, **kwargs):
        """Log error message with structured context."""
        if kwargs:
            message = f"{message} | {self._format_context(kwargs)}"
        self.logger.error(message)

    def debug(self, message: str, **kwargs):
        """Log debug message with structured context."""
        if kwargs:
            message = f"{message} | {self._format_context(kwargs)}"
        self.logger.debug(message)

    def _format_context(self, context: Dict[str, Any]) -> str:
        """Format context dictionary as a string."""
        # Filter out None values and format as key=value pairs
        filtered = {k: v for k, v in context.items() if v is not None}
        return " ".join([f"{k}={v}" for k, v in filtered.items()])


def get_structured_logger(name: str = "wayfarer") -> StructuredLogger:
    """
    Get a structured logger instance.

    Args:
        name: Logger name

    Returns:
        StructuredLogger instance
    """
    return StructuredLogger(name)