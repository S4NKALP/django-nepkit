from datetime import date as python_date

from django.db import models
from django.utils.translation import gettext_lazy as _
from nepali.datetime import nepalidate, nepalidatetime
from nepali.locations import districts, municipalities, provinces

from django_nepkit.forms import NepaliDateFormField
from django_nepkit.utils import (
    BS_DATE_FORMAT,
    BS_DATETIME_FORMAT,
    try_parse_nepali_date,
    try_parse_nepali_datetime,
)
from django_nepkit.validators import validate_nepali_phone_number
from django_nepkit.widgets import (
    DistrictSelectWidget,
    MunicipalitySelectWidget,
    NepaliDatePickerWidget,
    ProvinceSelectWidget,
)


class NepaliFieldMixin:
    """
    Mixin for Nepali model fields to handle 'ne' and 'en' arguments.
    """

    def __init__(self, *args, **kwargs):
        self.ne = kwargs.pop("ne", False)
        # Always pop en from kwargs to avoid passing it to super()
        en_value = kwargs.pop("en", True)
        # If ne=True, automatically set en=False
        if self.ne:
            self.en = False
        else:
            self.en = en_value
        super().__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        if self.ne:
            kwargs["ne"] = True
        if not self.en:
            kwargs["en"] = False
        return name, path, args, kwargs


class NepaliPhoneNumberField(models.CharField):
    description = _("Nepali Phone Number")

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("max_length", 10)
        super().__init__(*args, **kwargs)
        self.validators.append(validate_nepali_phone_number)


class NepaliDateField(NepaliFieldMixin, models.CharField):
    """
    A Django Model Field that stores Nepali (Bikram Sambat) Date.
    Internally it stores the date as BS string (YYYY-MM-DD) in the database.
    """

    description = _("Nepali Date (Bikram Sambat)")

    def __init__(self, *args, **kwargs):
        self.auto_now = kwargs.pop("auto_now", False)
        self.auto_now_add = kwargs.pop("auto_now_add", False)

        # Match Django's DateField behavior
        if self.auto_now or self.auto_now_add:
            kwargs.setdefault("editable", False)
            kwargs.setdefault("blank", True)

        kwargs.setdefault("max_length", 10)
        super().__init__(*args, **kwargs)

    def pre_save(self, model_instance, add):
        if self.auto_now or (self.auto_now_add and add):
            # Using nepalidate.today() to get current BS date.
            value = nepalidate.today().strftime(BS_DATE_FORMAT)
            setattr(model_instance, self.attname, value)
            return value
        return super().pre_save(model_instance, add)

    def from_db_value(self, value, expression, connection):
        parsed = try_parse_nepali_date(value)
        return parsed if parsed is not None else value

    def to_python(self, value):
        if value is None or isinstance(value, nepalidate):
            return value
        if isinstance(value, python_date):
            try:
                return nepalidate.from_date(value)
            except (ValueError, TypeError):
                return str(value)
        if isinstance(value, str):
            parsed = try_parse_nepali_date(value)
            return parsed if parsed is not None else value
        return super().to_python(value)

    def validate(self, value, model_instance):
        if isinstance(value, nepalidate):
            value = value.strftime(BS_DATE_FORMAT)
        super().validate(value, model_instance)

    def run_validators(self, value):
        if isinstance(value, nepalidate):
            value = value.strftime(BS_DATE_FORMAT)
        super().run_validators(value)

    def get_prep_value(self, value):
        if value is None:
            return value
        if isinstance(value, nepalidate):
            return value.strftime(BS_DATE_FORMAT)
        if isinstance(value, python_date):
            try:
                return nepalidate.from_date(value).strftime(BS_DATE_FORMAT)
            except (ValueError, TypeError):
                return str(value)
        if isinstance(value, str):
            return value
        return str(value)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        if self.auto_now:
            kwargs["auto_now"] = True
        if self.auto_now_add:
            kwargs["auto_now_add"] = True
        return name, path, args, kwargs

    def formfield(self, **kwargs):
        defaults = {
            "form_class": NepaliDateFormField,
            "widget": NepaliDatePickerWidget(ne=self.ne, en=self.en),
        }
        defaults.update(kwargs)
        return super().formfield(**defaults)


class NepaliTimeField(NepaliFieldMixin, models.TimeField):
    """
    A Django Model Field for Time with Nepali localization support.
    """

    description = _("Nepali Time")


class NepaliDateTimeField(NepaliFieldMixin, models.CharField):
    """
    A Django Model Field that stores Nepali (Bikram Sambat) DateTime.
    Internally it stores the datetime as BS string (YYYY-MM-DD HH:MM:SS) in the database.
    """

    description = _("Nepali DateTime (Bikram Sambat)")

    def __init__(self, *args, **kwargs):
        self.auto_now = kwargs.pop("auto_now", False)
        self.auto_now_add = kwargs.pop("auto_now_add", False)

        # Match Django's DateTimeField behavior
        if self.auto_now or self.auto_now_add:
            kwargs.setdefault("editable", False)
            kwargs.setdefault("blank", True)

        kwargs.setdefault("max_length", 19)  # YYYY-MM-DD HH:MM:SS
        super().__init__(*args, **kwargs)

    def pre_save(self, model_instance, add):
        if self.auto_now or (self.auto_now_add and add):
            value = nepalidatetime.now().strftime(BS_DATETIME_FORMAT)
            setattr(model_instance, self.attname, value)
            return value
        return super().pre_save(model_instance, add)

    def from_db_value(self, value, expression, connection):
        parsed = try_parse_nepali_datetime(value)
        return parsed if parsed is not None else value

    def to_python(self, value):
        if value is None or isinstance(value, nepalidatetime):
            return value
        if isinstance(value, str):
            parsed = try_parse_nepali_datetime(value)
            return parsed if parsed is not None else value
        return super().to_python(value)

    def validate(self, value, model_instance):
        if isinstance(value, nepalidatetime):
            value = value.strftime(BS_DATETIME_FORMAT)
        super().validate(value, model_instance)

    def run_validators(self, value):
        if isinstance(value, nepalidatetime):
            value = value.strftime(BS_DATETIME_FORMAT)
        super().run_validators(value)

    def get_prep_value(self, value):
        if value is None:
            return value
        if isinstance(value, nepalidatetime):
            return value.strftime(BS_DATETIME_FORMAT)
        if isinstance(value, str):
            return value
        return str(value)

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


class ProvinceField(NepaliFieldMixin, models.CharField):
    description = _("Nepali Province")

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("max_length", 100)

        # We need self.ne set by Mixin, but Mixin init runs last in normal MRO if we just use super().__init__.
        # So we manually handle pop before calling super, OR we rely on kwargs.

        # Actually, if we use NepaliFieldMixin as first parent, its __init__ will run.
        # But we need to define choices based on ne.
        # So we should pop 'ne' here, set it, then pass to super?
        # But Mixin expects to pop it.

        # Better approach: Extract ne here without popping (peek), or pop and pass back?
        # Let's just duplicate popping here to set choices, then re-inject for Mixin?
        # Or just handle it manually here and pass remaining to super.

        # Let's modify behavior: pop ne here, calculate choices, then put it back?
        # Or just manually set self.ne/self.en here and don't rely on Mixin's init for choices, but rely on it for other things?

        # To avoid complexity, I'll peek at kwargs['ne'] if it exists.
        ne = kwargs.get("ne", False)

        if ne:
            choices = [
                (getattr(p, "name_nepali", p.name), getattr(p, "name_nepali", p.name))
                for p in provinces
            ]
        else:
            choices = [(p.name, p.name) for p in provinces]

        kwargs.setdefault("choices", choices)
        super().__init__(*args, **kwargs)

    def formfield(self, **kwargs):
        defaults = {"widget": ProvinceSelectWidget(ne=self.ne, en=self.en)}
        defaults.update(kwargs)
        # Bypassing the immediate parent's formfield if it's just CharField's
        return super(models.CharField, self).formfield(**defaults)
        # Wait, super().formfield() calls Django's CharField.formfield.
        # We want that.


class DistrictField(NepaliFieldMixin, models.CharField):
    description = _("Nepali District")

    def __init__(self, *args, **kwargs):
        ne = kwargs.get("ne", False)
        kwargs.setdefault("max_length", 100)

        if ne:
            choices = [
                (getattr(d, "name_nepali", d.name), getattr(d, "name_nepali", d.name))
                for d in districts
            ]
        else:
            choices = [(d.name, d.name) for d in districts]

        kwargs.setdefault("choices", choices)
        super().__init__(*args, **kwargs)

    def formfield(self, **kwargs):
        defaults = {"widget": DistrictSelectWidget(ne=self.ne, en=self.en)}
        defaults.update(kwargs)
        return super(models.CharField, self).formfield(**defaults)


class MunicipalityField(NepaliFieldMixin, models.CharField):
    description = _("Nepali Municipality")

    def __init__(self, *args, **kwargs):
        ne = kwargs.get("ne", False)
        kwargs.setdefault("max_length", 100)

        if ne:
            choices = [
                (getattr(m, "name_nepali", m.name), getattr(m, "name_nepali", m.name))
                for m in municipalities
            ]
        else:
            choices = [(m.name, m.name) for m in municipalities]

        kwargs.setdefault("choices", choices)
        super().__init__(*args, **kwargs)

    def formfield(self, **kwargs):
        defaults = {"widget": MunicipalitySelectWidget(ne=self.ne, en=self.en)}
        defaults.update(kwargs)
        return super(models.CharField, self).formfield(**defaults)
