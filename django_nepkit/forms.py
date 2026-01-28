from datetime import date as python_date

from django import forms
from django.utils.translation import gettext_lazy as _
from nepali.datetime import nepalidate

from django_nepkit.validators import validate_nepali_phone_number
from django_nepkit.widgets import NepaliDatePickerWidget


class NepaliPhoneNumberField(forms.CharField):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.validators.append(validate_nepali_phone_number)


class NepaliDateFormField(forms.DateField):
    widget = NepaliDatePickerWidget

    def __init__(self, *args, **kwargs):
        kwargs.pop("max_length", None)
        super().__init__(*args, **kwargs)

    def to_python(self, value):
        if value in self.empty_values:
            return None
        if isinstance(value, nepalidate):
            return value
        if isinstance(value, python_date):
            return nepalidate.from_date(value)
        try:
            return nepalidate.strptime(str(value).strip(), "%Y-%m-%d")
        except Exception:
            raise forms.ValidationError(
                _("Enter a valid Nepali date in YYYY-MM-DD format."),
                code="invalid",
            )
