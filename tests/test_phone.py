import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from phone import extract_phone_from_url, normalize_phone, validate_phone


class TestNormalizePhone(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(normalize_phone("+55 (11) 99999-9999"), "+5511999999999")

    def test_with_dots(self):
        self.assertEqual(normalize_phone("+55.11.99999.9999"), "+5511999999999")

    def test_already_clean(self):
        self.assertEqual(normalize_phone("+5511999999999"), "+5511999999999")

    def test_with_spaces(self):
        self.assertEqual(normalize_phone("55 11 99999 9999"), "5511999999999")

    def test_only_digits(self):
        self.assertEqual(normalize_phone("5511999999999"), "5511999999999")


class TestValidatePhone(unittest.TestCase):
    def test_valid_with_plus(self):
        self.assertTrue(validate_phone("+5511999999999"))

    def test_valid_without_plus(self):
        self.assertTrue(validate_phone("5511999999999"))

    def test_invalid_letters(self):
        self.assertFalse(validate_phone("abc123"))

    def test_invalid_mixed(self):
        self.assertFalse(validate_phone("55abc123"))

    def test_empty(self):
        self.assertFalse(validate_phone(""))


class TestExtractPhone(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(extract_phone_from_url("callandroid://5511999999999"), "5511999999999")

    def test_with_plus(self):
        self.assertEqual(extract_phone_from_url("callandroid://+5511999999999"), "+5511999999999")

    def test_with_spaces_encoded(self):
        self.assertEqual(extract_phone_from_url("callandroid://+55%2011%2099999-9999"), "+55 11 99999-9999")

    def test_case_insensitive(self):
        self.assertEqual(extract_phone_from_url("CallAndroid://5511999999999"), "5511999999999")

    def test_trailing_slash(self):
        self.assertEqual(extract_phone_from_url("callandroid://5511999999999/"), "5511999999999")

    def test_invalid_protocol(self):
        with self.assertRaises(ValueError):
            extract_phone_from_url("https://example.com")

    def test_empty_url(self):
        with self.assertRaises(ValueError):
            extract_phone_from_url("")

    def test_no_number(self):
        with self.assertRaises(ValueError):
            extract_phone_from_url("callandroid://")


class TestIntegration(unittest.TestCase):
    def test_full_flow(self):
        url = "callandroid://+55%20(11)%2099999-9999"
        raw = extract_phone_from_url(url)
        phone = normalize_phone(raw)
        self.assertTrue(validate_phone(phone))
        self.assertEqual(phone, "+5511999999999")


if __name__ == "__main__":
    unittest.main()
