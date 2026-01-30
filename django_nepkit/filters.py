from __future__ import annotations

from typing import Any

from django.db.models import QuerySet

try:
    from django_filters import rest_framework as filters
except ImportError as e:
    raise ModuleNotFoundError(
        "django-nepkit filter support is optional. Install with `django-nepkit[drf]` "
        "to use `django_nepkit.filters`."
    ) from e


class NepaliDateYearFilter(filters.NumberFilter):
    """
    A filter for `NepaliDateField` that allows filtering by Bikram Sambat Year.
    Expects an integer year (e.g., 2080).

    Usage:
        year = NepaliDateYearFilter(field_name="dob")
    """

    def filter(self, qs: QuerySet, value: Any) -> QuerySet:
        if value:
            # Since date is stored as "YYYY-MM-DD" string
            return qs.filter(**{f"{self.field_name}__startswith": f"{value}-"})
        return qs


class NepaliDateRangeFilter(filters.BaseRangeFilter, filters.CharFilter):
    """
    A filter for `NepaliDateField` that allows filtering by a range of BS dates.
    Expects two BS strings separated by a comma (e.g., "2080-01-01,2080-12-30").
    """

    def filter(self, qs: QuerySet, value: Any) -> QuerySet:
        if value:
            if len(value) == 2:
                return qs.filter(**{f"{self.field_name}__range": (value[0], value[1])})
        return qs
