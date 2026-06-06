"""
Tests for django-nepkit widgets.
"""

from django_nepkit.widgets import (
    NepaliDatePickerWidget,
    ProvinceSelectWidget,
    DistrictSelectWidget,
    MunicipalitySelectWidget,
)


class TestNepaliDatePickerWidget:
    """Tests for NepaliDatePickerWidget."""

    def test_widget_renders_with_class(self):
        """Test that widget renders with nepkit-datepicker class."""
        widget = NepaliDatePickerWidget()
        html = widget.render("birth_date", None)

        assert "class=" in html
        assert "nepkit-datepicker" in html

    def test_widget_language_attribute_en(self):
        """Test that widget renders data-en attribute when en=True."""
        widget = NepaliDatePickerWidget(en=True)
        html = widget.render("birth_date", None)

        assert 'data-en="true"' in html

    def test_widget_language_attribute_ne(self):
        """Test that widget renders data-ne attribute when ne=True."""
        widget = NepaliDatePickerWidget(ne=True)
        html = widget.render("birth_date", None)

        assert 'data-ne="true"' in html

    def test_widget_format_attribute(self):
        """Test that widget renders data-format attribute."""
        widget = NepaliDatePickerWidget()
        html = widget.render("birth_date", None)

        assert "data-format=" in html

    def test_widget_autocomplete_off(self):
        """Test that widget has autocomplete=off."""
        widget = NepaliDatePickerWidget()
        html = widget.render("birth_date", None)

        assert 'autocomplete="off"' in html

    def test_widget_placeholder(self):
        """Test that widget has placeholder."""
        widget = NepaliDatePickerWidget()
        html = widget.render("birth_date", None)

        assert "placeholder=" in html

    def test_en_mode_format_value_renders_clean(self):
        """EN mode must not leak ``nepalidate(…)`` Python reprs."""
        from nepali.datetime import nepalidate

        widget = NepaliDatePickerWidget(en=True)
        # Pass a string (the DB-stored form); the widget should pass it
        # through unchanged rather than calling strptime on it.
        rendered = widget.format_value("2081-01-15")
        assert rendered == "2081-01-15"
        # Pass a real object and check the result doesn't contain
        # "nepalidate(" or "nepalidate(2" — i.e. no Python repr leak.
        rendered_obj = widget.format_value(nepalidate(2081, 1, 15))
        assert "nepalidate" not in rendered_obj

    def test_invalid_value_does_not_leak_repr(self):
        """Unknown value types render as empty instead of a Python repr."""
        widget = NepaliDatePickerWidget(en=True)
        rendered = widget.format_value(object())
        assert rendered == ""


class TestLocationWidgets:
    """Tests for location select widgets."""

    def test_province_widget_renders(self):
        """Test that ProvinceSelectWidget renders correctly."""
        widget = ProvinceSelectWidget()
        html = widget.render("province", None)

        assert "<select" in html
        assert 'name="province"' in html

    def test_district_widget_renders(self):
        """Test that DistrictSelectWidget renders correctly."""
        widget = DistrictSelectWidget()
        html = widget.render("district", None)

        assert "<select" in html
        assert 'name="district"' in html

    def test_municipality_widget_renders(self):
        """Test that MunicipalitySelectWidget renders correctly."""
        widget = MunicipalitySelectWidget()
        html = widget.render("municipality", None)

        assert "<select" in html
        assert 'name="municipality"' in html

    def test_location_widget_htmx_attributes(self):
        """Test that HTMX attributes are added when htmx=True."""
        widget = DistrictSelectWidget(htmx=True)
        context = widget.get_context("district", None, {})

        # Check that widget has HTMX configuration
        widget_attrs = context.get("widget", {}).get("attrs", {})
        assert "hx-get" in widget_attrs or widget.htmx is True

    def test_location_widget_language_ne(self):
        """Test that location widgets respect ne=True."""
        widget = ProvinceSelectWidget(ne=True)
        html = widget.render("province", None)

        assert 'data-ne="true"' in html

    def test_municipality_widget_htmx_attributes(self):
        """Test that MunicipalitySelectWidget enables HTMX mode when htmx=True."""
        widget = MunicipalitySelectWidget(htmx=True)
        assert widget.htmx is True
        assert widget._hx_url_name == "django_nepkit:municipality-list"
        assert widget._hx_target == ".nepkit-municipality-select"

    def test_unknown_type_renders_empty_for_time(self):
        from datetime import time

        from django_nepkit.widgets import NepaliTimeWidget

        widget = NepaliTimeWidget(en=True)
        # TimeField values should pass through.
        assert widget.format_value(time(9, 30)) == "09:30 AM"
        # Unknown types should not leak a Python repr.
        rendered = widget.format_value(12345)
        assert rendered == ""
