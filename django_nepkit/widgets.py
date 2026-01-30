from django import forms
from django.urls import reverse_lazy
from nepali.datetime import nepalidate

from django_nepkit.conf import nepkit_settings


def _append_css_class(attrs, class_name: str):
    """
    Django-idiomatic helper to append a CSS class without clobbering existing ones.
    """
    existing = (attrs.get("class") or "").strip()
    attrs["class"] = (f"{existing} {class_name}").strip() if existing else class_name
    return attrs


class NepaliWidgetMixin:
    def __init__(self, *args, **kwargs):
        default_lang = nepkit_settings.DEFAULT_LANGUAGE
        self.ne = kwargs.pop("ne", default_lang == "ne")
        
        self.en = kwargs.pop("en", not self.ne)
        self.htmx = kwargs.pop("htmx", False)

        attrs = kwargs.get("attrs", {}) or {}

        # Add data attributes
        if self.ne:
            attrs["data-ne"] = "true"
        if self.en:
            attrs["data-en"] = "true"

        # Hook for subclasses to add specific classes/attrs
        self._configure_attrs(attrs)

        kwargs["attrs"] = attrs
        super().__init__(*args, **kwargs)

    def _configure_attrs(self, attrs):
        """Override in subclasses to add specific classes or attributes."""
        pass


class ChainedSelectWidget(forms.Select):
    class Media:
        js = (
            "django_nepkit/js/nepal-data.js",
            "django_nepkit/js/address-chaining.js",
        )


class ProvinceSelectWidget(NepaliWidgetMixin, ChainedSelectWidget):
    def _configure_attrs(self, attrs):
        _append_css_class(attrs, "nepkit-province-select")
        if self.htmx:
            url = reverse_lazy("django_nepkit:district-list")
            attrs.update({
                "hx-get": url,
                "hx-target": ".nepkit-district-select",
                "hx-trigger": "change",
            })


class DistrictSelectWidget(NepaliWidgetMixin, ChainedSelectWidget):
    def _configure_attrs(self, attrs):
        _append_css_class(attrs, "nepkit-district-select")
        url = reverse_lazy("django_nepkit:district-list")
        attrs["data-url"] = url
        
        if self.htmx:
            url_muni = reverse_lazy("django_nepkit:municipality-list")
            attrs.update({
                "hx-get": url_muni,
                "hx-target": ".nepkit-municipality-select",
                "hx-trigger": "change",
            })


class MunicipalitySelectWidget(NepaliWidgetMixin, ChainedSelectWidget):
    def _configure_attrs(self, attrs):
        _append_css_class(attrs, "nepkit-municipality-select")
        url = reverse_lazy("django_nepkit:municipality-list")
        attrs["data-url"] = url


class NepaliDatePickerWidget(NepaliWidgetMixin, forms.TextInput):
    input_type = "text"

    class Media:
        css = {
            "all": (
                "https://nepalidatepicker.sajanmaharjan.com.np/v5/nepali.datepicker/css/nepali.datepicker.v5.0.6.min.css",
            )
        }
        js = (
            "https://code.jquery.com/jquery-3.5.1.slim.min.js",
            "https://nepalidatepicker.sajanmaharjan.com.np/v5/nepali.datepicker/js/nepali.datepicker.v5.0.6.min.js",
            "django_nepkit/js/nepali-datepicker-init.js",
        )

    def _configure_attrs(self, attrs):
        # Clean up Django admin class if present
        classes = attrs.get("class", "")
        if "vDateField" in classes:
            classes = classes.replace("vDateField", "")
        attrs["class"] = classes

        _append_css_class(attrs, "nepkit-datepicker")
        attrs["autocomplete"] = "off"
        attrs["placeholder"] = "YYYY-MM-DD"

    def format_value(self, value):
        if value is None:
            return None

        if self.ne and isinstance(value, nepalidate):
            if hasattr(value, "strftime_ne"):
                return value.strftime_ne("%Y-%m-%d")

        return super().format_value(value)
