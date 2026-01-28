from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from nepali.datetime import nepalidate, nepalidatetime

from django_nepkit.models import NepaliDateField


# --------------------------------------------------
# Internal helpers
# --------------------------------------------------

def _parse_nepali_date(value):
    """
    Normalize string / nepalidate to nepalidate.
    """
    if value is None:
        return None

    if isinstance(value, nepalidate):
        return value

    if isinstance(value, str):
        try:
            return nepalidate.strptime(value, "%Y-%m-%d")
        except (ValueError, TypeError):
            return None

    return None


def _parse_nepali_datetime(value):
    """
    Normalize string / nepalidatetime to nepalidatetime.
    """
    if value is None:
        return None

    if isinstance(value, nepalidatetime):
        return value

    if isinstance(value, str):
        try:
            return nepalidatetime.strptime(value, "%Y-%m-%d %H:%M:%S")
        except (ValueError, TypeError):
            return None

    return None


# --------------------------------------------------
# Formatting helpers
# --------------------------------------------------

def format_nepali_date(value, format_string="%B %d, %Y"):
    """
    Format a Nepali (BS) date with Nepali month names.
    """
    nd = _parse_nepali_date(value)
    return nd.strftime(format_string) if nd else ""


def format_nepali_datetime(value, format_string="%B %d, %Y %I:%M %p"):
    """
    Format a Nepali (BS) datetime (12-hour format by default).
    """
    ndt = _parse_nepali_datetime(value)
    return ndt.strftime(format_string) if ndt else ""


# --------------------------------------------------
# Admin List Filter (BS Year)
# --------------------------------------------------

class NepaliDateFilter(admin.FieldListFilter):
    """
    Admin list filter for NepaliDateField by BS year.
    """

    title = _("Nepali Date (Year)")

    def __init__(self, field, request, params, model, model_admin, field_path):
        self.field_path = field_path
        self.parameter_name = f"{field_path}_bs_year"
        super().__init__(field, request, params, model, model_admin, field_path)

    def expected_parameters(self):
        return [self.parameter_name]

    def _year_choices(self):
        current_year = nepalidate.today().year
        return range(current_year - 10, current_year + 2)

    def choices(self, changelist):
        yield {
            "selected": self.parameter_name not in self.used_parameters,
            "query_string": changelist.get_query_string(remove=[self.parameter_name]),
            "display": _("All"),
        }

        for year in self._year_choices():
            yield {
                "selected": self.used_parameters.get(self.parameter_name) == str(year),
                "query_string": changelist.get_query_string(
                    {self.parameter_name: year}
                ),
                "display": year,
            }

    def queryset(self, request, queryset):
        value = self.used_parameters.get(self.parameter_name)
        if not value:
            return queryset

        try:
            year = int(value)
        except (TypeError, ValueError):
            return queryset

        start_bs = nepalidate(year, 1, 1)

        # BS year length varies (30/31 days)
        for last_day in (31, 30):
            try:
                end_bs = nepalidate(year, 12, last_day)
                break
            except ValueError:
                continue

        return queryset.filter(
            **{
                f"{self.field_path}__range": (
                    start_bs.to_date(),
                    end_bs.to_date(),
                )
            }
        )


# Register filter automatically for NepaliDateField
admin.FieldListFilter.register(
    lambda f: isinstance(f, NepaliDateField),
    NepaliDateFilter,
    take_priority=True,
)


# --------------------------------------------------
# Admin mixins
# --------------------------------------------------

class NepaliAdminMixin:
    """
    Adds Nepali date formatting helpers to admin classes.
    """

    format_nepali_date = staticmethod(format_nepali_date)
    format_nepali_datetime = staticmethod(format_nepali_datetime)


class NepaliModelAdmin(NepaliAdminMixin, admin.ModelAdmin):
    """
    Base ModelAdmin with Nepali utilities.

    Example:
        @admin.register(MyModel)
        class MyModelAdmin(NepaliModelAdmin):
            list_filter = (('date_bs', NepaliDateFilter),)

            def date_display(self, obj):
                return self.format_nepali_date(obj.date_bs)
    """

    NepaliDateFilter = NepaliDateFilter
