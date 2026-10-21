"""Unit tests for OSINT Phone Intelligence Module"""
import unittest
from modules.osint_phone.parser import parse_phone_number
from modules.osint_phone.footprint import generate_osint_dorks


class TestOSINTPhone(unittest.TestCase):
    def test_parse_indonesian_number(self):
        meta = parse_phone_number("+628123456789")
        self.assertTrue(meta.is_valid)
        self.assertEqual(meta.country_code, 62)
        self.assertEqual(meta.e164, "+628123456789")
        self.assertEqual(meta.region_code, "ID")
        self.assertIn("Telkomsel", meta.carrier)

    def test_parse_international_number(self):
        meta = parse_phone_number("+14155552671")
        self.assertTrue(meta.is_valid)
        self.assertEqual(meta.country_code, 1)
        self.assertEqual(meta.region_code, "US")

    def test_invalid_number(self):
        meta = parse_phone_number("12345")
        self.assertFalse(meta.is_valid)

    def test_dork_generation(self):
        meta = parse_phone_number("+628123456789")
        dorks = generate_osint_dorks(meta)
        self.assertIn("Direct Messaging & Caller ID Lookups", dorks)
        self.assertIn("Social Media Footprints (Dorks)", dorks)
        self.assertIn("Public Pastes & Documents", dorks)


if __name__ == "__main__":
    unittest.main()
