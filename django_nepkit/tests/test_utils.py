"""
Tests for django-nepkit utility functions.
"""

from nepali.datetime import nepalidate, nepalidatetime

from django_nepkit.utils import (
    try_parse_nepali_date,
    try_parse_nepali_datetime,
)


class TestDateParsing:
    """Tests for date parsing utilities."""

    def test_parse_nepali_date_from_string(self):
        """Test parsing BS date from string."""
        result = try_parse_nepali_date("2081-01-15")

        assert result is not None
        assert isinstance(result, nepalidate)
        assert result.year == 2081
        assert result.month == 1
        assert result.day == 15

    def test_parse_nepali_date_multiple_formats(self):
        """Test parsing BS date from different formats."""
        formats = [
            "2081-01-15",
            "15/01/2081",
            "15-01-2081",
        ]

        for date_str in formats:
            result = try_parse_nepali_date(date_str)
            assert result is not None
            assert isinstance(result, nepalidate)

    def test_parse_nepali_date_from_object(self):
        """Test that passing a nepalidate object returns it unchanged."""
        date_obj = nepalidate(2081, 1, 15)
        result = try_parse_nepali_date(date_obj)

        assert result is date_obj

    def test_parse_nepali_date_none(self):
        """Test that None returns None."""
        result = try_parse_nepali_date(None)
        assert result is None

    def test_parse_nepali_date_empty_string(self):
        """Test that empty string returns None."""
        result = try_parse_nepali_date("")
        assert result is None

    def test_parse_nepali_date_invalid(self):
        """Test that invalid date string returns None."""
        result = try_parse_nepali_date("invalid-date")
        assert result is None


class TestDateTimeParsing:
    """Tests for datetime parsing utilities."""

    def test_parse_nepali_datetime_from_string(self):
        """Test parsing BS datetime from string."""
        result = try_parse_nepali_datetime("2081-01-15 14:30:00")

        assert result is not None
        assert isinstance(result, nepalidatetime)
        assert result.year == 2081
        assert result.month == 1
        assert result.day == 15
        assert result.hour == 14
        assert result.minute == 30

    def test_parse_nepali_datetime_from_object(self):
        """Test that passing a nepalidatetime object returns it unchanged."""
        dt_obj = nepalidatetime(2081, 1, 15, 14, 30, 0)
        result = try_parse_nepali_datetime(dt_obj)

        assert result is dt_obj

    def test_parse_nepali_datetime_none(self):
        """Test that None returns None."""
        result = try_parse_nepali_datetime(None)
        assert result is None

    def test_parse_nepali_datetime_invalid(self):
        """Test that invalid datetime string returns None."""
        result = try_parse_nepali_datetime("invalid-datetime")
        assert result is None
