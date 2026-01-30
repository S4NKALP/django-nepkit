from __future__ import annotations

from typing import Any, Optional

from nepali.datetime import nepalidate, nepalidatetime
from nepali.locations import districts, provinces

BS_DATE_FORMAT = "%Y-%m-%d"
BS_DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"


def _try_parse_nepali(value: Any, cls: Any, fmt: str) -> Any:
    """Internal helper to parse Nepali date/datetime."""
    if value in (None, ""):
        return None
    if isinstance(value, cls):
        return value
    if isinstance(value, str):
        try:
            return cls.strptime(value.strip(), fmt)
        except Exception:
            return None
    return None


def try_parse_nepali_date(value: Any) -> Optional[nepalidate]:
    """
    Best-effort conversion to `nepalidate`.
    """
    return _try_parse_nepali(value, nepalidate, BS_DATE_FORMAT)


def try_parse_nepali_datetime(value: Any) -> Optional[nepalidatetime]:
    """
    Best-effort conversion to `nepalidatetime`.
    """
    return _try_parse_nepali(value, nepalidatetime, BS_DATETIME_FORMAT)


def _get_location_children(parent_list, parent_name, child_attr, ne=False):
    """
    Internal helper to finding a parent in a list and returning its children (districts/municipalities).
    """
    selected_parent = None
    for p in parent_list:
        p_name = p.name
        p_name_ne = getattr(p, "name_nepali", None)

        # Mapping fix for lookups
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
    """
    Returns a list of districts in the given province.
    """
    # Logic note: if ne=True is passed, we shouldn't care about en=True (handled by caller typically)
    return _get_location_children(provinces, province_name, "districts", ne=ne)


def get_municipalities_by_district(district_name, ne=False, en=True):
    """
    Returns a list of municipalities in the given district.
    """
    return _get_location_children(districts, district_name, "municipalities", ne=ne)
