from datetime import date as python_date
from datetime import datetime as python_datetime
from datetime import time as python_time

from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from nepali.datetime import nepalidate, nepalidatetime
from nepali.locations import districts, municipalities, provinces

from django_nepkit.utils import (
    try_parse_nepali_date,
    try_parse_nepali_datetime,
    try_parse_nepali_time,
)
from django_nepkit.validators import validate_nepali_phone_number
from django_nepkit.widgets import (
    DistrictSelectWidget,
    MunicipalitySelectWidget,
    NepaliDatePickerWidget,
    NepaliTimeWidget,
    ProvinceSelectWidget,
)
from django_nepkit.conf import nepkit_settings


class NepaliFieldMixin:
    """Adds Nepali 'ne' and 'en' support to any field."""

    def __init__(self, *args, **kwargs):
        default_lang = nepkit_settings.DEFAULT_LANGUAGE
        self.ne = kwargs.pop("ne", default_lang == "ne")

        explicit_en = "en" in kwargs
        en_value = kwargs.pop("en", not self.ne)

        if self.ne and not explicit_en:
            self.en = False
        else:
            self.en = en_value

        self.htmx = kwargs.pop("htmx", False)

        super().__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        if self.ne:
            kwargs["ne"] = True
        if not self.en:
            kwargs["en"] = False
        if self.htmx:
            kwargs["htmx"] = True
        return name, path, args, kwargs


class NepaliPhoneNumberField(models.CharField):
    description = _("Nepali Phone Number")

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("max_length", 10)
        super().__init__(*args, **kwargs)
        self.validators.append(validate_nepali_phone_number)


class BaseNepaliBSField(NepaliFieldMixin, models.CharField):
    """Base class for Nepali date and datetime fields."""

    # Subclasses set these.
    nepali_cls = None  # nepalidate or nepalidatetime

    def __init__(self, *args, **kwargs):
        self.auto_now = kwargs.pop("auto_now", False)
        self.auto_now_add = kwargs.pop("auto_now_add", False)

        if self.auto_now or self.auto_now_add:
            kwargs.setdefault("editable", False)
            kwargs.setdefault("blank", True)

        kwargs.setdefault("max_length", getattr(self, "default_max_length", 20))
        super().__init__(*args, **kwargs)

    @property
    def format_str(self) -> str:
        """Resolved at call time so ``override_settings`` propagates."""
        if self.nepali_cls is nepalidate:
            return nepkit_settings.BS_DATE_FORMAT
        if self.nepali_cls is nepalidatetime:
            return nepkit_settings.BS_DATETIME_FORMAT
        return nepkit_settings.BS_DATE_FORMAT

    def _convert_from_python(self, value):
        """Convert a Python ``date``/``datetime`` to a Nepali object.

        Raises ``ValidationError`` on failure (out-of-range, etc.) so
        invalid data cannot reach the database.
        """
        if isinstance(value, python_datetime) and timezone.is_aware(value):
            value = timezone.localtime(value)
        try:
            if self.nepali_cls is nepalidate:
                return nepalidate.from_date(value)
            if self.nepali_cls is nepalidatetime:
                return nepalidatetime.from_datetime(value)
        except (ValueError, TypeError, OverflowError) as exc:
            raise ValidationError(
                _("Cannot convert %(value)r to a Nepali date/time: %(err)s"),
                params={"value": value, "err": exc},
            ) from exc
        raise ValidationError(
            _("Unsupported source type for Nepali date field: %(value)r"),
            params={"value": value},
        )

    def pre_save(self, model_instance, add):
        if self.auto_now or (self.auto_now_add and add):
            now = timezone.now()
            if timezone.is_aware(now):
                now = timezone.localtime(now)
            if self.nepali_cls is nepalidate:
                value = nepalidate.from_date(now.date())
            else:
                value = nepalidatetime.from_datetime(now)
            formatted = value.strftime(self.format_str)
            setattr(model_instance, self.attname, formatted)
            return formatted
        return super().pre_save(model_instance, add)

    def from_db_value(self, value, expression, connection):
        if value is None:
            return None
        parsed = self._parse_str(value)
        if parsed is None:
            # Lenient on read: log the inconsistency but don't crash the
            # queryset.  An admin can see and fix bad rows.
            import logging

            logging.getLogger(__name__).warning(
                "Nepali field %s.%s stored value %r could not be parsed",
                self.model.__name__ if hasattr(self, "model") else "?",
                self.attname,
                value,
            )
            return value
        return parsed

    def _parse_str(self, value):
        """Parse a stored string into a Nepali object (or ``None``)."""
        if isinstance(value, str):
            return self.parse_func(value)
        return None

    def to_python(self, value):
        if value is None or isinstance(value, self.nepali_cls):
            return value
        if isinstance(value, (python_date, python_datetime)):
            return self._convert_from_python(value)
        if isinstance(value, str):
            parsed = self._parse_str(value)
            if parsed is not None:
                return parsed
            raise ValidationError(
                _("Invalid Nepali date/time string: %(value)r"),
                params={"value": value},
            )
        return super().to_python(value)

    def _get_string_value(self, value):
        if isinstance(value, (nepalidate, nepalidatetime)):
            return value.strftime(self.format_str)
        return value

    def validate(self, value, model_instance):
        super().validate(self._get_string_value(value), model_instance)

    def run_validators(self, value):
        super().run_validators(self._get_string_value(value))

    def get_prep_value(self, value):
        if value is None:
            return value
        if isinstance(value, self.nepali_cls):
            return value.strftime(self.format_str)
        if isinstance(value, (python_date, python_datetime)):
            converted = self._convert_from_python(value)
            return converted.strftime(self.format_str)
        if isinstance(value, str):
            parsed = self._parse_str(value)
            if parsed is not None:
                return parsed.strftime(self.format_str)
            raise ValidationError(
                _("Invalid Nepali date/time string: %(value)r"),
                params={"value": value},
            )
        raise ValidationError(
            _("Unsupported value for Nepali date/time field: %(value)r"),
            params={"value": value},
        )

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        if self.auto_now:
            kwargs["auto_now"] = True
        if self.auto_now_add:
            kwargs["auto_now_add"] = True
        return name, path, args, kwargs

    def formfield(self, **kwargs):
        defaults = {
            "widget": NepaliDatePickerWidget(ne=self.ne, en=self.en),
        }
        defaults.update(kwargs)
        return super().formfield(**defaults)


class NepaliDateField(BaseNepaliBSField):
    description = _("Nepali Date (Bikram Sambat)")
    default_max_length = 10
    nepali_cls = nepalidate
    parse_func = staticmethod(try_parse_nepali_date)

    def formfield(self, **kwargs):
        from django_nepkit.forms import NepaliDateFormField

        kwargs.setdefault("form_class", NepaliDateFormField)
        return super().formfield(**kwargs)


class NepaliTimeField(NepaliFieldMixin, models.TimeField):
    """A ``TimeField`` that supports Devanagari digit display.

    Stores a real ``datetime.time`` value in the database (so existing
    queries / indexes behave like a normal ``TimeField``) but renders the
    value through ``BS_TIME_FORMAT`` and optionally converts the digits to
    Devanagari when ``ne=True``.
    """

    description = _("Nepali Time")

    @property
    def format_str(self) -> str:
        return nepkit_settings.BS_TIME_FORMAT

    def pre_save(self, model_instance, add):
        if self.auto_now or (self.auto_now_add and add):
            now = timezone.now()
            if timezone.is_aware(now):
                now = timezone.localtime(now)
            value = now.time()
            setattr(model_instance, self.attname, value)
            return value
        return super().pre_save(model_instance, add)

    def from_db_value(self, value, expression, connection):
        if value is None:
            return None
        if isinstance(value, python_time):
            return value
        if isinstance(value, str):
            parsed = try_parse_nepali_time(value)
            if parsed is not None:
                return parsed
            import logging

            logging.getLogger(__name__).warning(
                "NepaliTimeField stored value %r is not a valid time; returning as-is",
                value,
            )
        return value

    def to_python(self, value):
        if value is None or isinstance(value, python_time):
            return value
        if isinstance(value, python_datetime):
            return value.time()
        if isinstance(value, str):
            parsed = try_parse_nepali_time(value)
            if parsed is not None:
                return parsed
            raise ValidationError(
                _("Invalid Nepali time string: %(value)r"),
                params={"value": value},
            )
        return super().to_python(value)

    def get_prep_value(self, value):
        if value is None:
            return value
        if isinstance(value, python_datetime):
            value = value.time()
        return super().get_prep_value(value)

    def value_to_string(self, obj):
        from django_nepkit.utils import format_nepali_time

        value = self.value_from_object(obj)
        return "" if value is None else format_nepali_time(value, self.format_str)

    def format_value_for_display(self, value) -> str:
        """Render a ``time`` for templates / admin using the Nepali format."""
        from django_nepkit.utils import format_nepali_time

        return format_nepali_time(value, self.format_str)

    def formfield(self, **kwargs):
        defaults = {
            "widget": NepaliTimeWidget(ne=self.ne, en=self.en, htmx=self.htmx),
        }
        defaults.update(kwargs)
        return super().formfield(**defaults)


class NepaliDateTimeField(BaseNepaliBSField):
    description = _("Nepali DateTime (Bikram Sambat)")
    default_max_length = 19
    nepali_cls = nepalidatetime
    parse_func = staticmethod(try_parse_nepali_datetime)


class BaseLocationField(NepaliFieldMixin, models.CharField):
    """Base class for Province, District, and Municipality fields.

    ``choices`` is a *property* that re-reads ``nepkit_settings`` on every
    access, so flipping ``NEPKIT['DEFAULT_LANGUAGE']`` (e.g. via
    ``override_settings``) is reflected in the admin / forms without
    having to reconstruct the field.  An explicit ``ne=True`` /
    ``ne=False`` passed to the constructor pins the language for the
    field's lifetime — only the implicit default re-reads the setting.
    """

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("max_length", 100)
        self._explicit_ne = "ne" in kwargs
        # ``Field.__init__`` sets ``self.choices = choices or []``; the
        # property setter is a no-op, so any caller-provided choices are
        # ignored (matching the previous behaviour).
        kwargs.setdefault("choices", [])
        super().__init__(*args, **kwargs)

    @property
    def _resolved_ne(self) -> bool:
        if self._explicit_ne:
            return self.ne
        return nepkit_settings.DEFAULT_LANGUAGE == "ne"

    @property
    def choices(self):
        # Invalidate Django's flatchoices cache so the next consumer
        # (validate, formfield, etc.) sees the live list.
        self._flatchoices = None
        return self.get_choices_from_source(self._resolved_ne)

    @choices.setter
    def choices(self, value):
        # ``Field.__init__`` and the deprecated ``refresh_choices`` set
        # this attribute.  We accept the write but discard it — the
        # property always returns the live value.
        pass

    def refresh_choices(self, ne=None):  # noqa: ARG002 — kept for backwards compat
        """Deprecated: ``choices`` is now a live property.

        Kept as a no-op so existing ``setting_changed`` handlers /
        test fixtures keep working.
        """
        self._flatchoices = None
        return self.choices

    def get_choices_from_source(self, ne):
        source = getattr(self, "source", [])
        return [(self._get_name(item, ne), self._get_name(item, ne)) for item in source]

    def _get_name(self, item, ne):
        return getattr(item, "name_nepali", item.name) if ne else item.name

    def formfield(self, **kwargs):
        widget_cls = getattr(self, "widget_class", None)
        if widget_cls:
            defaults = {"widget": widget_cls(ne=self.ne, en=self.en, htmx=self.htmx)}
            defaults.update(kwargs)
            return super(models.CharField, self).formfield(**defaults)
        return super().formfield(**kwargs)


class ProvinceField(BaseLocationField):
    description = _("Nepali Province")
    source = provinces
    widget_class = ProvinceSelectWidget


class DistrictField(BaseLocationField):
    description = _("Nepali District")
    source = districts
    widget_class = DistrictSelectWidget


class MunicipalityField(BaseLocationField):
    description = _("Nepali Municipality")
    source = municipalities
    widget_class = MunicipalitySelectWidget


class NepaliCurrencyField(models.DecimalField):
    description = _("Nepali Currency")

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("max_digits", 19)
        kwargs.setdefault("decimal_places", 2)
        super().__init__(*args, **kwargs)
