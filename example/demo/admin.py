from django.contrib import admin

from django_nepkit import NepaliModelAdmin

from .models import Person


@admin.register(Person)
class PersonAdmin(NepaliModelAdmin):
    list_display = (
        "name",
        "birth_date",
        "birth_date_ne",
        "phone_number",
        "province",
        "province_ne",
        "district",
        "district_ne",
        "municipality",
        "municipality_ne",
        "created_at",
        "updated_at",
    )
    list_filter = ("birth_date", "province", "district")
    search_fields = ("name", "phone_number")
