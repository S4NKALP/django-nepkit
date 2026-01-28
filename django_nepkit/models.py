from datetime import date as python_date

from django.db import models
from django.utils.translation import gettext_lazy as _
from nepali.datetime import nepalidate, nepalidatetime
from nepali.locations import districts, municipalities, provinces

from django_nepkit.forms import NepaliDateFormField
from django_nepkit.validators import validate_nepali_phone_number
from django_nepkit.widgets import (
    DistrictSelectWidget,
    MunicipalitySelectWidget,
    NepaliDatePickerWidget,
    ProvinceSelectWidget,
)

# --------------------------------------------------
# Phone Number
# --------------------------------------------------


class NepaliPhoneNumberField(models.CharField):
    description = _("Nepali phone number")

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("max_length", 10)
        super().__init__(*args, **kwargs)
        self.validators.append(validate_nepali_phone_number)


# --------------------------------------------------
# Location Fields
# --------------------------------------------------


class ProvinceField(models.CharField):
    description = _("Nepal Province")

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("max_length", 100)
        kwargs.setdefault(
            "choices",
            [(p.name, p.name) for p in provinces],
        )
        super().__init__(*args, **kwargs)

    def formfield(self, **kwargs):
        kwargs.setdefault("widget", ProvinceSelectWidget)
        return super().formfield(**kwargs)


class DistrictField(models.CharField):
    description = _("Nepal District")

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("max_length", 100)
        kwargs.setdefault(
            "choices",
            [(d.name, d.name) for d in districts],
        )
        super().__init__(*args, **kwargs)

    def formfield(self, **kwargs):
        kwargs.setdefault("widget", DistrictSelectWidget)
        return super().formfield(**kwargs)


class MunicipalityField(models.CharField):
    description = _("Nepal Municipality")

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("max_length", 100)
        kwargs.setdefault(
            "choices",
            [(m.name, m.name) for m in municipalities],
        )
        super().__init__(*args, **kwargs)

    def formfield(self, **kwargs):
        kwargs.setdefault("widget", MunicipalitySelectWidget)
        return super().formfield(**kwargs)


# --------------------------------------------------
# Time Field
# --------------------------------------------------
class NepaliTimeField(models.TimeField):
    """
    Time field for Nepal (standard time).
    This is essentially Django's TimeField,
    kept for semantic clarity and future extensions.
    """

    description = _("Nepali Time")

    def formfield(self, **kwargs):
        return super().formfield(**kwargs)


# --------------------------------------------------
# Base Nepali BS Date / DateTime Field
# --------------------------------------------------


class BaseNepaliDateCharField(models.CharField):
    """
    Base class for Nepali (Bikram Sambat) Date / DateTime fields.
    Stored as string in DB, returned as nepali date objects in Python.
    """

    format = None
    nepali_type = None

    def __init__(self, *args, auto_now=False, auto_now_add=False, **kwargs):
        self.auto_now = auto_now
        self.auto_now_add = auto_now_add

        if auto_now or auto_now_add:
            kwargs.setdefault("editable", False)
            kwargs.setdefault("blank", True)

        super().__init__(*args, **kwargs)

    def _now(self):
        raise NotImplementedError

    def pre_save(self, model_instance, add):
        if self.auto_now or (self.auto_now_add and add):
            value = self._now().strftime(self.format)
            setattr(model_instance, self.attname, value)
            return value
        return super().pre_save(model_instance, add)

    def to_python(self, value):
        if value is None or isinstance(value, self.nepali_type):
            return value

        if isinstance(value, python_date):
            return self.nepali_type.from_date(value)

        if isinstance(value, str):
            return self.nepali_type.strptime(value.strip(), self.format)

        return value

    def from_db_value(self, value, expression, connection):
        if value is None:
            return value
        return self.nepali_type.strptime(value, self.format)

    def get_prep_value(self, value):
        if value is None:
            return None

        if isinstance(value, self.nepali_type):
            return value.strftime(self.format)

        return str(value)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        if self.auto_now:
            kwargs["auto_now"] = True
        if self.auto_now_add:
            kwargs["auto_now_add"] = True
        return name, path, args, kwargs


# --------------------------------------------------
# Nepali Date Field (BS)
# --------------------------------------------------


class NepaliDateField(BaseNepaliDateCharField):
    description = _("Nepali Date (Bikram Sambat)")
    format = "%Y-%m-%d"
    nepali_type = nepalidate

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("max_length", 10)
        super().__init__(*args, **kwargs)

    def _now(self):
        return nepalidate.today()

    def formfield(self, **kwargs):
        kwargs.setdefault("form_class", NepaliDateFormField)
        kwargs.setdefault("widget", NepaliDatePickerWidget)
        return super().formfield(**kwargs)


# --------------------------------------------------
# Nepali DateTime Field (BS)
# --------------------------------------------------


class NepaliDateTimeField(BaseNepaliDateCharField):
    description = _("Nepali DateTime (Bikram Sambat)")
    format = "%Y-%m-%d %H:%M:%S"
    nepali_type = nepalidatetime

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("max_length", 19)
        super().__init__(*args, **kwargs)

    def _now(self):
        return nepalidatetime.now()

    def formfield(self, **kwargs):
        kwargs.setdefault("widget", NepaliDatePickerWidget)
        return super().formfield(**kwargs)
