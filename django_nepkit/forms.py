from datetime import date as python_date

from django import forms
from django.utils.translation import gettext_lazy as _

from nepali.datetime import nepalidate
from django_nepkit.validators import validate_nepali_phone_number
from django_nepkit.widgets import NepaliDatePickerWidget


# --------------------------------------------------
# Nepali Phone Number Form Field
# --------------------------------------------------

class NepaliPhoneNumberField(forms.CharField):
    """
    Form field for Nepali phone numbers.
    """

    default_error_messages = {
        "invalid": _("Enter a valid Nepali phone number."),
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.validators.append(validate_nepali_phone_number)


# --------------------------------------------------
# Nepali Date (BS) Form Field
# --------------------------------------------------

class NepaliDateFormField(forms.Field):
    """
    Form field for Nepali (Bikram Sambat) date.

    Accepts:
    - YYYY-MM-DD (string)
    - python date
    - nepalidate instance

    Returns:
    - nepalidate instance
    """

    widget = NepaliDatePickerWidget

    default_error_messages = {
        "invalid": _("Enter a valid Nepali date in YYYY-MM-DD format."),
    }

    def to_python(self, value):
        if value in self.empty_values:
            return None

        if isinstance(value, nepalidate):
            return value

        if isinstance(value, python_date):
            return nepalidate.from_date(value)

        if isinstance(value, str):
            try:
                return nepalidate.strptime(value.strip(), "%Y-%m-%d")
            except (ValueError, TypeError):
                self.fail("invalid")

        self.fail("invalid")

    def validate(self, value):
        """
        Override default validation to allow nepalidate objects.
        """
        if value is None:
            return
        if not isinstance(value, nepalidate):
            self.fail("invalid")
