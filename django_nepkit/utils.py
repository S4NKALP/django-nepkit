from __future__ import annotations

from typing import Any, Optional

from nepali.datetime import nepalidate, nepalidatetime


BS_DATE_FORMAT = "%Y-%m-%d"
BS_DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"


def try_parse_nepali_date(value: Any) -> Optional[nepalidate]:
    """
    Best-effort conversion to `nepalidate`.

    - Returns `None` for empty values.
    - Returns `nepalidate` for valid inputs.
    - Returns `None` if the value cannot be parsed.

    Callers decide whether to raise, fallback, etc.
    """
    if value in (None, ""):
        return None
    if isinstance(value, nepalidate):
        return value
    if isinstance(value, str):
        try:
            return nepalidate.strptime(value.strip(), BS_DATE_FORMAT)
        except Exception:
            return None
    return None


def try_parse_nepali_datetime(value: Any) -> Optional[nepalidatetime]:
    """
    Best-effort conversion to `nepalidatetime`.

    - Returns `None` for empty values.
    - Returns `nepalidatetime` for valid inputs.
    - Returns `None` if the value cannot be parsed.

    Callers decide whether to raise, fallback, etc.
    """
    if value in (None, ""):
        return None
    if isinstance(value, nepalidatetime):
        return value
    if isinstance(value, str):
        try:
            return nepalidatetime.strptime(value.strip(), BS_DATETIME_FORMAT)
        except Exception:
            return None
    return None


def get_districts_by_province(province_name):
    """
    Returns a list of districts in the given province.
    """
    from nepali.locations import provinces

    selected_province = next((p for p in provinces if p.name == province_name), None)
    if not selected_province:
        return []
    return [{"id": d.name, "text": d.name} for d in selected_province.districts]


def get_municipalities_by_district(district_name):
    """
    Returns a list of municipalities in the given district.
    """
    from nepali.locations import districts

    selected_district = next((d for d in districts if d.name == district_name), None)
    if not selected_district:
        return []
    return [{"id": m.name, "text": m.name} for m in selected_district.municipalities]
