"""Tests for Chinese number parsing utility."""

from __future__ import annotations

import unittest

from intelligence.adapters._common import parse_chinese_number


class ChineseNumberParsingTests(unittest.TestCase):
    """Test parse_chinese_number handles all Chinese number formats."""

    def test_wan_format_with_plus_suffix(self) -> None:
        """10万+ should parse to 100000."""
        result = parse_chinese_number("10万+")
        self.assertEqual(result, 100000)

    def test_decimal_wan_format(self) -> None:
        """2.1万 should parse to 21000."""
        result = parse_chinese_number("2.1万")
        self.assertEqual(result, 21000)

    def test_decimal_wan_format_alternate(self) -> None:
        """1.3万 should parse to 13000."""
        result = parse_chinese_number("1.3万")
        self.assertEqual(result, 13000)

    def test_plain_digit_string(self) -> None:
        """9196 should parse to 9196."""
        result = parse_chinese_number("9196")
        self.assertEqual(result, 9196)

    def test_zero_string(self) -> None:
        """0 should parse to 0."""
        result = parse_chinese_number("0")
        self.assertEqual(result, 0)

    def test_none_returns_none(self) -> None:
        """None should return None."""
        result = parse_chinese_number(None)
        self.assertIsNone(result)

    def test_empty_string_returns_none(self) -> None:
        """Empty string should return None."""
        result = parse_chinese_number("")
        self.assertIsNone(result)

    def test_whitespace_only_returns_none(self) -> None:
        """Whitespace-only string should return None."""
        result = parse_chinese_number("   ")
        self.assertIsNone(result)

    def test_non_numeric_string_returns_none(self) -> None:
        """Non-numeric string should return None."""
        result = parse_chinese_number("abc")
        self.assertIsNone(result)

    def test_qian_format_with_decimal(self) -> None:
        """1.5千 should parse to 1500."""
        result = parse_chinese_number("1.5千")
        self.assertEqual(result, 1500)

    def test_integer_wan_format(self) -> None:
        """5万 should parse to 50000."""
        result = parse_chinese_number("5万")
        self.assertEqual(result, 50000)

    def test_integer_qian_format(self) -> None:
        """3千 should parse to 3000."""
        result = parse_chinese_number("3千")
        self.assertEqual(result, 3000)

    def test_plain_digit_string_with_leading_zero(self) -> None:
        """0123 should parse to 123."""
        result = parse_chinese_number("0123")
        self.assertEqual(result, 123)

    def test_wan_format_without_plus(self) -> None:
        """10万 should parse to 100000."""
        result = parse_chinese_number("10万")
        self.assertEqual(result, 100000)

    def test_decimal_wan_format_with_two_decimals(self) -> None:
        """0.57万 should parse to 5700, not 5699 (tests round instead of int truncation)."""
        result = parse_chinese_number("0.57万")
        self.assertEqual(result, 5700)


if __name__ == "__main__":
    unittest.main()
