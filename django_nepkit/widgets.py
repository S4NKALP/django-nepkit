import logging
from datetime import time as python_time

from django import forms
from django.urls import NoReverseMatch, reverse
from nepali.datetime import nepalidate
from nepali.number import english_to_nepali

from django_nepkit.conf import nepkit_settings
from django_nepkit.utils import BS_TIME_FORMAT, format_nepali_time

logger = logging.getLogger(__name__)


def _append_css_class(attrs, class_name: str):
    """Helper to add a CSS class safely."""
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

        if self.ne:
            attrs["data-ne"] = "true"
        if self.en:
            attrs["data-en"] = "true"

        attrs["data-format"] = self._default_format()
        self._configure_attrs(attrs)
        kwargs["attrs"] = attrs
        super().__init__(*args, **kwargs)

    def _default_format(self) -> str:
        return nepkit_settings.BS_DATE_FORMAT

    def _configure_attrs(self, attrs):
        css_class = getattr(self, "css_class", None)
        if css_class:
            _append_css_class(attrs, css_class)

    def _resolve_url(self, url_name, attr_name):
        """Resolve a URL name and return the URL string.

        On failure, log a warning and return an empty string so the JS
        can degrade gracefully.  The widget's data attribute is omitted
        entirely (rather than set to a broken value).
        """
        try:
            return reverse(url_name)
        except NoReverseMatch:
            logger.warning(
                "nepkit widget %r: URL name %r not found; "
                "the corresponding select will not auto-populate. "
                "Make sure 'django_nepkit.urls' is included in your URLconf.",
                self.__class__.__name__,
                url_name,
            )
            return ""

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        widget_attrs = context.get("widget", {}).get("attrs", {})

        url_name = getattr(self, "_url_name", None)
        if url_name:
            widget_attrs["data-url"] = self._resolve_url(url_name, "data-url")

        if self.htmx:
            hx_url_name = getattr(self, "_hx_url_name", None)
            if hx_url_name:
                widget_attrs["hx-get"] = self._resolve_url(hx_url_name, "hx-get")
                widget_attrs["hx-target"] = getattr(self, "_hx_target", "")
                widget_attrs["hx-trigger"] = "change"

        return context


class ChainedSelectWidget(forms.Select):
    class Media:
        js = (
            "django_nepkit/js/nepal-data.js",
            "django_nepkit/js/address-chaining.js",
        )


class ProvinceSelectWidget(NepaliWidgetMixin, ChainedSelectWidget):
    css_class = "nepkit-province-select"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.htmx:
            self._hx_url_name = "django_nepkit:district-list"
            self._hx_target = ".nepkit-district-select"


class DistrictSelectWidget(NepaliWidgetMixin, ChainedSelectWidget):
    css_class = "nepkit-district-select"
    _url_name = "django_nepkit:district-list"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.htmx:
            self._hx_url_name = "django_nepkit:municipality-list"
            self._hx_target = ".nepkit-municipality-select"


class MunicipalitySelectWidget(NepaliWidgetMixin, ChainedSelectWidget):
    css_class = "nepkit-municipality-select"
    _url_name = "django_nepkit:municipality-list"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.htmx:
            self._hx_url_name = "django_nepkit:municipality-list"
            self._hx_target = ".nepkit-municipality-select"


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
        super()._configure_attrs(attrs)
        classes = attrs.get("class", "")
        if "vDateField" in classes:
            classes = classes.replace("vDateField", "")
        attrs["class"] = classes

        _append_css_class(attrs, "nepkit-datepicker")
        attrs["autocomplete"] = "off"
        attrs["placeholder"] = (
            nepkit_settings.BS_DATE_FORMAT.replace("%Y", "YYYY")
            .replace("%m", "MM")
            .replace("%d", "DD")
        )

    def format_value(self, value):
        if value is None:
            return None
        from django_nepkit.utils import format_nepali_date

        try:
            if isinstance(value, nepalidate):
                if self.ne and hasattr(value, "strftime_ne"):
                    return value.strftime_ne(nepkit_settings.BS_DATE_FORMAT)
                return format_nepali_date(value, nepkit_settings.BS_DATE_FORMAT)
            if isinstance(value, str):
                return value
        except (ValueError, TypeError, AttributeError):
            logger.warning(
                "nepkit-datepicker: cannot format value %r; rendering empty", value
            )
        return ""


class NepaliTimeWidget(NepaliWidgetMixin, forms.TextInput):
    """Plain text input for time values with Devanagari digit support."""

    input_type = "text"
    css_class = "nepkit-time"

    class Media:
        js = ("django_nepkit/js/nepali-time-init.js",)

    def _default_format(self) -> str:
        return BS_TIME_FORMAT

    def _configure_attrs(self, attrs):
        super()._configure_attrs(attrs)
        _append_css_class(attrs, "nepkit-time-input")
        attrs["autocomplete"] = "off"
        fmt = nepkit_settings.BS_TIME_FORMAT
        attrs["placeholder"] = (
            fmt.replace("%H", "HH")
            .replace("%I", "hh")
            .replace("%M", "mm")
            .replace("%S", "ss")
            .replace("%p", "AM/PM")
        )

    def format_value(self, value):
        if value is None:
            return None
        if isinstance(value, python_time):
            try:
                formatted = format_nepali_time(value, nepkit_settings.BS_TIME_FORMAT)
            except (ValueError, TypeError):
                logger.warning(
                    "nepkit-time: cannot format value %r; rendering empty", value
                )
                return ""
            if self.ne and formatted:
                formatted = english_to_nepali(formatted)
            return formatted
        if isinstance(value, str):
            return value
        # Unknown type — refuse to leak a Python repr into the page.
        logger.warning(
            "nepkit-time: unexpected value type %s; rendering empty",
            type(value).__name__,
        )
        return ""
