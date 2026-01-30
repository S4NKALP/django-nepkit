"""
Tests for django-nepkit DRF serializers.
"""

import pytest
from nepali.datetime import nepalidate, nepalidatetime

try:
    from rest_framework import serializers
    from django_nepkit.serializers import (
        NepaliDateSerializerField,
        NepaliDateTimeSerializerField,
    )

    DRF_AVAILABLE = True
except ImportError:
    DRF_AVAILABLE = False


@pytest.mark.skipif(not DRF_AVAILABLE, reason="DRF not installed")
class TestNepaliDateSerializerField:
    """Tests for NepaliDateSerializerField."""

    def test_serialize_nepalidate_object(self):
        """Test serializing a nepalidate object to string."""
        field = NepaliDateSerializerField()
        date_obj = nepalidate(2081, 1, 15)

        result = field.to_representation(date_obj)
        assert result == "2081-01-15"
        assert isinstance(result, str)

    def test_serialize_string_date(self):
        """Test serializing a string date."""
        field = NepaliDateSerializerField()

        result = field.to_representation("2081-01-15")
        assert result == "2081-01-15"

    def test_serialize_none(self):
        """Test that None is serialized as None."""
        field = NepaliDateSerializerField()

        result = field.to_representation(None)
        assert result is None

    def test_deserialize_valid_date(self):
        """Test deserializing a valid date string."""
        field = NepaliDateSerializerField()

        result = field.to_internal_value("2081-01-15")
        assert isinstance(result, nepalidate)
        assert result.year == 2081
        assert result.month == 1
        assert result.day == 15

    def test_deserialize_none(self):
        """Test that None/empty string is deserialized as None."""
        field = NepaliDateSerializerField()

        assert field.to_internal_value(None) is None
        assert field.to_internal_value("") is None

    def test_deserialize_invalid_raises_error(self):
        """Test that invalid date raises ValidationError."""
        field = NepaliDateSerializerField()

        with pytest.raises(serializers.ValidationError):
            field.to_internal_value("invalid-date")

    def test_language_setting_ne(self):
        """Test Devanagari output when ne=True."""
        field = NepaliDateSerializerField(ne=True)
        date_obj = nepalidate(2081, 1, 15)

        result = field.to_representation(date_obj)
        # Should use strftime_ne for Devanagari digits
        assert result == "२०८१-०१-१५"
        assert field.ne is True


@pytest.mark.skipif(not DRF_AVAILABLE, reason="DRF not installed")
class TestNepaliDateTimeSerializerField:
    """Tests for NepaliDateTimeSerializerField."""

    def test_serialize_nepalidatetime_object(self):
        """Test serializing a nepalidatetime object to string."""
        field = NepaliDateTimeSerializerField()
        dt_obj = nepalidatetime(2081, 1, 15, 14, 30, 0)

        result = field.to_representation(dt_obj)
        assert result == "2081-01-15 14:30:00"
        assert isinstance(result, str)

    def test_deserialize_valid_datetime(self):
        """Test deserializing a valid datetime string."""
        field = NepaliDateTimeSerializerField()

        result = field.to_internal_value("2081-01-15 14:30:00")
        assert isinstance(result, nepalidatetime)
        assert result.year == 2081
        assert result.hour == 14
        assert result.minute == 30

    def test_custom_format(self):
        """Test using a custom datetime format."""
        field = NepaliDateTimeSerializerField(format="%Y-%m-%d")
        dt_obj = nepalidatetime(2081, 1, 15, 14, 30, 0)

        result = field.to_representation(dt_obj)
        assert result == "2081-01-15"
