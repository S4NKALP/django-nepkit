"""
Tests for the framework-agnostic serialization helpers in ``django_nepkit.api``.
"""

from datetime import datetime as python_datetime, time as python_time
from decimal import Decimal

import pytest
from nepali.datetime import nepalidate, nepalidatetime

from django_nepkit.api import (
    _looks_numeric,
    build_localized_payload,
    deserialize_nepali_currency,
    deserialize_nepali_date,
    deserialize_nepali_datetime,
    deserialize_nepali_time,
    serialize_nepali_currency,
    serialize_nepali_date,
    serialize_nepali_datetime,
    serialize_nepali_time,
    to_decimal,
)


class TestSerializeNepaliDate:
    def test_none_passthrough(self):
        assert serialize_nepali_date(None) is None

    def test_serializes_nepalidate(self):
        assert serialize_nepali_date(nepalidate(2081, 1, 15)) == "2081-01-15"

    def test_serializes_string_input(self):
        assert serialize_nepali_date("2081-01-15") == "2081-01-15"

    def test_ne_flag_uses_devanagari(self):
        assert "२०८१" in serialize_nepali_date(nepalidate(2081, 1, 15), ne=True)

    def test_custom_format(self):
        assert (
            serialize_nepali_date(nepalidate(2081, 1, 15), fmt="%Y/%m/%d")
            == "2081/01/15"
        )

    def test_strict_raises_on_garbage(self):
        with pytest.raises(ValueError, match="Cannot serialize"):
            serialize_nepali_date("not-a-date", strict=True)

    def test_non_strict_returns_str(self):
        """Non-strict mode is a passthrough so existing integrations don't break."""
        assert serialize_nepali_date("not-a-date") == "not-a-date"


class TestDeserializeNepaliDate:
    def test_none(self):
        assert deserialize_nepali_date(None) is None

    def test_empty_string(self):
        assert deserialize_nepali_date("") is None

    def test_round_trip(self):
        result = deserialize_nepali_date("2081-01-15")
        assert isinstance(result, nepalidate)
        assert result.year == 2081

    def test_strict_raises_on_garbage(self):
        with pytest.raises(ValueError, match="Cannot parse"):
            deserialize_nepali_date("not-a-date", strict=True)

    def test_strict_raises_on_wrong_type(self):
        with pytest.raises(ValueError, match="Cannot parse"):
            deserialize_nepali_date(12345, strict=True)


class TestSerializeNepaliDatetime:
    def test_serializes(self):
        assert (
            serialize_nepali_datetime(nepalidatetime(2081, 1, 15, 14, 30))
            == "2081-01-15 14:30:00"
        )

    def test_ne_flag(self):
        result = serialize_nepali_datetime(nepalidatetime(2081, 1, 15, 14, 30), ne=True)
        assert "२०८१" in result


class TestDeserializeNepaliDatetime:
    def test_round_trip(self):
        result = deserialize_nepali_datetime("2081-01-15 14:30:00")
        assert isinstance(result, nepalidatetime)
        assert result.hour == 14

    def test_strict_raises_on_garbage(self):
        with pytest.raises(ValueError, match="Cannot parse"):
            deserialize_nepali_datetime("not-a-datetime", strict=True)


class TestSerializeNepaliTime:
    def test_none(self):
        assert serialize_nepali_time(None) is None

    def test_serializes_time(self):
        assert serialize_nepali_time(python_time(14, 30)) == "02:30 PM"

    def test_ne_flag(self):
        result = serialize_nepali_time(python_time(14, 30), ne=True)
        assert "०२" in result

    def test_strict_raises_on_garbage(self):
        with pytest.raises(ValueError, match="Cannot serialize"):
            serialize_nepali_time("not-a-time", strict=True)


class TestDeserializeNepaliTime:
    def test_round_trip(self):
        result = deserialize_nepali_time("02:30 PM")
        assert isinstance(result, python_time)
        assert result.hour == 14
        assert result.minute == 30

    def test_from_datetime(self):
        result = deserialize_nepali_time(python_datetime(2024, 1, 1, 9, 0))
        assert result == python_time(9, 0)

    def test_strict_raises_on_garbage(self):
        with pytest.raises(ValueError, match="Cannot parse"):
            deserialize_nepali_time("not-a-time", strict=True)


class TestSerializeNepaliCurrency:
    def test_none(self):
        assert serialize_nepali_currency(None) is None

    def test_formats_with_symbol(self):
        assert serialize_nepali_currency(1234567) == "Rs. 12,34,567.00"

    def test_no_symbol(self):
        assert serialize_nepali_currency(1234567, currency_symbol="") == "12,34,567.00"

    def test_ne_flag(self):
        assert "१२" in serialize_nepali_currency(12, ne=True)

    def test_preserves_decimal_precision(self):
        value = Decimal("123456789012345.67")
        assert "12,34,56,78,90,12,345.67" in serialize_nepali_currency(value)

    def test_non_numeric_string_passthrough(self):
        """Non-numeric strings are passed through so legacy callers don't crash."""
        assert serialize_nepali_currency("n/a") == "n/a"


class TestDeserializeNepaliCurrency:
    def test_none(self):
        assert deserialize_nepali_currency(None) is None

    def test_passes_through_numbers(self):
        assert deserialize_nepali_currency(1234) == 1234
        assert deserialize_nepali_currency(Decimal("12.50")) == Decimal("12.50")

    def test_parses_formatted_string(self):
        result = deserialize_nepali_currency("Rs. 12,34,567.00")
        assert isinstance(result, Decimal)
        assert result == Decimal("1234567.00")

    def test_parses_nepali_digits(self):
        result = deserialize_nepali_currency("Rs. १२,३४५")
        assert isinstance(result, Decimal)
        assert result == Decimal("12345")

    def test_strict_raises_on_invalid_string(self):
        with pytest.raises(ValueError, match="Cannot parse"):
            deserialize_nepali_currency("not-a-number", strict=True)


class TestToDecimal:
    def test_none(self):
        assert to_decimal(None) is None

    def test_decimal_passthrough(self):
        assert to_decimal(Decimal("1.5")) == Decimal("1.5")

    def test_int(self):
        assert to_decimal(42) == Decimal("42")

    def test_string(self):
        assert to_decimal("12.34") == Decimal("12.34")

    def test_invalid_string_returns_input(self):
        assert to_decimal("not-a-number") == "not-a-number"

    def test_strict_raises_on_invalid_string(self):
        with pytest.raises(ValueError, match="Cannot convert"):
            to_decimal("not-a-number", strict=True)

    def test_strict_raises_on_bool(self):
        with pytest.raises(ValueError, match="boolean"):
            to_decimal(True, strict=True)

    def test_strict_raises_on_non_finite(self):
        with pytest.raises(ValueError, match="non-finite"):
            to_decimal(float("inf"), strict=True)


class TestLooksNumeric:
    def test_rejects_infinity_strings(self):
        """``1e1000`` overflows to ``inf`` and must be rejected."""
        assert _looks_numeric("1e1000") is False
        assert _looks_numeric("inf") is False
        assert _looks_numeric("nan") is False

    def test_accepts_plain_numbers(self):
        assert _looks_numeric("1234") is True
        assert _looks_numeric("-12.5") is True
        assert _looks_numeric("1,234.5") is True

    def test_rejects_empty_and_garbage(self):
        assert _looks_numeric("") is False
        assert _looks_numeric("abc") is False
        assert _looks_numeric("12abc") is False


class TestBuildLocalizedPayload:
    def test_disabled_returns_input(self):
        data = {"a": 1}
        assert build_localized_payload(data, ne=False) == {"a": 1}

    def test_mirrors_nepalidate(self):
        data = {"date": nepalidate(2080, 1, 1)}
        out = build_localized_payload(data, ne=True, raw_values=data)
        assert out["date_ne"] == "२०८०-०१-०१"

    def test_mirrors_currency(self):
        data = {"amount": 100000}
        out = build_localized_payload(data, ne=True)
        assert "१" in out["amount_ne"]

    def test_does_not_overwrite_existing(self):
        data = {"amount": 100, "amount_ne": "preexisting"}
        out = build_localized_payload(data, ne=True)
        assert out["amount_ne"] == "preexisting"

    def test_no_mirror_when_ne_false(self):
        data = {"date": nepalidate(2080, 1, 1)}
        out = build_localized_payload(data, ne=False, raw_values=data)
        assert "date_ne" not in out
