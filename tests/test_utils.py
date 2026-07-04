"""
Tests for utility functions
"""
import unittest
from utils import (
    extract_iata_codes,
    format_currency,
    validate_date_range,
    extract_travel_duration,
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

    def test_format_currency(self):
        """Test currency formatting"""
        # Test default currency (INR)
        self.assertEqual(format_currency(1234.5), "₹1,234.50")
        self.assertEqual(format_currency(0), "₹0.00")
        self.assertEqual(format_currency(1000000), "₹1,000,000.00")

        # Test custom currency
        self.assertEqual(format_currency(100, "$"), "$100.00")
        self.assertEqual(format_currency(50.5, "€"), "€50.50")

    def test_validate_date_range(self):
        """Test date range validation"""
        # Valid dates
        self.assertTrue(validate_date_range("2023-01-01", "2023-12-31"))
        self.assertTrue(validate_date_range("2023-06-15", "2023-06-15"))  # Same day

        # Invalid dates
        self.assertFalse(validate_date_range("2023-12-31", "2023-01-01"))  # End before start
        self.assertFalse(validate_date_range("not-a-date", "2023-01-01"))
        self.assertFalse(validate_date_range("2023-01-01", "not-a-date"))

    def test_extract_travel_duration(self):
        """Test travel duration extraction"""
        # Test various formats
        self.assertEqual(extract_travel_duration("7-day trip to Paris"), 7)
        self.assertEqual(extract_travel_duration("10 day vacation"), 10)
        self.assertEqual(extract_travel_duration("Stay for 5 days"), 5)
        self.assertEqual(extract_travel_duration("3 days trip"), 3)
        self.assertEqual(extract_travel_duration("Two week trip"), None)  # Written numbers not handled
        self.assertEqual(extract_travel_duration("Just visiting"), None)  # No duration

    def test_setup_logging(self):
        """Test logging setup"""
        logger = setup_logging()
        self.assertIsInstance(logger, logging.Logger)
        self.assertEqual(logger.name, "wayfarer")
        self.assertGreaterEqual(len(logger.handlers), 1)


if __name__ == '__main__':
    unittest.main()