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
