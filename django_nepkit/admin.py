from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from nepali.datetime import nepalidate, nepalidatetime

from django_nepkit.models import NepaliDateField


def format_nepali_date(date_value, format_string="%B %d, %Y"):
    """
    Format a nepalidate object with Nepali month names.

    Args:
        date_value: A nepalidate object or string in YYYY-MM-DD format
        format_string: strftime format string (default: '%B %d, %Y')
                      %B = Full month name (Baishak, Jestha, etc.)
                      %b = Short month name
                      %d = Day of month
                      %Y = Year

    Returns:
        Formatted date string with Nepali month names, or empty string if invalid
    """

    if date_value is None:
        return ""

    try:
        if isinstance(date_value, str):
            date_value = nepalidate.strptime(date_value, "%Y-%m-%d")

        if isinstance(date_value, nepalidate):
            return date_value.strftime(format_string)
    except (ValueError, TypeError, AttributeError):
        pass

    return str(date_value) if date_value else ""


def format_nepali_datetime(datetime_value, format_string="%B %d, %Y %I:%M %p"):
    """
    Format a nepalidatetime object with Nepali month names.

    Default output uses **12-hour time with AM/PM**.
    """
    if datetime_value is None:
        return ""

    try:
        if isinstance(datetime_value, str):
            datetime_value = nepalidatetime.strptime(
                datetime_value, "%Y-%m-%d %H:%M:%S"
            )

        if isinstance(datetime_value, nepalidatetime):
            return datetime_value.strftime(format_string)
    except (ValueError, TypeError, AttributeError):
        pass

    return str(datetime_value) if datetime_value else ""


class NepaliDateFilter(admin.FieldListFilter):
    """
    A list filter for NepaliDateField to filter by BS Year.
    """

    def __init__(self, field, request, params, model, model_admin, field_path):
        self.parameter_name = f"{field_path}_bs_year"
        super().__init__(field, request, params, model, model_admin, field_path)
        self.title = _("Nepali Date (Year)")

    def expected_parameters(self):
        return [self.parameter_name]

    def choices(self, changelist):
        yield {
            "selected": self.used_parameters.get(self.parameter_name) is None,
            "query_string": changelist.get_query_string(remove=[self.parameter_name]),
            "display": _("All"),
        }
        current_year = nepalidate.today().year
        for year in range(current_year - 10, current_year + 2):
            yield {
                "selected": self.used_parameters.get(self.parameter_name) == str(year),
                "query_string": changelist.get_query_string(
                    {self.parameter_name: str(year)}
                ),
                "display": str(year),
            }

    def queryset(self, request, queryset):
        value = self.used_parameters.get(self.parameter_name)
        if value:
            year = int(value)
            # Convert BS year range to AD date range
            start_date_bs = nepalidate(year, 1, 1)
            # Find last day of the year. Some BS years end on the 30th,
            # so we try 31 first and then fall back to 30 if that date
            # is not valid.
            try:
                end_date_bs = nepalidate(year, 12, 31)
            except ValueError:
                end_date_bs = nepalidate(year, 12, 30)

            start_date_ad = start_date_bs.to_date()
            end_date_ad = end_date_bs.to_date()

            return queryset.filter(
                **{f"{self.field_path}__range": (start_date_ad, end_date_ad)}
            )
        return queryset


admin.FieldListFilter.register(
    lambda f: isinstance(f, NepaliDateField), NepaliDateFilter, take_priority=True
)


class NepaliAdminMixin:
    """
    Mixin for Django admin classes that provides Nepali date utilities.
    Makes format_nepali_date and NepaliDateFilter available without explicit imports.
    """

    def format_nepali_date(self, date_value, format_string="%B %d, %Y"):
        """
        Format a nepalidate object with Nepali month names.
        Available as a method on admin classes using this mixin.
        """
        return format_nepali_date(date_value, format_string)

    def format_nepali_datetime(
        self, datetime_value, format_string="%B %d, %Y %I:%M %p"
    ):
        return format_nepali_datetime(datetime_value, format_string)


class NepaliModelAdmin(NepaliAdminMixin, admin.ModelAdmin):
    """
    Base ModelAdmin class with Nepali date utilities built-in.
    Use this instead of admin.ModelAdmin to have format_nepali_date available.

    Example:
        from django_nepkit import NepaliModelAdmin, NepaliDateFilter

        @admin.register(MyModel)
        class MyModelAdmin(NepaliModelAdmin):
            list_filter = (('date_field', NepaliDateFilter),)

            def display_date(self, obj):
                return self.format_nepali_date(obj.date_field)
    """

    # Make NepaliDateFilter available as a class attribute
    NepaliDateFilter = NepaliDateFilter
