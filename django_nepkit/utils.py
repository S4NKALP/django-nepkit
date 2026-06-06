from __future__ import annotations

import re
from datetime import time as python_time
from decimal import Decimal, InvalidOperation
from functools import lru_cache
from typing import Any, Optional

from nepali.datetime import nepalidate, nepalidatetime
from nepali.exceptions import FormatNotMatchException
from nepali.locations import districts, municipalities, provinces

from django_nepkit.conf import nepkit_settings
from django_nepkit.constants import NEGATIVE_PREFIX, NEPALI_ONES, NEPALI_UNITS


# Anything we treat as "this format didn't match, try the next one".
_PARSE_ERRORS = (ValueError, TypeError, FormatNotMatchException)


# ---------------------------------------------------------------------------
# Live format constants
# ---------------------------------------------------------------------------
#
# ``BS_DATE_FORMAT`` / ``BS_DATETIME_FORMAT`` / ``BS_TIME_FORMAT`` are exposed
# for backwards compat (e.g. ``from django_nepkit.utils import BS_DATE_FORMAT``).
# Re-exporting them through a module-level ``__getattr__`` means each
# attribute access re-reads ``nepkit_settings`` rather than being frozen at
# import time.
#
# If the user changes ``settings.NEPKIT['BS_DATE_FORMAT']`` via
# ``override_settings`` (or a runtime signal), a fresh
# ``from django_nepkit.utils import BS_DATE_FORMAT`` will see the new value.

__all__ = [
    "BS_DATE_FORMAT",  # noqa: F822  — exposed via module __getattr__
    "BS_DATETIME_FORMAT",  # noqa: F822
    "BS_TIME_FORMAT",  # noqa: F822
    "format_nepali_currency",
    "format_nepali_date",
    "format_nepali_datetime",
    "format_nepali_time",
    "try_parse_nepali_date",
    "try_parse_nepali_datetime",
    "try_parse_nepali_time",
    "get_districts_by_province",
    "get_municipalities_by_district",
    "number_to_nepali_words",
    "english_to_nepali_unicode",
    "normalize_address",
]


_LIVE_SETTINGS = {
    "BS_DATE_FORMAT",
    "BS_DATETIME_FORMAT",
    "BS_TIME_FORMAT",
}


def __getattr__(name):
    if name in _LIVE_SETTINGS:
        return getattr(nepkit_settings, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


# ---------------------------------------------------------------------------
# Parsing
# ---------------------------------------------------------------------------


def _try_parse_nepali(value: Any, cls: Any, fallback_fmt: str) -> Any:
    """Turn a string into a Nepali date/datetime object.

    Returns ``None`` for empty input or when no format matches.  Other
    exceptions (programmer errors, OOM) propagate.
    """
    if value in (None, ""):
        return None
    if isinstance(value, cls):
        return value
    if isinstance(value, str):
        formats = list(nepkit_settings.DATE_INPUT_FORMATS)
        if fallback_fmt not in formats:
            formats.append(fallback_fmt)
        for fmt in formats:
            try:
                return cls.strptime(value.strip(), fmt)
            except _PARSE_ERRORS:
                continue
    return None


def try_parse_nepali_date(value: Any) -> Optional[nepalidate]:
    """Convert any value to a Nepali Date (``None`` on failure)."""
    return _try_parse_nepali(value, nepalidate, nepkit_settings.BS_DATE_FORMAT)


def try_parse_nepali_datetime(value: Any) -> Optional[nepalidatetime]:
    """Convert any value to a Nepali DateTime (``None`` on failure)."""
    return _try_parse_nepali(value, nepalidatetime, nepkit_settings.BS_DATETIME_FORMAT)


# Per-string parse caches used by ``BaseNepaliBSField`` so admin list
# views don't re-parse the same stored string thousands of times per
# request.  The cache key is the raw stored string; the value is the
# parsed object (``None`` when the string is unparseable).  Capping at
# 2048 covers the worst case (all unique dates in a 5-year window of
# ~30k rows) without unbounded growth.
@lru_cache(maxsize=2048)
def _cached_parse_nepali_date(value: str) -> Optional[nepalidate]:
    return try_parse_nepali_date(value)


@lru_cache(maxsize=2048)
def _cached_parse_nepali_datetime(value: str) -> Optional[nepalidatetime]:
    return try_parse_nepali_datetime(value)


def try_parse_nepali_time(value: Any) -> Optional[python_time]:
    """Convert any value to a Python ``time`` (``None`` on failure)."""
    from datetime import datetime as _dt

    if value in (None, ""):
        return None
    if isinstance(value, python_time):
        return value
    if isinstance(value, _dt):
        return value.time()
    if isinstance(value, str):
        formats = list(nepkit_settings.TIME_INPUT_FORMATS)
        if nepkit_settings.BS_TIME_FORMAT not in formats:
            formats.append(nepkit_settings.BS_TIME_FORMAT)
        for fmt in formats:
            try:
                return _dt.strptime(value.strip(), fmt).time()
            except _PARSE_ERRORS:
                continue
    return None


# ---------------------------------------------------------------------------
# Formatting
# ---------------------------------------------------------------------------


def format_nepali_time(value: Any, format_str: Optional[str] = None) -> str:
    """Format a Python ``time``/``datetime`` as a string.

    Returns an empty string for ``None`` and falls back to ``str(value)`` when
    the value cannot be formatted.  Honours ``nepkit_settings.BS_TIME_FORMAT``
    when no explicit format is supplied.
    """
    from datetime import datetime as _dt

    if value is None:
        return ""
    if format_str is None:
        format_str = nepkit_settings.BS_TIME_FORMAT
    if isinstance(value, _dt):
        value = value.time()
    if isinstance(value, python_time):
        try:
            return value.strftime(format_str)
        except (ValueError, TypeError):
            return str(value)
    return str(value)


def format_nepali_date(value: Any, format_str: Optional[str] = None) -> str:
    """Format a ``nepalidate``/``nepalidatetime``/``str`` as a string.

    Returns an empty string for ``None`` and ``str(value)`` for anything
    that can't be parsed.  Honours ``nepkit_settings.BS_DATE_FORMAT``
    when no explicit format is supplied.
    """
    if value is None:
        return ""
    if format_str is None:
        format_str = nepkit_settings.BS_DATE_FORMAT
    if isinstance(value, (nepalidate, nepalidatetime)):
        try:
            return value.strftime(format_str)
        except (ValueError, TypeError):
            return str(value)
    if isinstance(value, str):
        # Already-formatted strings pass through unchanged.
        return value
    return str(value)


def format_nepali_datetime(value: Any, format_str: Optional[str] = None) -> str:
    """Format a ``nepalidatetime`` for display.

    Honours ``nepkit_settings.BS_DATETIME_FORMAT`` when no explicit
    format is supplied.
    """
    if value is None:
        return ""
    if format_str is None:
        format_str = nepkit_settings.BS_DATETIME_FORMAT
    if isinstance(value, nepalidatetime):
        try:
            return value.strftime(format_str)
        except (ValueError, TypeError):
            return str(value)
    if isinstance(value, nepalidate):
        # A pure date stored where a datetime is expected — format as a
        # date and append the default time.
        try:
            return value.strftime(
                format_str.split(" ")[0] if " " in format_str else format_str
            )
        except (ValueError, TypeError):
            return str(value)
    if isinstance(value, str):
        return value
    return str(value)


def format_nepali_currency(
    number: Any, currency_symbol: str = "Rs.", ne: bool = False
) -> str:
    """
    Format a number with Nepali-style commas and optional currency symbol.

    Examples:
        ``1234567``  -> ``Rs. 12,34,567.00``
        ``Decimal('123456789012345.67')`` -> preserves precision
        ``None`` -> ``""``

    Raises:
        ValueError: if ``number`` cannot be coerced to a finite ``Decimal``.
    """
    from nepali.number import add_comma, english_to_nepali

    if number is None:
        return ""
    if isinstance(number, bool):
        raise ValueError(f"Cannot format boolean as currency: {number!r}")

    try:
        amount = Decimal(str(number)) if not isinstance(number, Decimal) else number
    except (InvalidOperation, ValueError) as exc:
        raise ValueError(f"Cannot format {number!r} as currency: {exc}") from exc

    if not amount.is_finite():
        raise ValueError(f"Cannot format non-finite currency value: {number!r}")

    quantized = amount.quantize(Decimal("0.01"))
    sign = "-" if quantized < 0 else ""
    abs_q = -quantized if quantized < 0 else quantized
    integer_part, _, decimal_part = format(abs_q, "f").partition(".")
    formatted_integer = add_comma(int(integer_part))
    res = (
        f"{formatted_integer}.{decimal_part or '00'}"
        if "." in format(abs_q, "f") or decimal_part
        else f"{formatted_integer}.00"
    )

    if ne:
        res = english_to_nepali(res)

    if currency_symbol:
        return f"{currency_symbol} {sign}{res}"
    return f"{sign}{res}"


# ---------------------------------------------------------------------------
# Nepali words
# ---------------------------------------------------------------------------


def number_to_nepali_words(number: Any) -> str:
    """
    Convert a number to Nepali words.

    Examples:
        ``123`` -> ``एक सय तेईस``
        ``-25`` -> ``ऋणात्मक पच्चीस``

    Raises:
        ValueError: if ``number`` cannot be coerced to an int.
    """
    if number is None:
        return ""

    try:
        if isinstance(number, bool):
            raise ValueError(f"Cannot convert boolean to words: {number!r}")
        if isinstance(number, Decimal):
            if not number.is_finite():
                raise ValueError(f"Cannot convert non-finite Decimal: {number!r}")
            num = int(number)
        else:
            num = int(Decimal(str(number)).quantize(Decimal("1")))
    except (InvalidOperation, ValueError, TypeError) as exc:
        raise ValueError(f"Cannot convert {number!r} to Nepali words: {exc}") from exc

    if num == 0:
        return "शून्य"

    def _convert(n: int) -> str:
        if n == 0:
            return ""
        if n < 0:
            return f"{NEGATIVE_PREFIX} {_convert(-n)}".strip()
        if n < 100:
            return NEPALI_ONES[n]
        for i in range(len(NEPALI_UNITS) - 1, 0, -1):
            div, unit_name = NEPALI_UNITS[i]
            if n >= div:
                prefix_val = n // div
                remainder = n % div
                prefix_words = _convert(prefix_val)
                res = f"{prefix_words} {unit_name}".strip()
                if remainder > 0:
                    res = f"{res} {_convert(remainder)}"
                return res.strip()
        return ""

    return _convert(num)


def english_to_nepali_unicode(text: Any) -> str:
    """Convert English digits in ``text`` to Nepali Unicode digits."""
    from nepali.number import english_to_nepali

    if text is None:
        return ""
    return english_to_nepali(text)


# ---------------------------------------------------------------------------
# Location data
# ---------------------------------------------------------------------------


def _normalize_nepali_text(text):
    """Normalize Nepali text for easier matching.

    Replaces Chandrabindu with Anusvara so that variant spellings of the
    same place name (e.g. काठमाडौँ vs काठमाडौं) compare equal.
    """
    if not text:
        return text
    return text.replace("ँ", "ं").replace("ाँ", "ां")


def get_districts_by_province(province_name, ne=False, en=True):
    """Get all districts for a province."""
    return _get_location_children(provinces, province_name, "districts", ne=ne)


def get_municipalities_by_district(district_name, ne=False, en=True):
    """Get all municipalities for a district."""
    return _get_location_children(districts, district_name, "municipalities", ne=ne)


def _get_location_children(parent_list, parent_name, child_attr, ne=False):
    selected_parent = None
    for p in parent_list:
        p_name = p.name
        p_name_ne = getattr(p, "name_nepali", None)
        if p_name == parent_name or p_name_ne == parent_name:
            selected_parent = p
            break
    if not selected_parent:
        return []
    children = getattr(selected_parent, child_attr, [])
    if ne:
        return [
            {
                "id": getattr(child, "name_nepali", child.name),
                "text": getattr(child, "name_nepali", child.name),
            }
            for child in children
        ]
    return [{"id": child.name, "text": child.name} for child in children]


# ---------------------------------------------------------------------------
# Address normalization
# ---------------------------------------------------------------------------

# Rank higher = better match.  Used to pick the best candidate when a token
# matches multiple location names.  Exact > substring so that the most
# precise match always wins.
_MATCH_RANK_EXACT = 100
_MATCH_RANK_SUBSTRING = 20

# Minimum lengths for substring matches (avoid matching single characters).
_MIN_EN_SUBSTRING = 4
_MIN_NE_SUBSTRING = 2


def _classify_match(
    token, token_lower, name_eng, name_eng_lower, name_nep, name_nep_norm
):
    """Return a (rank, matched_name) tuple or ``None`` if there's no match.

    The caller is expected to take the highest-ranked candidate.
    """
    # Nepali exact (case-sensitive, since the script has no case).
    if name_nep and token == name_nep:
        return (_MATCH_RANK_EXACT, name_eng)
    if name_nep and name_nep_norm and token == name_nep_norm:
        return (_MATCH_RANK_EXACT, name_eng)
    # English exact (case-insensitive).
    if name_eng and token_lower == name_eng_lower:
        return (_MATCH_RANK_EXACT, name_eng)
    # English substring (length-guarded to avoid false positives).
    if len(token) >= _MIN_EN_SUBSTRING and name_eng and token_lower in name_eng_lower:
        return (_MATCH_RANK_SUBSTRING, name_eng)
    # Nepali substring
    if len(token) >= _MIN_NE_SUBSTRING and name_nep_norm and token in name_nep_norm:
        return (_MATCH_RANK_SUBSTRING, name_eng)
    return None


def _matches_location_name(name_eng, name_nep, token, normalized_token):
    """Boolean wrapper around :func:`_classify_match`.

    Returns ``True`` when ``token`` matches either the English or Nepali
    name according to the same rules used by
    :func:`_find_location_in_tokens`.  Kept for backwards compatibility
    with existing test suites.
    """
    classified = _classify_match(
        token,
        token.lower(),
        name_eng,
        (name_eng or "").lower(),
        name_nep,
        _normalize_nepali_text(name_nep),
    )
    return classified is not None


def _find_location_in_tokens(location_list, tokens, normalized_tokens):
    """Find the best-matching location for any of ``tokens``.

    Returns the location object, or ``None`` if nothing matches.  When
    multiple candidates match, the one with the highest rank wins; ties
    are broken by the first token that produced the match.

    ``normalized_tokens`` is accepted for API stability but is currently
    unused (ranking is done on the ASCII-folded form of each token).
    """
    del normalized_tokens  # currently unused; kept for API symmetry
    best = None
    best_rank = -1
    for token in tokens:
        for location in location_list:
            name_eng = location.name
            name_eng_lower = name_eng.lower() if name_eng else ""
            name_nep = getattr(location, "name_nepali", None) or ""
            name_nep_norm = _normalize_nepali_text(name_nep)
            classified = _classify_match(
                token, token.lower(), name_eng, name_eng_lower, name_nep, name_nep_norm
            )
            if classified is None:
                continue
            rank, _ = classified
            if rank > best_rank:
                best_rank = rank
                best = location
                if rank == _MATCH_RANK_EXACT:
                    return best
    return best


def _is_nepali_text(tokens):
    """Check if any token contains Devanagari characters."""
    return any(re.search(r"[\u0900-\u097F]", t) for t in tokens)


@lru_cache(maxsize=1024)
def _find_address_components(address_string: str):
    """Resolve the (municipality, district, province) location objects.

    Memoised on ``address_string`` (the input is a small string and the
    location data is static).  Returns ``(None, None, None)`` for empty
    input.  The location objects come from ``nepali.locations`` and are
    safe to share across callers.
    """
    if not address_string:
        return None, None, None

    content = address_string.replace(",", " ").replace("-", " ")
    tokens = [t.strip() for t in content.split() if t.strip()]
    normalized_tokens = [_normalize_nepali_text(t) for t in tokens]

    found_municipality = _find_location_in_tokens(
        municipalities, tokens, normalized_tokens
    )
    found_district = _find_location_in_tokens(districts, tokens, normalized_tokens)
    found_province = _find_location_in_tokens(provinces, tokens, normalized_tokens)

    if found_municipality:
        if not found_district:
            found_district = found_municipality.district
        if not found_province:
            found_province = found_municipality.province
    if found_district and not found_province:
        found_province = found_district.province

    return found_municipality, found_district, found_province


def normalize_address(address_string: str) -> dict[str, Optional[str]]:
    """
    Best-effort: split a Nepali address string into Province, District, and
    Municipality.

    Returns a dict with the (English) names of the matched locations, or
    their Nepali names if the input contains Devanagari.  The heavy
    matching is memoised on ``address_string``; each call still returns
    a fresh dict so callers can mutate the result without affecting the
    cache.
    """
    result: dict[str, Optional[str]] = {
        "province": None,
        "district": None,
        "municipality": None,
    }
    if not address_string:
        return result

    tokens = [t.strip() for t in address_string.split() if t.strip()]
    is_nepali = _is_nepali_text(tokens)

    municipality, district, province = _find_address_components(address_string)

    def _name(loc):
        if loc is None:
            return None
        return loc.name_nepali if is_nepali else loc.name

    result["municipality"] = _name(municipality)
    result["district"] = _name(district)
    result["province"] = _name(province)
    return result
