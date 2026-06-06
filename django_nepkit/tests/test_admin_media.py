"""
Tests for ``NepaliModelAdmin`` media and address-chaining integration.
"""

from django.db import models

from django_nepkit.admin import NepaliModelAdmin
from django_nepkit.models import (
    DistrictField,
    MunicipalityField,
    NepaliTimeField,
    ProvinceField,
)
from django_nepkit.widgets import NepaliTimeWidget
from django.contrib.admin.sites import AdminSite


class _ChainedModel(models.Model):
    province = ProvinceField()
    district = DistrictField()
    municipality = MunicipalityField()

    class Meta:
        app_label = "django_nepkit"


class _TimeModel(models.Model):
    t = NepaliTimeField()

    class Meta:
        app_label = "django_nepkit"


class _PlainModel(models.Model):
    name = models.CharField(max_length=10)

    class Meta:
        app_label = "django_nepkit"


class TestNepaliModelAdminMedia:
    def test_includes_address_chaining_js(self):
        admin_cls = NepaliModelAdmin(_ChainedModel, AdminSite())
        js = admin_cls.media._js
        assert "django_nepkit/js/nepal-data.js" in js
        assert "django_nepkit/js/address-chaining.js" in js

    def test_chaining_js_ordered_after_data(self):
        admin_cls = NepaliModelAdmin(_ChainedModel, AdminSite())
        js = list(admin_cls.media._js)
        data_idx = js.index("django_nepkit/js/nepal-data.js")
        chain_idx = js.index("django_nepkit/js/address-chaining.js")
        assert data_idx < chain_idx

    def test_time_widget_carries_its_own_js(self):
        """The NepaliTimeWidget contributes its own JS via form media."""
        from django_nepkit.widgets import NepaliTimeWidget

        widget = NepaliTimeWidget()
        js = list(widget.media._js)
        assert "django_nepkit/js/nepali-time-init.js" in js


class TestAdminUsesNepaliTimeWidget:
    def test_time_field_gets_nepali_widget(self):
        admin_cls = NepaliModelAdmin(_TimeModel, AdminSite())
        ff = admin_cls.formfield_for_dbfield(
            _TimeModel._meta.get_field("t"), request=None
        )
        assert isinstance(ff.widget, NepaliTimeWidget)

    def test_time_widget_inherits_ne_setting(self):
        admin_cls = NepaliModelAdmin(_TimeModel, AdminSite())
        ff = admin_cls.formfield_for_dbfield(
            _TimeModel._meta.get_field("t"), request=None
        )
        assert ff.widget.ne is False
        assert ff.widget.en is True


class TestFormfieldForDbfieldIdempotency:
    def test_unrelated_field_falls_through(self):
        admin_cls = NepaliModelAdmin(_PlainModel, AdminSite())
        ff = admin_cls.formfield_for_dbfield(
            _PlainModel._meta.get_field("name"), request=None
        )
        assert ff is not None
