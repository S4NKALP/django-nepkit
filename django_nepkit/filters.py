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
    """

    def filter(self, qs: QuerySet, value: Any) -> QuerySet:
        if value:
            from django_nepkit.utils import BS_DATE_FORMAT

            # Find the date separator (e.g., '-' in '2080-01-01')
            if BS_DATE_FORMAT.startswith("%Y"):
                separator = BS_DATE_FORMAT[2] if len(BS_DATE_FORMAT) > 2 else "-"
                return qs.filter(
                    **{f"{self.field_name}__startswith": f"{value}{separator}"}
                )

            # Fallback if the format is unusual
            return qs.filter(**{f"{self.field_name}__icontains": str(value)})
        return qs


class NepaliDateMonthFilter(filters.NumberFilter):
    """
    A filter for `NepaliDateField` that allows filtering by Bikram Sambat Month.
    Expects an integer month (1-12).
    """

    def filter(self, qs: QuerySet, value: Any) -> QuerySet:
        if value:
            from django_nepkit.utils import BS_DATE_FORMAT

            month_str = f"{int(value):02d}"

            # Standard format: look for '-01-' for Baisakh
            if BS_DATE_FORMAT == "%Y-%m-%d":
                return qs.filter(**{f"{self.field_name}__contains": f"-{month_str}-"})

            # Adaptive check for other separators
            separator = BS_DATE_FORMAT[2] if len(BS_DATE_FORMAT) > 2 else "-"
            return qs.filter(
                **{f"{self.field_name}__contains": f"{separator}{month_str}{separator}"}
            )
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
