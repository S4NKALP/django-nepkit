from __future__ import annotations

from typing import Any, Optional

from nepali.datetime import nepalidate, nepalidatetime
from nepali.locations import districts, municipalities, provinces

from django_nepkit.conf import nepkit_settings

BS_DATE_FORMAT = nepkit_settings.BS_DATE_FORMAT
BS_DATETIME_FORMAT = nepkit_settings.BS_DATETIME_FORMAT


def _try_parse_nepali(value: Any, cls: Any, fallback_fmt: str) -> Any:
    """Helper to turn a string into a Nepali date object."""
    if value in (None, ""):
        return None
    if isinstance(value, cls):
        return value
    if isinstance(value, str):
        formats = nepkit_settings.DATE_INPUT_FORMATS
        if fallback_fmt not in formats:
            formats = list(formats) + [fallback_fmt]

        for fmt in formats:
            try:
                return cls.strptime(value.strip(), fmt)
            except Exception:
                continue
    return None


def try_parse_nepali_date(value: Any) -> Optional[nepalidate]:
    """Convert any value to a Nepali Date."""
    return _try_parse_nepali(value, nepalidate, BS_DATE_FORMAT)


def try_parse_nepali_datetime(value: Any) -> Optional[nepalidatetime]:
    """Convert any value to a Nepali Date and Time."""
    return _try_parse_nepali(value, nepalidatetime, BS_DATETIME_FORMAT)


def _get_location_children(parent_list, parent_name, child_attr, ne=False):
    """Find children (like districts) of a parent (like a province)."""
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
    else:
        return [{"id": child.name, "text": child.name} for child in children]


def get_districts_by_province(province_name, ne=False, en=True):
    """Get all districts for a province."""
    # Logic note: if ne=True is passed, we shouldn't care about en=True (handled by caller typically)
    return _get_location_children(provinces, province_name, "districts", ne=ne)


def get_municipalities_by_district(district_name, ne=False, en=True):
    """Get all municipalities for a district."""
    return _get_location_children(districts, district_name, "municipalities", ne=ne)


def format_nepali_currency(
    number: Any, currency_symbol: str = "Rs.", ne: bool = False
) -> str:
    """
    Formats a number with Nepali-style commas and optional currency symbol.
    Eg. 1234567 -> Rs. 12,34,567
    """
    from nepali.number import add_comma, english_to_nepali

    if number is None:
        return ""

    try:
        # Convert to string and split by decimal point
        num_str = f"{float(number):.2f}"
        if "." in num_str:
            integer_part, decimal_part = num_str.split(".")
        else:
            integer_part, decimal_part = num_str, ""

        # Format integer part with commas
        formatted_integer = add_comma(int(integer_part))

        # Join back
        res = formatted_integer
        if decimal_part:
            res = f"{res}.{decimal_part}"

        if ne:
            res = english_to_nepali(res)

        if currency_symbol:
            return f"{currency_symbol} {res}"
        return res
    except Exception:
        return str(number)


def number_to_nepali_words(number: Any) -> str:
    """
    Converts a number to Nepali words.
    Eg. 123 -> एक सय तेईस
    """
    from django_nepkit.constants import NEPALI_ONES, NEPALI_UNITS

    if number is None:
        return ""

    try:
        num = int(float(number))
    except (ValueError, TypeError):
        return str(number)

    if num == 0:
        return "शून्य"

    def _convert(n):
        if n == 0:
            return ""
        if n < 100:
            return NEPALI_ONES[n]

        for i in range(len(NEPALI_UNITS) - 1, 0, -1):
            div, unit_name = NEPALI_UNITS[i]
            if n >= div:
                prefix_val = n // div
                remainder = n % div

                # For 'सय' (100), we use NEPALI_ONES[prefix_val]
                # For others, we might need recursive calls if prefix_val >= 100
                prefix_words = _convert(prefix_val)
                res = f"{prefix_words} {unit_name}"
                if remainder > 0:
                    res += f" {_convert(remainder)}"
                return res.strip()
        return ""

    return _convert(num)


def english_to_nepali_unicode(text: Any) -> str:
    """
    Converts English text/numbers to Nepali Unicode.
    Currently focuses on numbers.
    """
    from nepali.number import english_to_nepali

    if text is None:
        return ""

    return english_to_nepali(text)


def _normalize_nepali_text(text):
    """
    Normalize Nepali text for easier matching.
    Replaces Chandrabindu with Anusvara.
    """
    if not text:
        return text
    return text.replace("ँ", "ं").replace("ाँ", "ां")


def _matches_location_name(name_eng, name_nep, token, normalized_token):
    """
    Check if a token matches a location name (English or Nepali).

    Args:
        name_eng: English name of location
        name_nep: Nepali name of location
        token: Original token to match
        normalized_token: Normalized version of token

    Returns:
        True if token matches the location name
    """
    token_lower = token.lower()
    name_nep_norm = _normalize_nepali_text(name_nep)

    # Exact matches
    if (
        token == name_nep
        or normalized_token == name_nep_norm
        or token_lower == name_eng.lower()
    ):
        return True

    # Partial matches for English (e.g., "Pokhara" in "Pokhara Metropolitan City")
    # Only if token is at least 4 characters to avoid too many false positives
    if len(token) >= 4:
        if token_lower in name_eng.lower():
            return True

    # Partial matches for Nepali
    if len(normalized_token) >= 2:
        if normalized_token in name_nep_norm:
            return True

    return False


def _find_location_in_tokens(location_list, tokens, normalized_tokens):
    """
    Find a location from a list by matching against tokens.

    Args:
        location_list: List of location objects to search
        tokens: List of original tokens
        normalized_tokens: List of normalized tokens

    Returns:
        Matching location object or None
    """
    for i, token in enumerate(tokens):
        nt = normalized_tokens[i]
        for location in location_list:
            if _matches_location_name(location.name, location.name_nepali, token, nt):
                return location
    return None


def _is_nepali_text(tokens):
    """Check if any token contains Devanagari characters."""
    import re

    return any(re.search(r"[\u0900-\u097F]", t) for t in tokens)


def normalize_address(address_string: str) -> dict[str, Optional[str]]:
    """
    Attempts to normalize a Nepali address string into Province, District, and Municipality.
    Returns a dictionary with 'province', 'district', and 'municipality'.
    """
    if not address_string:
        return {"province": None, "district": None, "municipality": None}

    result: dict[str, Optional[str]] = {
        "province": None,
        "district": None,
        "municipality": None,
    }

    # Prepare tokens
    content = address_string.replace(",", " ").replace("-", " ")
    tokens = [t.strip() for t in content.split() if t.strip()]
    normalized_tokens = [_normalize_nepali_text(t) for t in tokens]

    # Find locations - most specific to least specific
    found_municipality = _find_location_in_tokens(
        municipalities, tokens, normalized_tokens
    )
    found_district = _find_location_in_tokens(districts, tokens, normalized_tokens)
    found_province = _find_location_in_tokens(provinces, tokens, normalized_tokens)

    # Fill in the gaps using hierarchy
    if found_municipality:
        result["municipality"] = found_municipality.name
        if not found_district:
            found_district = found_municipality.district
        if not found_province:
            found_province = found_municipality.province

    if found_district:
        result["district"] = found_district.name
        if not found_province:
            found_province = found_district.province

    if found_province:
        result["province"] = found_province.name

    # Use Nepali names if input contains Nepali text
    if _is_nepali_text(tokens):
        if found_municipality:
            result["municipality"] = found_municipality.name_nepali
        if found_district:
            result["district"] = found_district.name_nepali
        if found_province:
            result["province"] = found_province.name_nepali

    return result
