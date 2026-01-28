from django.db import models
from django_nepkit import (
    NepaliDateField,
    NepaliTimeField,
    NepaliPhoneNumberField,
    NepaliDateTimeField,
    ProvinceField,
    DistrictField,
    MunicipalityField,
)


class Person(models.Model):
    name = models.CharField(max_length=100)
    birth_date = NepaliDateField()
    registration_time = NepaliTimeField(auto_now_add=True)
    phone_number = NepaliPhoneNumberField()

    # Address chaining
    province = ProvinceField()
    district = DistrictField()
    municipality = MunicipalityField()
    created_at = NepaliDateTimeField(auto_now_add=True)
    updated_at = NepaliDateTimeField(auto_now=True)

    def __str__(self):
        return self.name
