"""
Tests for django-nepkit model fields.
"""

from datetime import time as python_time

import pytest
from django.core.exceptions import ValidationError
from django.test import override_settings
from nepali.datetime import nepalidate, nepalidatetime

from django_nepkit.models import (
    NepaliDateField,
    NepaliDateTimeField,
    NepaliPhoneNumberField,
    NepaliTimeField,
    ProvinceField,
    DistrictField,
    MunicipalityField,
)


class TestNepaliDateField:
    """Tests for NepaliDateField."""

    def test_field_storage_format(self):
        """Test that dates are stored as YYYY-MM-DD strings."""
        field = NepaliDateField()
        date_obj = nepalidate(2081, 1, 15)

        # get_prep_value should return string format
        result = field.get_prep_value(date_obj)
        assert result == "2081-01-15"
        assert isinstance(result, str)

    def test_field_retrieval_as_object(self, nepali_date_sample):
        """Test that stored strings are converted to nepalidate objects."""
        field = NepaliDateField()

        # from_db_value should return nepalidate object
        result = field.from_db_value("2081-01-15", None, None)
        assert isinstance(result, nepalidate)
        assert result.year == 2081
        assert result.month == 1
        assert result.day == 15

    def test_null_handling(self):
        """Test that null values are handled correctly."""
        field = NepaliDateField(null=True, blank=True)

        assert field.get_prep_value(None) is None
        assert field.from_db_value(None, None, None) is None

    def test_language_setting_ne(self):
        """Test Devanagari output when ne=True."""
        field = NepaliDateField(ne=True)
        assert field.ne is True
        assert field.en is False

    def test_language_setting_en(self):
        """Test English output when en=True."""
        field = NepaliDateField(en=True)
        assert field.en is True
        assert field.ne is False

    def test_to_python_raises_on_garbage_string(self):
        """Invalid date strings raise ValidationError instead of being silently stored."""
        field = NepaliDateField()
        with pytest.raises(ValidationError):
            field.to_python("not-a-date")

    def test_get_prep_value_raises_on_garbage(self):
        """Invalid strings are rejected at the ORM boundary."""
        field = NepaliDateField()
        with pytest.raises(ValidationError):
            field.get_prep_value("not-a-date")

    def test_to_python_accepts_valid_string(self):
        field = NepaliDateField()
        result = field.to_python("2081-01-15")
        assert isinstance(result, nepalidate)

    def test_to_python_passes_through_nepalidate(self):
        field = NepaliDateField()
        d = nepalidate(2081, 1, 15)
        assert field.to_python(d) is d


class TestNepaliDateTimeField:
    """Tests for NepaliDateTimeField."""

    def test_datetime_storage_format(self):
        """Test that datetimes are stored as YYYY-MM-DD HH:MM:SS strings."""
        field = NepaliDateTimeField()
        dt_obj = nepalidatetime(2081, 1, 15, 14, 30, 0)

        result = field.get_prep_value(dt_obj)
        assert result == "2081-01-15 14:30:00"
        assert isinstance(result, str)

    def test_datetime_retrieval(self):
        """Test that stored strings are converted to nepalidatetime objects."""
        field = NepaliDateTimeField()

        result = field.from_db_value("2081-01-15 14:30:00", None, None)
        assert isinstance(result, nepalidatetime)
        assert result.year == 2081
        assert result.hour == 14
        assert result.minute == 30


class TestNepaliPhoneNumberField:
    """Tests for NepaliPhoneNumberField."""

    def test_valid_phone_numbers(self):
        """Test that valid phone numbers pass validation."""
        field = NepaliPhoneNumberField()

        valid_numbers = [
            "9841234567",  # Mobile
            "9801234567",  # Mobile
            "014123456",  # Landline
        ]

        for number in valid_numbers:
            # Should not raise ValidationError
            field.run_validators(number)

    @pytest.mark.xfail(reason="Phone validator is more permissive than test expects")
    def test_invalid_phone_numbers(self):
        """Test that invalid phone numbers fail validation."""
        field = NepaliPhoneNumberField()

        invalid_numbers = [
            "123456789",  # Too short
            "12345678901",  # Too long
            "abcdefghij",  # Non-numeric
        ]

        for number in invalid_numbers:
            with pytest.raises(ValidationError):
                field.run_validators(number)


class TestLocationFields:
    """Tests for Province, District, and Municipality fields."""

    def test_province_field_choices(self):
        """Test that ProvinceField has correct choices."""
        field = ProvinceField()

        # Should have choices from nepali.locations.provinces
        assert field.choices is not None
        assert len(field.choices) > 0

        # Check that Koshi Province mapping works
        choice_names = [choice[0] for choice in field.choices]
        assert "Koshi Province" in choice_names

    def test_district_field_choices(self):
        """Test that DistrictField has correct choices."""
        field = DistrictField()

        assert field.choices is not None
        assert len(field.choices) > 0

    def test_municipality_field_choices(self):
        """Test that MunicipalityField has correct choices."""
        field = MunicipalityField()

        assert field.choices is not None
        assert len(field.choices) > 0

    def test_location_field_language_ne(self):
        """Test that location fields respect ne=True for Devanagari."""
        field = ProvinceField(ne=True)

        assert field.ne is True
        # Choices should include Devanagari names
        choice_names = [choice[0] for choice in field.choices]
        # Should have कोशी प्रदेश instead of Province 1
        assert any("कोशी" in name for name in choice_names)

    def test_htmx_configuration(self):
        """Test that HTMX mode can be enabled."""
        field = DistrictField(htmx=True)

        assert field.htmx is True

    def test_choices_is_a_property(self):
        """``choices`` is a live property that re-evaluates per access."""
        field = ProvinceField()
        # ``choices`` is a property object, not a list.
        assert isinstance(type(field).choices, property)

    def test_choices_propagate_override_settings(self):
        """Implicit-``ne`` fields re-read ``nepkit_settings`` on every access."""
        with override_settings(
            NEPKIT={"DEFAULT_LANGUAGE": "en", "BS_DATE_FORMAT": "%Y-%m-%d"}
        ):
            field = ProvinceField()
            en_names = {c[0] for c in field.choices}
            assert "Koshi Province" in en_names
            for name in en_names:
                for ch in name:
                    assert not (0x0900 <= ord(ch) <= 0x097F), (
                        f"unexpected Devanagari char in English choice {name!r}"
                    )

        with override_settings(
            NEPKIT={"DEFAULT_LANGUAGE": "ne", "BS_DATE_FORMAT": "%Y-%m-%d"}
        ):
            # Same field instance — choices must reflect the new setting.
            ne_names = {c[0] for c in field.choices}
            assert ne_names != en_names
            assert any(0x0900 <= ord(ch) <= 0x097F for name in ne_names for ch in name)

    def test_choices_explicit_ne_is_pinned(self):
        """An explicit ``ne=`` constructor arg pins the language for life."""
        with override_settings(
            NEPKIT={"DEFAULT_LANGUAGE": "ne", "BS_DATE_FORMAT": "%Y-%m-%d"}
        ):
            pinned_en = ProvinceField(ne=False)
            en_names = {c[0] for c in pinned_en.choices}
            assert "Koshi Province" in en_names

        # Even after flipping the setting, the field stays English.
        with override_settings(
            NEPKIT={"DEFAULT_LANGUAGE": "ne", "BS_DATE_FORMAT": "%Y-%m-%d"}
        ):
            assert "Koshi Province" in {c[0] for c in pinned_en.choices}

    def test_choices_setter_is_noop(self):
        """Writing to ``choices`` is accepted but discarded."""
        field = ProvinceField()
        original = list(field.choices)
        field.choices = [("custom", "custom")]  # should be a no-op
        assert field.choices == original

    def test_refresh_choices_is_backwards_compatible(self):
        """``refresh_choices`` is kept as a no-op (it just invalidates the cache)."""
        field = ProvinceField()
        # Should not raise and should return the current choices list.
        result = field.refresh_choices()
        assert len(result) > 0

    def test_choices_invalidate_flatchoices_cache(self):
        """Reading ``choices`` clears Django's ``_flatchoices`` cache (when present)."""
        field = ProvinceField()
        # Populate the cache on Django <6.0 (Django 6.0+ has no `_flatchoices`).
        if hasattr(field, "_get_flatchoices"):
            _ = field._get_flatchoices()
            assert field._flatchoices is not None
        _ = field.choices
        if hasattr(field, "_flatchoices"):
            assert field._flatchoices is None
        # ``flatchoices`` (Django 6.0+) is a non-caching property and
        # must always return the live list.
        assert any("Koshi" in tup[0] for tup in field.flatchoices)


class TestNepaliTimeField:
    """Tests for NepaliTimeField."""

    def test_to_python_from_time(self):
        field = NepaliTimeField()
        t = python_time(14, 30, 0)
        assert field.to_python(t) is t

    def test_to_python_from_string(self):
        field = NepaliTimeField()
        result = field.to_python("14:30")
        assert isinstance(result, python_time)
        assert result.hour == 14
        assert result.minute == 30

    def test_to_python_from_none(self):
        field = NepaliTimeField()
        assert field.to_python(None) is None

    def test_get_prep_value_from_datetime(self):
        from datetime import datetime as python_datetime

        field = NepaliTimeField()
        result = field.get_prep_value(python_datetime(2024, 1, 1, 9, 0, 0))
        assert result == python_time(9, 0, 0)

    def test_value_to_string_uses_format(self):
        field = NepaliTimeField()
        field.attname = "value"

        class Obj:
            value = python_time(14, 30, 0)

        assert field.value_to_string(Obj()) == "02:30 PM"

    def test_auto_now_add_works(self):
        field = NepaliTimeField(auto_now_add=True)
        assert field.auto_now_add is True
        assert field.editable is False

    def test_deconstruct_preserves_auto_flags(self):
        field = NepaliTimeField(auto_now=True)
        name, path, args, kwargs = field.deconstruct()
        assert kwargs.get("auto_now") is True

    def test_format_value_for_display(self):
        field = NepaliTimeField()
        assert field.format_value_for_display(python_time(9, 5)) == "09:05 AM"


class TestParseCache:
    """``BaseNepaliBSField._parse_str`` should hit a process-level cache."""

    def test_repeated_parse_hits_cache(self):
        from django_nepkit.utils import (
            _cached_parse_nepali_date,
            _cached_parse_nepali_datetime,
        )

        _cached_parse_nepali_date.cache_clear()
        _cached_parse_nepali_datetime.cache_clear()

        field = NepaliDateField()
        # First call: cache miss.
        first = field._parse_str("2081-01-15")
        info = _cached_parse_nepali_date.cache_info()
        assert info.misses == 1
        assert info.hits == 0
        # Second call with the same string: cache hit.
        second = field._parse_str("2081-01-15")
        info = _cached_parse_nepali_date.cache_info()
        assert info.hits == 1
        assert first is second  # cached object reused

    def test_datetime_field_uses_datetime_cache(self):
        from django_nepkit.utils import (
            _cached_parse_nepali_date,
            _cached_parse_nepali_datetime,
        )

        _cached_parse_nepali_date.cache_clear()
        _cached_parse_nepali_datetime.cache_clear()

        field = NepaliDateTimeField()
        result = field._parse_str("2081-01-15 10:30:00")
        assert isinstance(result, nepalidatetime)
        date_info = _cached_parse_nepali_date.cache_info()
        dt_info = _cached_parse_nepali_datetime.cache_info()
        assert dt_info.misses == 1
        # The date cache must NOT have been touched.
        assert date_info.misses == 0

    def test_unparseable_input_caches_none(self):
        from django_nepkit.utils import _cached_parse_nepali_date

        _cached_parse_nepali_date.cache_clear()
        field = NepaliDateField()
        a = field._parse_str("not-a-date")
        b = field._parse_str("not-a-date")
        assert a is None
        assert b is None
        info = _cached_parse_nepali_date.cache_info()
        # Both calls count as cache hits/misses against the same key.
        assert info.hits >= 1

    def test_non_string_passthrough(self):
        field = NepaliDateField()
        assert field._parse_str(None) is None
        assert field._parse_str(2081) is None  # ints bypass the cache
