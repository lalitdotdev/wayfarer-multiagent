"""
Tests for utility functions
"""
import unittest
from utils import (
    extract_iata_codes,
    validate_iata_code,
    extract_dates_from_text,
    extract_travel_dates,
    format_currency,
    format_duration,
    validate_date_range,
    calculate_trip_duration,
    extract_travel_duration,
    clean_travel_text,
    setup_logging
)


class TestUtils(unittest.TestCase):

    def test_extract_iata_codes(self):
        """Test IATA code extraction from text"""
        # Test with two codes
        result = extract_iata_codes("Fly from JFK to LAX")
        self.assertEqual(result['departure'], 'JFK')
        self.assertEqual(result['arrival'], 'LAX')

        # Test with one code
        result = extract_iata_codes("Heading to JFK")
        self.assertEqual(result['departure'], 'JFK')
        self.assertNotIn('arrival', result)

        # Test with no codes
        result = extract_iata_codes("Going to Paris")
        self.assertEqual(result, {})

        # Test case insensitivity
        result = extract_iata_codes("fly from jfk to lax")
        self.assertEqual(result['departure'], 'JFK')
        self.assertEqual(result['arrival'], 'LAX')

    def test_validate_iata_code(self):
        """Test IATA code validation"""
        # Valid codes
        self.assertTrue(validate_iata_code("JFK"))
        self.assertTrue(validate_iata_code("lax"))  # Case insensitive
        self.assertTrue(validate_iata_code("CdG"))  # Mixed case

        # Invalid codes
        self.assertFalse(validate_iata_code("JFK1"))  # Too long
        self.assertFalse(validate_iata_code("JK"))   # Too short
        self.assertFalse(validate_iata_code("JFK1")) # Contains number
        self.assertFalse(validate_iata_code(""))     # Empty string
        self.assertFalse(validate_iata_code(None))   # None
        self.assertFalse(validate_iata_code("JFK LA")) # Space

    def test_extract_dates_from_text(self):
        """Test date extraction from text"""
        # Single date
        dates = extract_dates_from_text("Traveling on 2023-06-15")
        self.assertEqual(dates, ["2023-06-15"])

        # Multiple dates
        dates = extract_dates_from_text("Trip from 2023-06-15 to 2023-06-20")
        self.assertEqual(set(dates), {"2023-06-15", "2023-06-20"})

        # No dates
        dates = extract_dates_from_text("Going to Paris")
        self.assertEqual(dates, [])

        # Invalid dates (should be filtered out)
        dates = extract_dates_from_text("Invalid dates: 2023-13-45 and 2023-02-30")
        self.assertEqual(dates, [])

        # Valid date with invalid ones
        dates = extract_dates_from_text("Valid: 2023-06-15, Invalid: 2023-13-45")
        self.assertEqual(dates, ["2023-06-15"])

    def test_extract_travel_dates(self):
        """Test travel date extraction (departure/return)"""
        # Both dates present
        dep, ret = extract_travel_dates("Departing on 2023-06-15 and returning 2023-06-20")
        self.assertEqual(dep, "2023-06-15")
        self.assertEqual(ret, "2023-06-20")

        # Only departure
        dep, ret = extract_travel_dates("Leaving on 2023-06-15")
        self.assertEqual(dep, "2023-06-15")
        self.assertIsNone(ret)

        # Only return
        dep, ret = extract_travel_dates("Returning on 2023-06-20")
        self.assertIsNone(dep)
        self.assertEqual(ret, "2023-06-20")

        # No dates
        dep, ret = extract_travel_dates("Going to Paris")
        self.assertIsNone(dep)
        self.assertIsNone(ret)

        # Invalid dates should be ignored
        dep, ret = extract_travel_dates("Departing on 2023-13-45 and returning 2023-06-20")
        self.assertIsNone(dep)  # Invalid departure ignored
        self.assertEqual(ret, "2023-06-20")  # Valid return kept

    def test_format_currency(self):
        """Test currency formatting"""
        # Test default currency (INR)
        self.assertEqual(format_currency(1234.5), "₹1,234.50")
        self.assertEqual(format_currency(0), "₹0.00")
        self.assertEqual(format_currency(1000000), "₹1,000,000.00")

        # Test custom currency
        self.assertEqual(format_currency(100, "$"), "$100.00")
        self.assertEqual(format_currency(50.5, "€"), "€50.50")

    def test_format_duration(self):
        """Test duration formatting"""
        # Minutes only
        self.assertEqual(format_duration(0), "0m")
        self.assertEqual(format_duration(45), "45m")
        self.assertEqual(format_duration(59), "59m")

        # Hours only
        self.assertEqual(format_duration(60), "1h")
        self.assertEqual(format_duration(120), "2h")
        self.assertEqual(format_duration(180), "3h")

        # Hours and minutes
        self.assertEqual(format_duration(90), "1h 30m")
        self.assertEqual(format_duration(125), "2h 5m")
        self.assertEqual(format_duration(375), "6h 15m")

    def test_validate_date_range(self):
        """Test date range validation"""
        # Valid dates
        self.assertTrue(validate_date_range("2023-01-01", "2023-12-31"))
        self.assertTrue(validate_date_range("2023-06-15", "2023-06-15"))  # Same day

        # Invalid dates
        self.assertFalse(validate_date_range("2023-12-31", "2023-01-01"))  # End before start
        self.assertFalse(validate_date_range("not-a-date", "2023-01-01"))
        self.assertFalse(validate_date_range("2023-01-01", "not-a-date"))

    def test_calculate_trip_duration(self):
        """Test trip duration calculation"""
        # Normal case
        self.assertEqual(calculate_trip_duration("2023-06-15", "2023-06-20"), 6)  # 6 days inclusive

        # Same day
        self.assertEqual(calculate_trip_duration("2023-06-15", "2023-06-15"), 1)  # 1 day

        # Next day
        self.assertEqual(calculate_trip_duration("2023-06-15", "2023-06-16"), 2)  # 2 days

        # Invalid dates
        self.assertIsNone(calculate_trip_duration("2023-06-20", "2023-06-15"))  # End before start
        self.assertIsNone(calculate_trip_duration("not-a-date", "2023-06-15"))
        self.assertIsNone(calculate_trip_duration("2023-06-15", "not-a-date"))

    def test_extract_travel_duration(self):
        """Test travel duration extraction"""
        # Test various formats
        self.assertEqual(extract_travel_duration("7-day trip to Paris"), 7)
        self.assertEqual(extract_travel_duration("10 day vacation"), 10)
        self.assertEqual(extract_travel_duration("Stay for 5 days"), 5)
        self.assertEqual(extract_travel_duration("3 days trip"), 3)
        self.assertEqual(extract_travel_duration("Two week trip"), None)  # Written numbers not handled
        self.assertEqual(extract_travel_duration("Just visiting"), None)  # No duration

    def test_clean_travel_text(self):
        """Test text cleaning function"""
        # Normal text
        self.assertEqual(clean_travel_text("  Hello   World  "), "Hello World")

        # Text with special characters to remove
        self.assertEqual(clean_travel_text("Hello@#$%World"), "HelloWorld")
        self.assertEqual(clean_travel_text("Visit Paris!"), "Visit Paris")
        self.assertEqual(clean_travel_text("Flight #123 to NYC"), "Flight 123 to NYC")

        # Empty and None-like inputs
        self.assertEqual(clean_travel_text(""), "")
        self.assertEqual(clean_travel_text("   "), "")

    def test_setup_logging(self):
        """Test logging setup"""
        logger = setup_logging()
        self.assertIsInstance(logger, logging.Logger)
        self.assertEqual(logger.name, "wayfarer")
        self.assertGreaterEqual(len(logger.handlers), 1)


if __name__ == '__main__':
    unittest.main()