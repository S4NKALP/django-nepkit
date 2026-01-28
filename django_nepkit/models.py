from django.db import models
from django.utils.translation import gettext_lazy as _

from django_nepkit.validators import validate_nepali_phone_number


class NepaliPhoneNumberField(models.CharField):
    description = _("Nepali phone number")

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("max_length", 10)
        super().__init__(*args, **kwargs)
        self.validators.append(validate_nepali_phone_number)
