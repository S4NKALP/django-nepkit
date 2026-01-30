from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from nepali.datetime import nepalidate, nepalidatetime

from django_nepkit.models import NepaliDateField, NepaliDateTimeField
from django_nepkit.utils import (
    try_parse_nepali_date,
    try_parse_nepali_datetime,
)


def _format_nepali_common(value, try_parse_func, format_string, ne, cls_type):
    """Internal helper for formatting Nepali objects."""
    if value is None:
        return ""

    try:
        parsed = try_parse_func(value)
        if parsed is not None:
            if ne and hasattr(parsed, "strftime_ne"):
                return parsed.strftime_ne(format_string)
            return parsed.strftime(format_string)
        if isinstance(value, cls_type):
            if ne and hasattr(value, "strftime_ne"):
                return value.strftime_ne(format_string)
            return value.strftime(format_string)
    except (ValueError, TypeError, AttributeError):
        pass

    return str(value) if value else ""


def format_nepali_date(date_value, format_string="%B %d, %Y", ne=False):
    """
    Format a nepalidate object with Nepali month names.
    """
    return _format_nepali_common(
        date_value, try_parse_nepali_date, format_string, ne, nepalidate
    )


def format_nepali_datetime(
    datetime_value, format_string="%B %d, %Y %I:%M %p", ne=False
):
    """
    Format a nepalidatetime object with Nepali month names.
    """
    return _format_nepali_common(
        datetime_value, try_parse_nepali_datetime, format_string, ne, nepalidatetime
    )


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


# Register NepaliDateFilter as the default list filter for NepaliDateField
admin.FieldListFilter.register(
    lambda f: isinstance(f, NepaliDateField),
    NepaliDateFilter,
    take_priority=True,
)


class NepaliAdminMixin:
    """
    Mixin for Django admin classes that provides Nepali date utilities.
    Makes format_nepali_date and NepaliDateFilter available without explicit imports.
    """

    def _get_field_ne_setting(self, field_name):
        """
        Get the 'ne' setting from a model field.

        Args:
            field_name: Name of the field in the model

        Returns:
            True if field has ne=True, False otherwise
        """
        if not hasattr(self, "model"):
            return False

        try:
            field = self.model._meta.get_field(field_name)
            if hasattr(field, "ne"):
                return field.ne
        except (AttributeError, LookupError):
            pass

        return False

    def format_nepali_date(
        self, date_value, format_string="%B %d, %Y", ne=None, field_name=None
    ):
        """
        Format a nepalidate object with Nepali month names.
        Available as a method on admin classes using this mixin.

        Args:
            date_value: A nepalidate object or string
            format_string: strftime format string
            ne: If True, format using Devanagari script. If None, auto-detect from field (default: None)
            field_name: Name of the field to auto-detect 'ne' setting from (optional)
        """
        # Auto-detect 'ne' from field if not explicitly provided
        if ne is None and field_name:
            ne = self._get_field_ne_setting(field_name)
        elif ne is None:
            ne = False

        return format_nepali_date(date_value, format_string, ne=ne)

    def format_nepali_datetime(
        self,
        datetime_value,
        format_string="%B %d, %Y %I:%M %p",
        ne=None,
        field_name=None,
    ):
        """
        Format a nepalidatetime object with Nepali month names.

        Args:
            datetime_value: A nepalidatetime object or string
            format_string: strftime format string
            ne: If True, format using Devanagari script. If None, auto-detect from field (default: None)
            field_name: Name of the field to auto-detect 'ne' setting from (optional)
        """
        # Auto-detect 'ne' from field if not explicitly provided
        if ne is None and field_name:
            ne = self._get_field_ne_setting(field_name)
        elif ne is None:
            ne = False

        return format_nepali_datetime(datetime_value, format_string, ne=ne)


class NepaliModelAdmin(NepaliAdminMixin, admin.ModelAdmin):
    """
    Base ModelAdmin class with Nepali date utilities built-in.
    NepaliDateField and NepaliDateTimeField in list_display are automatically
    formatted (using the field's ne setting). No manual display methods needed.

    Example:
        from django_nepkit import NepaliModelAdmin, NepaliDateFilter

        @admin.register(MyModel)
        class MyModelAdmin(NepaliModelAdmin):
            list_display = ("name", "birth_date", "created_at")  # auto-formatted
            list_filter = (("birth_date", NepaliDateFilter),)
    """

    # Make NepaliDateFilter available as a class attribute
    NepaliDateFilter = NepaliDateFilter

    def _make_nepali_display(self, field_name, formatter_method):
        """Generic helper to return a callable that formats a Nepali field for list_display."""
        admin_instance = self
        try:
            field = self.model._meta.get_field(field_name)
            short_description = getattr(
                field, "verbose_name", field_name.replace("_", " ").title()
            )
        except Exception:
            short_description = field_name.replace("_", " ").title()

        def display(obj):
            val = getattr(obj, field_name, None)
            if val is None:
                return admin_instance.get_empty_value_display()
            # Call the passed formatter method (bound to self)
            return formatter_method(val, field_name=field_name)

        display.short_description = short_description
        display.admin_order_field = field_name
        return display

    def _make_nepali_date_display(self, field_name):
        return self._make_nepali_display(field_name, self.format_nepali_date)

    def _make_nepali_datetime_display(self, field_name):
        return self._make_nepali_display(field_name, self.format_nepali_datetime)

    def get_list_display(self, request):
        list_display = super().get_list_display(request)
        result = []
        for item in list_display:
            if not isinstance(item, str):
                result.append(item)
                continue
            try:
                field = self.model._meta.get_field(item)
                if isinstance(field, NepaliDateField):
                    result.append(self._make_nepali_date_display(item))
                    continue
                if isinstance(field, NepaliDateTimeField):
                    result.append(self._make_nepali_datetime_display(item))
                    continue
            except Exception:
                pass
            result.append(item)
        return result

    # Ensure admin forms render Nepali fields with the proper widget,
    # even if a project doesn't provide custom ModelForms.
    def formfield_for_dbfield(self, db_field, request, **kwargs):
        """
        Force Nepali widgets in Django admin without requiring user forms.
        """
        try:
            from django_nepkit.models import NepaliDateField, NepaliDateTimeField
            from django_nepkit.widgets import NepaliDatePickerWidget
        except Exception:
            return super().formfield_for_dbfield(db_field, request, **kwargs)

        if isinstance(db_field, (NepaliDateField, NepaliDateTimeField)):
            # Pass ne/en parameters from field to widget if they exist
            widget_kwargs = {}
            if hasattr(db_field, "ne"):
                widget_kwargs["ne"] = db_field.ne
            if hasattr(db_field, "en"):
                widget_kwargs["en"] = db_field.en
            kwargs.setdefault("widget", NepaliDatePickerWidget(**widget_kwargs))

        return super().formfield_for_dbfield(db_field, request, **kwargs)

    class Media:
        """
        Django admin ships jQuery as `django.jQuery` (not `window.jQuery`).
        The Nepali date picker library expects a global `jQuery`, so we bridge it.
        """

        css = {
            "all": (
                "https://nepalidatepicker.sajanmaharjan.com.np/v5/nepali.datepicker/css/nepali.datepicker.v5.0.6.min.css",
                "django_nepkit/css/admin-nepali-datepicker.css",
            )
        }
        js = (
            # Bridge admin's `django.jQuery` -> `window.jQuery`
            "django_nepkit/js/admin-jquery-bridge.js",
            # Date picker lib
            "https://nepalidatepicker.sajanmaharjan.com.np/v5/nepali.datepicker/js/nepali.datepicker.v5.0.6.min.js",
            # Init
            "django_nepkit/js/nepali-datepicker-init.js",
        )


# Exporting for easy usage
__all__ = [
    "NepaliDateFilter",
    "format_nepali_date",
    "format_nepali_datetime",
    "NepaliAdminMixin",
    "NepaliModelAdmin",
]
