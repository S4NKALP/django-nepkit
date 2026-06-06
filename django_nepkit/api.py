"""
Framework-agnostic serialization helpers for Nepali values.

These functions are designed to be reused by any API framework
(DRF, Django Ninja, plain Django views, …) and only depend on
standard library types plus ``nepali`` for the date logic.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import datetime as python_datetime
from datetime import time as python_time
from decimal import Decimal, InvalidOperation
from typing import Any, Optional

from nepali.datetime import nepalidate, nepalidatetime
from nepali.number import english_to_nepali

from django_nepkit.conf import nepkit_settings
from django_nepkit.utils import (
    format_nepali_currency,
    format_nepali_time,
    try_parse_nepali_date,
    try_parse_nepali_datetime,
    try_parse_nepali_time,
)


@dataclass
class NepaliValue:
    """A typed wrapper around a parsed Nepali value.

    ``raw`` is the underlying Python object (``nepalidate``, ``nepalidatetime``
    or ``time``). ``format`` is the strftime format the caller wants to use
    for display, and ``ne`` signals whether Devanagari digits should be
    applied. ``source`` records where the value came from so callers can
    route validation messages back to the right field.
    """

    raw: Any
    format: str
    ne: bool = False
    source: str = ""

    def to_string(self) -> str:
        return _format_with_ne(self.raw, self.format, self.ne)


def _format_with_ne(value: Any, fmt: str, ne: bool) -> str:
    if value is None:
        return ""
    if ne and hasattr(value, "strftime_ne"):
        try:
            return value.strftime_ne(fmt)
        except (ValueError, TypeError):
            pass
    if isinstance(value, (nepalidate, nepalidatetime)):
        return value.strftime(fmt)
    if isinstance(value, python_time):
        return format_nepali_time(value, fmt)
    if isinstance(value, python_datetime):
        return value.strftime(fmt)
    return str(value)


def resolve_ne_flag(ne: Optional[bool]) -> bool:
    """Default ``ne`` from the project setting when ``ne is None``."""
    if ne is None:
        return nepkit_settings.DEFAULT_LANGUAGE == "ne"
    return ne


def serialize_nepali_date(
    value: Any,
    *,
    fmt: Optional[str] = None,
    ne: Optional[bool] = None,
    strict: bool = False,
) -> Optional[str]:
    """
    Serialize a Nepali date (or any value accepted by ``try_parse_nepali_date``).

    Returns ``None`` for ``None`` input.  When ``strict=True``, raises
    ``ValueError`` for values that cannot be parsed; otherwise returns
    the string representation of the input as a best-effort passthrough.
    """
    if value is None:
        return None
    parsed = value if isinstance(value, nepalidate) else try_parse_nepali_date(value)
    if parsed is None:
        if strict:
            raise ValueError(f"Cannot serialize {value!r} as a Nepali date")
        return str(value)
    return _format_with_ne(
        parsed, fmt or nepkit_settings.BS_DATE_FORMAT, resolve_ne_flag(ne)
    )


def deserialize_nepali_date(data: Any, strict: bool = False) -> Optional[nepalidate]:
    """Parse a string/object into a ``nepalidate`` (or ``None``).

    With ``strict=True`` raises ``ValueError`` for unrecognised values
    that aren't ``None`` or empty.
    """
    if data in (None, ""):
        return None
    if isinstance(data, nepalidate):
        return data
    if isinstance(data, str):
        result = try_parse_nepali_date(data)
        if result is not None:
            return result
        if strict:
            raise ValueError(f"Cannot parse {data!r} as a Nepali date")
        return None
    if strict:
        raise ValueError(f"Cannot parse {type(data).__name__} as a Nepali date")
    return None


def serialize_nepali_datetime(
    value: Any,
    *,
    fmt: Optional[str] = None,
    ne: Optional[bool] = None,
    strict: bool = False,
) -> Optional[str]:
    if value is None:
        return None
    parsed = (
        value if isinstance(value, nepalidatetime) else try_parse_nepali_datetime(value)
    )
    if parsed is None:
        if strict:
            raise ValueError(f"Cannot serialize {value!r} as a Nepali datetime")
        return str(value)
    return _format_with_ne(
        parsed, fmt or nepkit_settings.BS_DATETIME_FORMAT, resolve_ne_flag(ne)
    )


def deserialize_nepali_datetime(
    data: Any, strict: bool = False
) -> Optional[nepalidatetime]:
    if data in (None, ""):
        return None
    if isinstance(data, nepalidatetime):
        return data
    if isinstance(data, str):
        result = try_parse_nepali_datetime(data)
        if result is not None:
            return result
        if strict:
            raise ValueError(f"Cannot parse {data!r} as a Nepali datetime")
        return None
    if strict:
        raise ValueError(f"Cannot parse {type(data).__name__} as a Nepali datetime")
    return None


def serialize_nepali_time(
    value: Any,
    *,
    fmt: Optional[str] = None,
    ne: Optional[bool] = None,
    strict: bool = False,
) -> Optional[str]:
    if value is None:
        return None
    parsed = value if isinstance(value, python_time) else try_parse_nepali_time(value)
    if parsed is None:
        if strict:
            raise ValueError(f"Cannot serialize {value!r} as a Nepali time")
        return str(value)
    formatted = format_nepali_time(parsed, fmt or nepkit_settings.BS_TIME_FORMAT)
    if resolve_ne_flag(ne) and formatted:
        formatted = english_to_nepali(formatted)
    return formatted


def deserialize_nepali_time(data: Any, strict: bool = False) -> Optional[python_time]:
    if data in (None, ""):
        return None
    if isinstance(data, python_time):
        return data
    if isinstance(data, python_datetime):
        return data.time()
    if isinstance(data, str):
        result = try_parse_nepali_time(data)
        if result is not None:
            return result
        if strict:
            raise ValueError(f"Cannot parse {data!r} as a Nepali time")
        return None
    if strict:
        raise ValueError(f"Cannot parse {type(data).__name__} as a Nepali time")
    return None


def serialize_nepali_currency(
    value: Any,
    *,
    currency_symbol: str = "Rs.",
    ne: Optional[bool] = None,
) -> Optional[str]:
    if value is None:
        return None
    if isinstance(value, str) and not _looks_numeric(value):
        return value
    return format_nepali_currency(
        value, currency_symbol=currency_symbol, ne=resolve_ne_flag(ne)
    )


def deserialize_nepali_currency(data: Any, strict: bool = False) -> Any:
    """Parse a currency input back to a ``Decimal`` (or float for empty input).

    Accepts plain numbers and Nepali-formatted strings (with Nepali digits
    and the optional ``Rs.`` prefix).  With ``strict=True`` raises
    ``ValueError`` for unrecognised strings.
    """
    if data in (None, ""):
        return None
    if isinstance(data, (int, float, Decimal)):
        return data
    if isinstance(data, str):
        cleaned = _strip_nepali_currency(data)
        try:
            return Decimal(cleaned)
        except (InvalidOperation, ValueError) as exc:
            if strict:
                raise ValueError(f"Cannot parse {data!r} as a currency") from exc
            return data
    if strict:
        raise ValueError(f"Cannot parse {type(data).__name__} as a currency")
    return data


def _looks_numeric(value: str) -> bool:
    """Heuristic: does ``value`` look like a number?

    Accepts commas and leading ``+``/``-``; rejects infinities, NaN, and
    obviously non-numeric strings so callers can short-circuit.
    """
    cleaned = value.replace(",", "").strip()
    if not cleaned:
        return False
    try:
        number = float(cleaned)
    except (ValueError, TypeError):
        return False
    return math.isfinite(number)


def _strip_nepali_currency(text: str) -> str:
    """Strip ``Rs.`` / ``रु.`` prefix and convert Nepali digits to English."""
    cleaned = text.strip()
    for prefix in ("Rs.", "Rs ", "रु.", "रु ", "NPR", "NPR "):
        if cleaned.startswith(prefix):
            cleaned = cleaned[len(prefix) :]
            break
    cleaned = cleaned.replace(",", "").strip()
    return _nepali_digits_to_english(cleaned)


_NEPALI_DIGITS = {
    "०": "0",
    "१": "1",
    "२": "2",
    "३": "3",
    "४": "4",
    "५": "5",
    "६": "6",
    "७": "7",
    "८": "8",
    "९": "9",
}


def _nepali_digits_to_english(text: str) -> str:
    return "".join(_NEPALI_DIGITS.get(ch, ch) for ch in text)


def to_decimal(value: Any, strict: bool = False) -> Any:
    """Coerce ``value`` to ``Decimal`` when possible, otherwise return as-is.

    With ``strict=True`` raises ``ValueError`` for unparseable strings
    instead of returning them.
    """
    if value in (None, ""):
        return None
    if isinstance(value, Decimal):
        return value
    if isinstance(value, bool):
        if strict:
            raise ValueError(f"Cannot convert boolean to Decimal: {value!r}")
        return value
    if isinstance(value, (int, float)):
        if isinstance(value, float) and not math.isfinite(value):
            if strict:
                raise ValueError(
                    f"Cannot convert non-finite float to Decimal: {value!r}"
                )
            return value
        return Decimal(str(value))
    if isinstance(value, str):
        try:
            return Decimal(value)
        except (InvalidOperation, ValueError) as exc:
            if strict:
                raise ValueError(f"Cannot convert {value!r} to Decimal") from exc
            return value
    if strict:
        raise ValueError(f"Cannot convert {type(value).__name__} to Decimal")
    return value


def build_localized_payload(
    representation: dict,
    *,
    ne: bool = False,
    raw_values: Optional[dict] = None,
) -> dict:
    """Return ``representation`` plus a ``_ne`` mirror if ``ne`` is True.

    The mirror uses keys suffixed with ``_ne`` so frameworks that expect a
    flat dict (Django's ``JsonResponse``, Ninja schemas with dict fields)
    can opt-in to localized output without custom mixins.

    ``raw_values`` lets the caller supply the original Python objects
    (e.g. :class:`nepalidate` instances) for fields where the serialized
    representation has already been stringified. When supplied, raw
    values take precedence over the (possibly stringified) ones in
    ``representation``.
    """
    if not ne:
        return representation
    out = dict(representation)
    for key, value in representation.items():
        mirror_key = f"{key}_ne"
        if mirror_key in out:
            continue
        raw = (raw_values or {}).get(key, value)
        if isinstance(raw, nepalidate):
            out[mirror_key] = raw.strftime_ne(nepkit_settings.BS_DATE_FORMAT)
        elif isinstance(raw, nepalidatetime):
            out[mirror_key] = raw.strftime_ne(nepkit_settings.BS_DATETIME_FORMAT)
        elif isinstance(raw, python_time):
            out[mirror_key] = english_to_nepali(
                format_nepali_time(raw, nepkit_settings.BS_TIME_FORMAT)
            )
        elif isinstance(raw, (int, float, Decimal)):
            out[mirror_key] = format_nepali_currency(raw, currency_symbol="", ne=True)
        elif isinstance(value, str) and _looks_numeric(value):
            out[mirror_key] = format_nepali_currency(value, currency_symbol="", ne=True)
    return out
