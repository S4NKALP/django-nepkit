from django import forms
from django.urls import reverse_lazy


def _append_css_class(attrs, class_name: str):
    """
    Django-idiomatic helper to append a CSS class without clobbering existing ones.
    """
    existing = (attrs.get("class") or "").strip()
    attrs["class"] = (f"{existing} {class_name}").strip() if existing else class_name
    return attrs


class ChainedSelectWidget(forms.Select):
    class Media:
        js = ("django_nepkit/js/address-chaining.js",)


class ProvinceSelectWidget(ChainedSelectWidget):
    def __init__(self, *args, **kwargs):
        attrs = kwargs.get("attrs", {})
        _append_css_class(attrs, "nepkit-province-select")
        kwargs["attrs"] = attrs
        super().__init__(*args, **kwargs)


class DistrictSelectWidget(ChainedSelectWidget):
    def __init__(self, *args, **kwargs):
        attrs = kwargs.get("attrs", {})
        _append_css_class(attrs, "nepkit-district-select")
        attrs["data-url"] = reverse_lazy("django_nepkit:district-list")
        kwargs["attrs"] = attrs
        super().__init__(*args, **kwargs)


class MunicipalitySelectWidget(ChainedSelectWidget):
    def __init__(self, *args, **kwargs):
        attrs = kwargs.get("attrs", {})
        _append_css_class(attrs, "nepkit-municipality-select")
        attrs["data-url"] = reverse_lazy("django_nepkit:municipality-list")
        kwargs["attrs"] = attrs
        super().__init__(*args, **kwargs)


class NepaliDatePickerWidget(forms.TextInput):
    input_type = "text"

    class Media:
        css = {
            "all": (
                "https://unpkg.com/nepali-date-picker@2.0.2/dist/nepaliDatePicker.min.css",
            )
        }
        js = (
            "https://code.jquery.com/jquery-3.5.1.slim.min.js",
            "https://unpkg.com/nepali-date-picker@2.0.2/dist/nepaliDatePicker.min.js",
            "django_nepkit/js/nepali-datepicker-init.js",
        )

    def __init__(self, *args, **kwargs):
        attrs = kwargs.get("attrs", {})
        # Ensure we don't have vDateField class which triggers Django admin calendar
        classes = attrs.get("class", "")
        if "vDateField" in classes:
            classes = classes.replace("vDateField", "")

        attrs["class"] = (classes or "").strip()
        _append_css_class(attrs, "nepkit-datepicker")
        attrs["autocomplete"] = "off"
        attrs["placeholder"] = "YYYY-MM-DD"
        kwargs["attrs"] = attrs
        super().__init__(*args, **kwargs)
