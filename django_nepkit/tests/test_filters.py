"""
Tests for django-nepkit filters (DRF and Admin).
"""
import pytest

try:
    from django_filters import FilterSet
    from django_nepkit.filters import (
        NepaliDateYearFilter,
        NepaliDateMonthFilter,
    )
    FILTERS_AVAILABLE = True
except ImportError:
    FILTERS_AVAILABLE = False


@pytest.mark.skipif(not FILTERS_AVAILABLE, reason="django-filter not installed")
class TestNepaliDateYearFilter:
    """Tests for NepaliDateYearFilter."""

    def test_filter_initialization(self):
        """Test that NepaliDateYearFilter can be initialized."""
        filter_instance = NepaliDateYearFilter(field_name="birth_date")
        
        assert filter_instance.field_name == "birth_date"

    def test_filter_has_correct_type(self):
        """Test that filter is a NumberFilter."""
        from django_filters import NumberFilter
        
        filter_instance = NepaliDateYearFilter(field_name="birth_date")
        assert isinstance(filter_instance, NumberFilter)


@pytest.mark.skipif(not FILTERS_AVAILABLE, reason="django-filter not installed")
class TestNepaliDateMonthFilter:
    """Tests for NepaliDateMonthFilter."""

    def test_filter_initialization(self):
        """Test that NepaliDateMonthFilter can be initialized."""
        filter_instance = NepaliDateMonthFilter(field_name="birth_date")
        
        assert filter_instance.field_name == "birth_date"

    def test_filter_has_correct_type(self):
        """Test that filter is a NumberFilter."""
        from django_filters import NumberFilter
        
        filter_instance = NepaliDateMonthFilter(field_name="birth_date")
        assert isinstance(filter_instance, NumberFilter)
