from datetime import date as python_date

from django.db import models
from django.utils.translation import gettext_lazy as _
from nepali.datetime import nepalidate
from nepali.locations import districts, municipalities, provices

from django_nepkit.forms import NepaliDateFormField
from django_nepkit.validators import validate_nepali_phone_number
from django_nepkit.widgets import (
    DistrictSelectWidget,
    MunicipalitySelectWidget,
    NepaliDatePickerWidget,
    ProvinceSelectWidget,
)


class NepaliPhoneNumberField(models.CharField):
    description = _("Nepali phone number")

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("max_length", 10)
        super().__init__(*args, **kwargs)
        self.validators.append(validate_nepali_phone_number)


class ProvinceField(models.CharField):
    description = _("Nepal's Province")

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("max_length", 100)
        kwargs.setdefault("choices", [(p.name, p.name) for p in provices])
        super().__init__(*args, **kwargs)

    def formfield(self, **kwargs):
        defaults = {"widget": ProvinceSelectWidget}
        defaults.update(kwargs)
        return super().formfield(**defaults)


class DistrictField(models.CharField):
    description = _("Nepal's District")

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("max_length", 100)
        kwargs.setdefault("choices", [(d.name, d.name) for d in districts])
        super().__init__(*args, **kwargs)

    def formfield(self, **kwargs):
        defaults = {"widget": DistrictSelectWidget}
        defaults.update(kwargs)
        return super().formfield(**defaults)


class MunicipalityField(models.CharField):
    description = _("Nepal's Municipality")

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("max_length", 100)
        kwargs.setdefault("choices", [(m.name, m.name) for m in municipalities])
        super().__init__(*args, **kwargs)

    def formfield(self, **kwargs):
        defaults = {"widget": MunicipalitySelectWidget}
        defaults.update(kwargs)
        return super().formfield(**defaults)


class NepaliTimeField(models.TimeField):
    description = _("Nepali Time")


class NepaliDateField(models.CharField):
    description = _("Nepali Date (Bikram Sambat)")

    def __init__(self, *args, **kwargs):
        self.auto_now = kwargs.pop("auto_now", False)
        self.auto_now_add = kwargs.pop("auto_now_add", False)

        if self.auto_now or self.auto_now_add:
            kwargs.setdefault("editable", False)
            kwargs.setdefault("blank", True)

        kwargs.setdefault("max_length", 10)
        super().__init__(*args, **kwargs)

    def pre_save(self, model_instance, add):
        if self.auto_now or (self.auto_now_add and add):
            value = nepalidate.today().strftime("%Y-%m-%d")
            setattr(model_instance, self.attname, value)
            return value
        return super().pre_save(model_instance, add)

    def from_db_value(self, value, expression, connection):
        if value is None:
            return value
        try:
            return nepalidate.strptime(value, "%Y-%m-%d")
        except (ValueError, TypeError):
            return value

    def to_python(self, value):
        if value is None or isinstance(value, nepalidate):
            return value
        if isinstance(value, python_date):
            try:
                return nepalidate.from_date(value)
            except (ValueError, TypeError):
                return str(value)
        if isinstance(value, str):
            try:
                return nepalidate.strptime(value.strip(), "%Y-%m-%d")
            except (ValueError, TypeError):
                return value
        return super().to_python(value)

    def validate(self, value, model_instance):
        if isinstance(value, nepalidate):
            value = value.strftime("%Y-%m-%d")
        super().validate(value, model_instance)

    def run_validators(self, value):
        if isinstance(value, nepalidate):
            value = value.strftime("%Y-%m-%d")
        super().run_validators(value)

    def get_prep_value(self, value):
        if value is None:
            return value
        if isinstance(value, nepalidate):
            return value.strftime("%Y-%m-%d")
        if isinstance(value, python_date):
            try:
                return nepalidate.from_date(value).strftime("%Y-%m-%d")
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
        defaults = {
            "form_class": NepaliDateFormField,
            "widget": NepaliDatePickerWidget,
        }
        defaults.update(kwargs)
        return super().formfield(**defaults)
