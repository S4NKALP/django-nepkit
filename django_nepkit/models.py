from datetime import date as python_date

from django.db import models
from django.utils.translation import gettext_lazy as _
from nepali.datetime import nepalidate, nepalidatetime

from django_nepkit.utils import (
    BS_DATE_FORMAT,
    BS_DATETIME_FORMAT,
    try_parse_nepali_date,
    try_parse_nepali_datetime,
)
from django_nepkit.validators import validate_nepali_phone_number


class NepaliPhoneNumberField(models.CharField):
    description = _("Nepali Phone Number")

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("max_length", 10)
        super().__init__(*args, **kwargs)
        self.validators.append(validate_nepali_phone_number)


class NepaliDateField(models.CharField):
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
            # This is BS-native as much as possible.
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
            # If we MUST handle AD date object, we convert it to BS.
            # But we should prefer strings or nepalidate.
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
        # Fallback: convert to string
        return str(value)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        if self.auto_now:
            kwargs["auto_now"] = True
        if self.auto_now_add:
            kwargs["auto_now_add"] = True
        return name, path, args, kwargs

    def formfield(self, **kwargs):
        from .forms import NepaliDateFormField
        from .widgets import NepaliDatePickerWidget

        defaults = {
            "form_class": NepaliDateFormField,
            "widget": NepaliDatePickerWidget,
        }
        defaults.update(kwargs)
        return super().formfield(**defaults)


class NepaliTimeField(models.TimeField):
    """
    A Django Model Field for Time with Nepali localization support.
    Supports auto_now and auto_now_add like standard Django TimeField.
    """

    description = _("Nepali Time")


class NepaliDateTimeField(models.CharField):
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
            # Using nepalidatetime.now() to get current BS datetime
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
        # Fallback: convert to string
        return str(value)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        if self.auto_now:
            kwargs["auto_now"] = True
        if self.auto_now_add:
            kwargs["auto_now_add"] = True
        return name, path, args, kwargs

    def formfield(self, **kwargs):
        from .widgets import NepaliDatePickerWidget

        defaults = {
            "widget": NepaliDatePickerWidget,
        }
        defaults.update(kwargs)
        return super().formfield(**defaults)


class ProvinceField(models.CharField):
    """
    A Django Model Field for Nepali Provinces.
    """

    description = _("Nepali Province")

    def __init__(self, *args, **kwargs):
        from nepali.locations import provinces

        kwargs.setdefault("max_length", 100)
        kwargs.setdefault("choices", [(p.name, p.name) for p in provinces])
        super().__init__(*args, **kwargs)

    def formfield(self, **kwargs):
        from .widgets import ProvinceSelectWidget

        defaults = {"widget": ProvinceSelectWidget}
        defaults.update(kwargs)
        return super().formfield(**defaults)


class DistrictField(models.CharField):
    """
    A Django Model Field for Nepali Districts.
    """

    description = _("Nepali District")

    def __init__(self, *args, **kwargs):
        from nepali.locations import districts

        kwargs.setdefault("max_length", 100)
        kwargs.setdefault("choices", [(d.name, d.name) for d in districts])
        super().__init__(*args, **kwargs)

    def formfield(self, **kwargs):
        from .widgets import DistrictSelectWidget

        defaults = {"widget": DistrictSelectWidget}
        defaults.update(kwargs)
        return super().formfield(**defaults)


class MunicipalityField(models.CharField):
    """
    A Django Model Field for Nepali Municipalities.
    Includes Metropolitan, Sub-Metropolitan, Municipality, and Rural Municipality.
    """

    description = _("Nepali Municipality")

    def __init__(self, *args, **kwargs):
        from nepali.locations import municipalities

        kwargs.setdefault("max_length", 100)
        kwargs.setdefault("choices", [(m.name, m.name) for m in municipalities])
        super().__init__(*args, **kwargs)

    def formfield(self, **kwargs):
        from .widgets import MunicipalitySelectWidget

        defaults = {"widget": MunicipalitySelectWidget}
        defaults.update(kwargs)
        return super().formfield(**defaults)
