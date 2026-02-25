"""
Tests for django-nepkit form fields.
"""

import pytest
from django.core.exceptions import ValidationError
from nepali.datetime import nepalidate

from django_nepkit.forms import NepaliDateFormField


class TestNepaliDateFormField:
    """Tests for NepaliDateFormField."""

    def test_valid_date_input(self):
        """Test that valid date strings are accepted."""
        field = NepaliDateFormField()

        result = field.clean("2081-01-15")
        assert isinstance(result, nepalidate)
        assert result.year == 2081
        assert result.month == 1
        assert result.day == 15

    def test_multiple_input_formats(self):
        """Test that multiple date formats are accepted."""
        field = NepaliDateFormField()

        formats = [
            "2081-01-15",
            "15/01/2081",
            "15-01-2081",
        ]

        for date_str in formats:
            result = field.clean(date_str)
            assert isinstance(result, nepalidate)

    def test_empty_value_optional(self):
        """Test that empty value is accepted for optional fields."""
        field = NepaliDateFormField(required=False)

        result = field.clean("")
        assert result is None

    def test_empty_value_required(self):
        """Test that empty value raises error for required fields."""
        field = NepaliDateFormField(required=True)

        with pytest.raises(ValidationError):
            field.clean("")

    def test_invalid_date_format(self):
        """Test that invalid date format raises ValidationError."""
        field = NepaliDateFormField()

        with pytest.raises(ValidationError):
            field.clean("invalid-date")

    def test_nepalidate_object_input(self):
        """Test that nepalidate objects are accepted."""
        field = NepaliDateFormField()
        date_obj = nepalidate(2081, 1, 15)

        result = field.clean(date_obj)
        assert result is date_obj
