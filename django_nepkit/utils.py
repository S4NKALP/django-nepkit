from __future__ import annotations

from typing import Any, Optional

from nepali.datetime import nepalidate, nepalidatetime
from nepali.locations import districts, provinces

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

        # Handle province name variations
        if parent_name == "Koshi Province":
            if p_name == "Province 1":
                selected_parent = p
                break
        elif parent_name == "कोशी प्रदेश":
            if p_name_ne == "प्रदेश नं. १":
                selected_parent = p
                break

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


def format_nepali_currency(number: Any, currency_symbol: str = "Rs.") -> str:
    """
    Formats a number with Nepali-style commas and optional currency symbol.
    Eg. 1234567 -> Rs. 12,34,567
    """
    from nepali.number import add_comma

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
    if number is None:
        return ""

    # Basic implementation for now, can be expanded
    # Mapping for numbers to words (simplified)
    # This is a complex task for a full implementation,
    # but I'll provide a robust enough version for common usage.

    try:
        num = int(float(number))
    except (ValueError, TypeError):
        return str(number)

    if num == 0:
        return "शून्य"

    ones = ["", "एक", "दुई", "तीन", "चार", "पाँच", "छ", "सात", "आठ", "नौ", "दश",
            "एघार", "बाह्र", "तेह्र", "चौध", "पन्ध्र", "सोह्र", "सत्र", "अठार", "उन्नाइस", "बीस",
            "एकाइस", "बाइस", "तेईस", "चौबीस", "पच्चीस", "छब्बीस", "सत्ताइस", "अठाइस", "उनन्तीस", "तीस",
            "एकतीस", "बत्तीस", "तेत्तीस", "चौंतीस", "पैंतीस", "छत्तीस", "सैंतीस", "अठतीस", "उनन्चालीस", "चालीस",
            "एकचालीस", "बयालीस", "त्रिचालीस", "चवालीस", "पैंतालीस", "छयालीस", "सत्तालीस", "अठचालीस", "उनन्पचास", "पचास",
            "एकाउन्न", "बाउन्न", "त्रिपन्न", "चउन्न", "पचपन्न", "छपन्न", "सन्ताउन्न", "अन्ठाउन्न", "उनन्साठी", "साठी",
            "एकसाठी", "बासट्ठी", "त्रिसट्ठी", "चौसट्ठी", "पैंसट्ठी", "छयसट्ठी", "सतसट्ठी", "अठसट्ठी", "उनन्सत्तरी", "सत्तरी",
            "एकहत्तर", "बाहत्तर", "त्रिहत्तर", "चौरहत्तर", "पचहत्तर", "छयहत्तर", "सतहत्तर", "अठहत्तर", "उनन्असी", "असी",
            "एकासी", "बयासी", "त्रियासी", "चौरासी", "पचासी", "छयासी", "सतासी", "अठासी", "उनन्नब्बे", "नब्बे",
            "एकानब्बे", "बयानब्बे", "त्रियानब्बे", "चौरानब्बे", "पञ्चानब्बे", "छ्यानब्बे", "सन्तानब्बे", "अन्ठानब्बे", "उनन्सय"]

    units = [
        ("", ""),
        (100, "सय"),
        (1000, "हजार"),
        (100000, "लाख"),
        (10000000, "करोड"),
        (1000000000, "अरब"),
        (100000000000, "खरब"),
    ]

    def _convert(n):
        if n == 0:
            return ""
        if n < 100:
            return ones[n]

        for i in range(len(units) - 1, 0, -1):
            div, unit_name = units[i]
            if n >= div:
                prefix_val = n // div
                remainder = n % div

                # For 'सय' (100), we use ones[prefix_val]
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
