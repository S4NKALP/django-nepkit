import logging

from django.contrib import admin
from django.core.exceptions import FieldDoesNotExist
from django.utils.translation import gettext_lazy as _
from nepali.datetime import nepalidate, nepalidatetime
from nepali.number import english_to_nepali

from django_nepkit.conf import nepkit_settings
from django_nepkit.models import (
    NepaliCurrencyField,
    NepaliDateField,
    NepaliDateTimeField,
    NepaliTimeField,
)
from django_nepkit.utils import (
    format_nepali_currency,
    format_nepali_time,
    try_parse_nepali_date,
    try_parse_nepali_datetime,
)

logger = logging.getLogger(__name__)


def _format_nepali_common(value, try_parse_func, format_string, ne, cls_type):
    """Format a Nepali date/time for admin display, falling back gracefully."""
    if value is None:
        return ""

    try:
        if isinstance(value, str):
            parsed = try_parse_func(value)
            if parsed is not None:
                if ne and hasattr(parsed, "strftime_ne"):
                    return parsed.strftime_ne(format_string)
                return parsed.strftime(format_string)
        if isinstance(value, cls_type):
            if ne and hasattr(value, "strftime_ne"):
                return value.strftime_ne(format_string)
            return value.strftime(format_string)
    except (ValueError, TypeError, AttributeError) as exc:
        logger.warning("nepkit admin formatter: cannot format %r: %s", value, exc)
    return ""


def format_nepali_date(date_value, format_string="%B %d, %Y", ne=False):
    """Format a nepalidate object with Nepali month names."""
    return _format_nepali_common(
        date_value, try_parse_nepali_date, format_string, ne, nepalidate
    )


def format_nepali_datetime(datetime_value, format_string=None, ne=False):
    """Format a nepalidatetime object with Nepali month names."""
    if format_string is None:
        if nepkit_settings.TIME_FORMAT == 24:
            format_string = "%B %d, %Y %H:%M"
        else:
            format_string = "%B %d, %Y %I:%M %p"
    return _format_nepali_common(
        datetime_value, try_parse_nepali_datetime, format_string, ne, nepalidatetime
    )


def format_nepali_time_admin(time_value, format_string=None, ne=False):
    """Format a ``time``/``datetime`` for the admin with Devanagari support."""
    if format_string is None:
        format_string = nepkit_settings.BS_TIME_FORMAT
    formatted = format_nepali_time(time_value, format_string)
    if ne and formatted:
        formatted = english_to_nepali(formatted)
    return formatted


# ---------------------------------------------------------------------------
# Admin list filters
# ---------------------------------------------------------------------------


def _separator_from_format(fmt):
    """Pick the first non-% character from a strftime format string.

    Returns the separator for ``%Y/%m/%d``-style formats, falling back to
    ``"-"`` when the format has no separator (e.g. ``%Y%m%d``).
    """
    if not fmt or len(fmt) < 3:
        return "-"
    return fmt[2] if not fmt[2].startswith("%") else "-"


class BaseNepaliDateFilter(admin.FieldListFilter):
    """Base class for date filters (Year/Month)."""

    def __init__(self, field, request, params, model, model_admin, field_path):
        self.parameter_name = f"{field_path}_{self.suffix}"
        super().__init__(field, request, params, model, model_admin, field_path)

    def expected_parameters(self):
        return [self.parameter_name]

    def choices(self, changelist):
        yield {
            "selected": self.used_parameters.get(self.parameter_name) is None,
            "query_string": changelist.get_query_string(remove=[self.parameter_name]),
            "display": _("All"),
        }
        for value, display in self.get_filter_options():
            yield {
                "selected": self.used_parameters.get(self.parameter_name) == str(value),
                "query_string": changelist.get_query_string(
                    {self.parameter_name: str(value)}
                ),
                "display": display,
            }

    def queryset(self, request, queryset):
        value = self.used_parameters.get(self.parameter_name)
        if value:
            return self.apply_filter(queryset, value)
        return queryset

    def get_filter_options(self):
        raise NotImplementedError

    def apply_filter(self, queryset, value):
        raise NotImplementedError


class NepaliDateFilter(BaseNepaliDateFilter):
    """Filter by Nepali Year (e.g. 2080)."""

    suffix = "bs_year"
    title = _("Nepali Date (Year)")

    def get_filter_options(self):
        current_year = nepalidate.today().year
        return [(y, str(y)) for y in range(current_year - 10, current_year + 2)]

    def apply_filter(self, queryset, value):
        fmt = nepkit_settings.BS_DATE_FORMAT
        if fmt.startswith("%Y"):
            separator = _separator_from_format(fmt)
            return queryset.filter(
                **{f"{self.field_path}__startswith": f"{value}{separator}"}
            )
        return queryset.filter(**{f"{self.field_path}__icontains": f"{value}"})


class NepaliMonthFilter(BaseNepaliDateFilter):
    """Filter by Nepali Month (e.g. Baisakh)."""

    suffix = "bs_month"
    title = _("Nepali Date (Month)")

    def get_filter_options(self):
        ne = nepkit_settings.DEFAULT_LANGUAGE == "ne"
        names = [
            ("बैशाख", "Baisakh"),
            ("जेठ", "Jestha"),
            ("असार", "Ashad"),
            ("साउन", "Shrawan"),
            ("भदौ", "Bhadra"),
            ("असोज", "Ashwin"),
            ("कात्तिक", "Kartik"),
            ("मंसिर", "Mangsir"),
            ("पुष", "Poush"),
            ("माघ", "Magh"),
            ("फागुन", "Falgun"),
            ("चैत", "Chaitra"),
        ]
        return [(f"{i:02d}", n[0] if ne else n[1]) for i, n in enumerate(names, 1)]

    def apply_filter(self, queryset, value):
        fmt = nepkit_settings.BS_DATE_FORMAT
        if fmt == "%Y-%m-%d":
            return queryset.filter(**{f"{self.field_path}__contains": f"-{value}-"})
        separator = _separator_from_format(fmt)
        return queryset.filter(
            **{f"{self.field_path}__contains": f"{separator}{value}{separator}"}
        )


# Register the year filter as the default for NepaliDateField.
admin.FieldListFilter.register(
    lambda f: isinstance(f, NepaliDateField),
    NepaliDateFilter,
    take_priority=True,
)


# ---------------------------------------------------------------------------
# ModelAdmin mixin
# ---------------------------------------------------------------------------


class NepaliAdminMixin:
    """Provides date formatting helpers for Admin classes."""

    def _get_field_ne_setting(self, field_name):
        """Return the field's ``ne`` flag, or ``None`` if the field has none.

        ``None`` distinguishes "field has no opinion" from an explicit
        ``ne=False`` (English), which the caller can use to fall back to
        the project default without overwriting a field-level override.
        """
        if not hasattr(self, "model"):
            return None
        try:
            field = self.model._meta.get_field(field_name)
            if hasattr(field, "ne"):
                return field.ne
        except (FieldDoesNotExist, AttributeError):
            return None
        return None

    def format_nepali_date(
        self, date_value, format_string="%B %d, %Y", ne=None, field_name=None
    ):
        if ne is None and field_name:
            ne = self._get_field_ne_setting(field_name)
        if ne is None:
            ne = nepkit_settings.DEFAULT_LANGUAGE == "ne"
        return format_nepali_date(date_value, format_string, ne=ne)

    def format_nepali_datetime(
        self,
        datetime_value,
        format_string=None,
        ne=None,
        field_name=None,
    ):
        if ne is None and field_name:
            ne = self._get_field_ne_setting(field_name)
        if ne is None:
            ne = nepkit_settings.DEFAULT_LANGUAGE == "ne"
        return format_nepali_datetime(datetime_value, format_string, ne=ne)

    def format_nepali_currency(self, value, currency_symbol="Rs.", ne=False, **kwargs):
        return format_nepali_currency(value, currency_symbol=currency_symbol, ne=ne)


class NepaliModelAdmin(NepaliAdminMixin, admin.ModelAdmin):
    """
    Standard Admin class that automatically formats Nepali dates in lists.

    Example::

        @admin.register(MyModel)
        class MyModelAdmin(NepaliModelAdmin):
            list_display = ("name", "birth_date", "created_at")
            list_filter = (("birth_date", NepaliDateFilter),)
    """

    NepaliDateFilter = NepaliDateFilter
    NepaliMonthFilter = NepaliMonthFilter

    def _make_nepali_display(self, field_name, formatter_method):
        admin_instance = self
        try:
            field = self.model._meta.get_field(field_name)
            short_description = getattr(
                field, "verbose_name", field_name.replace("_", " ").title()
            )
        except (FieldDoesNotExist, AttributeError):
            short_description = field_name.replace("_", " ").title()

        def display(obj):
            val = getattr(obj, field_name, None)
            if val is None:
                return admin_instance.get_empty_value_display()
            return formatter_method(val, field_name=field_name)

        display.short_description = short_description
        display.admin_order_field = field_name
        return display

    def _make_nepali_date_display(self, field_name):
        return self._make_nepali_display(field_name, self.format_nepali_date)

    def _make_nepali_datetime_display(self, field_name):
        return self._make_nepali_display(field_name, self.format_nepali_datetime)

    def _make_nepali_currency_display(self, field_name):
        return self._make_nepali_display(field_name, self.format_nepali_currency)

    def get_list_display(self, request):
        list_display = super().get_list_display(request)
        result = []
        for item in list_display:
            if not isinstance(item, str):
                result.append(item)
                continue
            try:
                field = self.model._meta.get_field(item)
            except (FieldDoesNotExist, AttributeError):
                result.append(item)
                continue
            if isinstance(field, NepaliDateField):
                result.append(self._make_nepali_date_display(item))
            elif isinstance(field, NepaliDateTimeField):
                result.append(self._make_nepali_datetime_display(item))
            elif isinstance(field, NepaliTimeField):
                result.append(self._make_nepali_time_display(item))
            elif isinstance(field, NepaliCurrencyField):
                result.append(self._make_nepali_currency_display(item))
            else:
                result.append(item)
        return result

    def _make_nepali_time_display(self, field_name):
        def display(obj):
            val = getattr(obj, field_name, None)
            if val is None:
                return self.get_empty_value_display()
            ne = self._get_field_ne_setting(field_name)
            if ne is None:
                # Field has no ``ne`` attribute (e.g. plain ``TimeField``)
                # — fall back to the project default.
                ne = nepkit_settings.DEFAULT_LANGUAGE == "ne"
            return format_nepali_time_admin(val, ne=ne)

        try:
            field = self.model._meta.get_field(field_name)
            display.short_description = getattr(
                field, "verbose_name", field_name.replace("_", " ").title()
            )
        except (FieldDoesNotExist, AttributeError):
            display.short_description = field_name.replace("_", " ").title()
        display.admin_order_field = field_name
        return display

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        """Auto-wire NepaliDatePicker / NepaliTimeWidget in the admin form."""
        from django_nepkit.widgets import NepaliDatePickerWidget, NepaliTimeWidget

        if (
            isinstance(db_field, (NepaliDateField, NepaliDateTimeField))
            and nepkit_settings.ADMIN_DATEPICKER
        ):
            widget_kwargs = {}
            if hasattr(db_field, "ne"):
                widget_kwargs["ne"] = db_field.ne
            if hasattr(db_field, "en"):
                widget_kwargs["en"] = db_field.en
            kwargs.setdefault("widget", NepaliDatePickerWidget(**widget_kwargs))

        if isinstance(db_field, NepaliTimeField):
            widget_kwargs = {}
            if hasattr(db_field, "ne"):
                widget_kwargs["ne"] = db_field.ne
            if hasattr(db_field, "en"):
                widget_kwargs["en"] = db_field.en
            if hasattr(db_field, "htmx"):
                widget_kwargs["htmx"] = db_field.htmx
            kwargs.setdefault("widget", NepaliTimeWidget(**widget_kwargs))

        return super().formfield_for_dbfield(db_field, request, **kwargs)

    class Media:
        """Loads the Nepali Datepicker and bridging scripts."""

        css = {
            "all": (
                "https://nepalidatepicker.sajanmaharjan.com.np/v5/nepali.datepicker/css/nepali.datepicker.v5.0.6.min.css",
                "django_nepkit/css/admin-nepali-datepicker.css",
            )
        }
        js = (
            "django_nepkit/js/admin-jquery-bridge.js",
            "https://nepalidatepicker.sajanmaharjan.com.np/v5/nepali.datepicker/js/nepali.datepicker.v5.0.6.min.js",
            "django_nepkit/js/nepali-datepicker-init.js",
            "django_nepkit/js/nepal-data.js",
            "django_nepkit/js/address-chaining.js",
        )


__all__ = [
    "NepaliDateFilter",
    "NepaliMonthFilter",
    "format_nepali_date",
    "format_nepali_datetime",
    "NepaliAdminMixin",
    "NepaliModelAdmin",
]
