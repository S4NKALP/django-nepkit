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
    # Date/time fields - examples with and without Devanagari
    birth_date = NepaliDateField(ne=True)  # Devanagari
    birth_date_en = NepaliDateField(blank=True, null=True)  # English (default)
    registration_time = NepaliTimeField(auto_now_add=True, ne=True)  # Devanagari
    phone_number = NepaliPhoneNumberField()

    # Address chaining - examples with and without Devanagari
    province = ProvinceField(ne=True)  # Devanagari
    province_en = ProvinceField(blank=True, null=True)  # English (default)
    district = DistrictField(ne=True)  # Devanagari
    district_en = DistrictField(blank=True, null=True)  # English (default)
    municipality = MunicipalityField(ne=True)  # Devanagari
    municipality_en = MunicipalityField(blank=True, null=True)  # English (default)

    created_at = NepaliDateTimeField(auto_now_add=True, ne=True)  # Devanagari
    updated_at = NepaliDateTimeField(auto_now=True, ne=True)  # Devanagari

    def __str__(self):
        return self.name
