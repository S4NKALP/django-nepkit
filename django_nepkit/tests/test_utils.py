"""
Tests for django-nepkit utility functions.
"""

from datetime import datetime as python_datetime, time as python_time

from nepali.datetime import nepalidate, nepalidatetime

from django_nepkit.utils import (
    format_nepali_time,
    try_parse_nepali_date,
    try_parse_nepali_datetime,
    try_parse_nepali_time,
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


class TestTimeParsing:
    """Tests for the framework-agnostic time parser."""

    def test_parse_time_from_string_24h(self):
        result = try_parse_nepali_time("14:30")
        assert isinstance(result, python_time)
        assert result.hour == 14
        assert result.minute == 30

    def test_parse_time_from_string_12h(self):
        result = try_parse_nepali_time("02:45 PM")
        assert isinstance(result, python_time)
        assert result.hour == 14
        assert result.minute == 45

    def test_parse_time_from_object(self):
        t = python_time(9, 15, 0)
        assert try_parse_nepali_time(t) is t

    def test_parse_time_from_datetime(self):
        dt = python_datetime(2024, 1, 1, 8, 0, 0)
        result = try_parse_nepali_time(dt)
        assert isinstance(result, python_time)
        assert result.hour == 8

    def test_parse_time_none_and_empty(self):
        assert try_parse_nepali_time(None) is None
        assert try_parse_nepali_time("") is None

    def test_parse_time_invalid(self):
        assert try_parse_nepali_time("not-a-time") is None


class TestTimeFormatting:
    """Tests for ``format_nepali_time``."""

    def test_format_default(self):
        assert format_nepali_time(python_time(14, 30)) == "02:30 PM"

    def test_format_with_explicit_format(self):
        assert format_nepali_time(python_time(14, 30), "%H:%M") == "14:30"

    def test_format_none(self):
        assert format_nepali_time(None) == ""

    def test_format_datetime(self):
        dt = python_datetime(2024, 1, 1, 9, 0, 0)
        assert format_nepali_time(dt, "%H:%M") == "09:00"
