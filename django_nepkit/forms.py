from django import forms

from django_nepkit.validators import validate_nepali_phone_number


class NepaliPhoneNumberField(forms.CharField):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.validators.append(validate_nepali_phone_number)
