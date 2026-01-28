from django.db import models
from django.utils.translation import gettext_lazy as _
from nepali.locations import districts, municipalities, provices

from django_nepkit.validators import validate_nepali_phone_number
from django_nepkit.widgets import (
    DistrictSelectWidget,
    MunicipalitySelectWidget,
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
