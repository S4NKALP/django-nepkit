"""
Tests for django-nepkit validators.
"""
import pytest
from django.core.exceptions import ValidationError

from django_nepkit.validators import validate_nepali_phone_number


class TestPhoneNumberValidator:
    """Tests for Nepali phone number validation."""

    def test_valid_mobile_numbers(self):
        """Test that valid mobile numbers pass validation."""
        valid_mobiles = [
            "9841234567",
            "9801234567",
            "9851234567",
            "9861234567",
            "9741234567",
        ]
        
        for number in valid_mobiles:
            # Should not raise ValidationError
            validate_nepali_phone_number(number)

    def test_valid_landline_numbers(self):
        """Test that valid landline numbers pass validation."""
        valid_landlines = [
            "014123456",
            "015123456",
            "016123456",
        ]
        
        for number in valid_landlines:
            # Should not raise ValidationError
            validate_nepali_phone_number(number)

    def test_invalid_too_short(self):
        """Test that too short numbers fail validation."""
        with pytest.raises(ValidationError):
            validate_nepali_phone_number("12345")

    def test_invalid_too_long(self):
        """Test that too long numbers fail validation."""
        with pytest.raises(ValidationError):
            validate_nepali_phone_number("12345678901")

    def test_invalid_non_numeric(self):
        """Test that non-numeric strings fail validation."""
        with pytest.raises(ValidationError):
            validate_nepali_phone_number("abcdefghij")

    def test_invalid_wrong_prefix(self):
        """Test that numbers with wrong prefix fail validation."""
        with pytest.raises(ValidationError):
            validate_nepali_phone_number("1234567890")

    def test_invalid_empty_string(self):
        """Test that empty string fails validation."""
        with pytest.raises(ValidationError):
            validate_nepali_phone_number("")
