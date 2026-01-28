from django import forms
from django.urls import reverse_lazy


# --------------------------------------------------
# Utility mixin
# --------------------------------------------------

class ClassAttrMixin:
    """
    Safely append CSS classes to widget attrs.
    """

    css_class = ""

    def _build_attrs(self, attrs):
        attrs = attrs or {}
        classes = attrs.get("class", "").split()
        if self.css_class:
            classes.append(self.css_class)
        attrs["class"] = " ".join(dict.fromkeys(classes))
        return attrs


# --------------------------------------------------
# Chained Select Base
# --------------------------------------------------

class ChainedSelectWidget(ClassAttrMixin, forms.Select):
    """
    Base widget for chained location selects.
    """

    class Media:
        js = ("django_nepkit/js/address-chaining.js",)


# --------------------------------------------------
# Province / District / Municipality Widgets
# --------------------------------------------------

class ProvinceSelectWidget(ChainedSelectWidget):
    css_class = "nepkit-province-select"

    def __init__(self, *args, **kwargs):
        kwargs["attrs"] = self._build_attrs(kwargs.get("attrs"))
        super().__init__(*args, **kwargs)


class DistrictSelectWidget(ChainedSelectWidget):
    css_class = "nepkit-district-select"

    def __init__(self, *args, **kwargs):
        attrs = self._build_attrs(kwargs.get("attrs"))
        attrs.setdefault("data-url", reverse_lazy("django_nepkit:district-list"))
        kwargs["attrs"] = attrs
        super().__init__(*args, **kwargs)


class MunicipalitySelectWidget(ChainedSelectWidget):
    css_class = "nepkit-municipality-select"

    def __init__(self, *args, **kwargs):
        attrs = self._build_attrs(kwargs.get("attrs"))
        attrs.setdefault("data-url", reverse_lazy("django_nepkit:municipality-list"))
        kwargs["attrs"] = attrs
        super().__init__(*args, **kwargs)


# --------------------------------------------------
# Nepali Date Picker
# --------------------------------------------------

class NepaliDatePickerWidget(ClassAttrMixin, forms.TextInput):
    """
    Nepali BS date picker widget.
    """

    input_type = "text"
    css_class = "nepkit-datepicker"

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

        # Remove Django admin default class
        classes = attrs.get("class", "").replace("vDateField", "").strip()
        attrs["class"] = classes

        attrs = self._build_attrs(attrs)
        attrs.setdefault("autocomplete", "off")
        attrs.setdefault("placeholder", "YYYY-MM-DD")

        kwargs["attrs"] = attrs
        super().__init__(*args, **kwargs)
