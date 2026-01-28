from django import forms
from django.urls import reverse_lazy


class ChainedSelectWidget(forms.Select):
    class Media:
        js = ("django_nepkit/js/address-chaining.js",)


class ProvinceSelectWidget(ChainedSelectWidget):
    def __init__(self, *args, **kwargs):
        attrs = kwargs.get("attrs", {})
        attrs["class"] = attrs.get("class", "") + " nepkit-province-select"
        kwargs["attrs"] = attrs
        super().__init__(*args, **kwargs)


class DistrictSelectWidget(ChainedSelectWidget):
    def __init__(self, *args, **kwargs):
        attrs = kwargs.get("attrs", {})
        attrs["class"] = attrs.get("class", "") + " nepkit-district-select"
        attrs["data-url"] = reverse_lazy("django_nepkit:district-list")
        kwargs["attrs"] = attrs
        super().__init__(*args, **kwargs)


class MunicipalitySelectWidget(ChainedSelectWidget):
    def __init__(self, *args, **kwargs):
        attrs = kwargs.get("attrs", {})
        attrs["class"] = attrs.get("class", "") + " nepkit-municipality-select"
        attrs["data-url"] = reverse_lazy("django_nepkit:municipality-list")
        kwargs["attrs"] = attrs
        super().__init__(*args, **kwargs)
