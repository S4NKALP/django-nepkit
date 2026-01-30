import pytest
from django_nepkit.admin import NepaliModelAdmin
from django_nepkit.models import NepaliCurrencyField
from django.db import models
from django.contrib.admin.sites import AdminSite

class MockModel(models.Model):
    amount = NepaliCurrencyField()
    class Meta:
        app_label = 'django_nepkit'

class MockAdmin(NepaliModelAdmin):
    list_display = ('amount',)

def test_admin_currency_formatting():
    admin = MockAdmin(MockModel, AdminSite())
    displays = admin.get_list_display(None)
    
    # The first item should now be a callable (the display function)
    assert callable(displays[0])
    
    # Test the formatter directly
    obj = MockModel(amount=1234567)
    assert admin.format_nepali_currency(obj.amount) == "Rs. 12,34,567"
