from django.contrib import admin

from django_nepkit import NepaliModelAdmin

from .models import Person


@admin.register(Person)
class PersonAdmin(NepaliModelAdmin):
    list_display = (
        "name",
        "birth_date",
        "birth_date_en",
        "phone_number",
        "province",
        "province_en",
        "district",
        "district_en",
        "municipality",
        "municipality_en",
        "created_at",
        "updated_at",
    )
    list_filter = ("birth_date", "province", "district")
    search_fields = ("name", "phone_number")
