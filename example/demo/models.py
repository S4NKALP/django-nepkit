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
    # Date/time fields - now default to English via NEPKIT['DEFAULT_LANGUAGE']
    birth_date = NepaliDateField()  # Defaults to en=True
    birth_date_ne = NepaliDateField(ne=True, blank=True, null=True)  # Explicitly Nepali
    registration_time = NepaliTimeField(auto_now_add=True)  # Defaults to en=True
    phone_number = NepaliPhoneNumberField()

    # Address chaining - now default to English via NEPKIT['DEFAULT_LANGUAGE']
    province = ProvinceField()  # Defaults to en=True
    province_ne = ProvinceField(ne=True, blank=True, null=True)  # Explicitly Nepali
    district = DistrictField()  # Defaults to en=True
    district_ne = DistrictField(ne=True, blank=True, null=True)  # Explicitly Nepali
    municipality = MunicipalityField()  # Defaults to en=True
    municipality_ne = MunicipalityField(ne=True, blank=True, null=True)  # Explicitly Nepali

    created_at = NepaliDateTimeField(auto_now_add=True)  # Defaults to en=True
    updated_at = NepaliDateTimeField(auto_now=True)  # Defaults to en=True

    def __str__(self):
        return self.name
