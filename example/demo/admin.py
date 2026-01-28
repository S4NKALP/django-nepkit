from django.contrib import admin

from django_nepkit import NepaliModelAdmin

from .models import Person


@admin.register(Person)
class PersonAdmin(NepaliModelAdmin):
    list_display = (
        "name",
        "display_birth_date",
        "phone_number",
        "province",
        "district",
        "municipality",
        "display_created_at",
        "display_updated_at",
    )
    list_filter = ("birth_date", "province", "district")
    search_fields = ("name", "phone_number")

    def display_birth_date(self, obj):
        """Display birth date with Nepali month names"""
        return self.format_nepali_date(obj.birth_date)

    display_birth_date.short_description = "Birth Date"
    display_birth_date.admin_order_field = "birth_date"

    def display_created_at(self, obj):
        """Display created date with Nepali month names"""
        return self.format_nepali_datetime(obj.created_at)

    display_created_at.short_description = "Created At"
    display_created_at.admin_order_field = "created_at"

    def display_updated_at(self, obj):
        """Display updated date with Nepali month names"""
        return self.format_nepali_datetime(obj.updated_at)

    display_updated_at.short_description = "Updated At"
    display_updated_at.admin_order_field = "updated_at"
