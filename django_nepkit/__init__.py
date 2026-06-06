"""
django-nepkit: Nepali date, time, phone, currency and address helpers for
Django. Framework-agnostic — no DRF or django-filter dependency.
"""

from .conf import nepkit_settings
from .models import (
    NepaliCurrencyField,
    NepaliDateField,
    NepaliDateTimeField,
    NepaliPhoneNumberField,
    NepaliTimeField,
    DistrictField,
    MunicipalityField,
    ProvinceField,
)
from .admin import (
    NepaliAdminMixin,
    NepaliDateFilter,
    NepaliModelAdmin,
    NepaliMonthFilter,
    format_nepali_date,
    format_nepali_datetime,
)
from .widgets import (
    DistrictSelectWidget,
    MunicipalitySelectWidget,
    NepaliDatePickerWidget,
    NepaliTimeWidget,
    ProvinceSelectWidget,
)
from .api import (
    build_localized_payload,
    deserialize_nepali_currency,
    deserialize_nepali_date,
    deserialize_nepali_datetime,
    deserialize_nepali_time,
    serialize_nepali_currency,
    serialize_nepali_date,
    serialize_nepali_datetime,
    serialize_nepali_time,
    to_decimal,
)
from .utils import (
    BS_DATE_FORMAT,
    BS_DATETIME_FORMAT,
    BS_TIME_FORMAT,
    english_to_nepali_unicode,
    format_nepali_currency,
    format_nepali_time,
    normalize_address,
    number_to_nepali_words,
)

# ``BS_DATE_FORMAT`` / ``BS_DATETIME_FORMAT`` / ``BS_TIME_FORMAT`` are
# re-exported via ``utils.__getattr__`` so they reflect the *current*
# ``settings.NEPKIT`` value at access time.  Importing the names here
# gives users a snapshot at their import time, which is the historical
# behaviour.  To get a live read, use ``nepkit_settings.BS_DATE_FORMAT``.

__all__ = [
    # Settings
    "nepkit_settings",
    # Model fields
    "NepaliDateField",
    "NepaliTimeField",
    "NepaliDateTimeField",
    "NepaliPhoneNumberField",
    "ProvinceField",
    "DistrictField",
    "MunicipalityField",
    "NepaliCurrencyField",
    # Admin
    "NepaliDateFilter",
    "NepaliMonthFilter",
    "format_nepali_date",
    "format_nepali_datetime",
    "NepaliModelAdmin",
    "NepaliAdminMixin",
    # Widgets
    "NepaliDatePickerWidget",
    "NepaliTimeWidget",
    "ProvinceSelectWidget",
    "DistrictSelectWidget",
    "MunicipalitySelectWidget",
    # Framework-agnostic API helpers (use directly in any view / framework)
    "build_localized_payload",
    "deserialize_nepali_currency",
    "deserialize_nepali_date",
    "deserialize_nepali_datetime",
    "deserialize_nepali_time",
    "serialize_nepali_currency",
    "serialize_nepali_date",
    "serialize_nepali_datetime",
    "serialize_nepali_time",
    "to_decimal",
    # Utility helpers
    "BS_DATE_FORMAT",
    "BS_DATETIME_FORMAT",
    "BS_TIME_FORMAT",
    "english_to_nepali_unicode",
    "format_nepali_currency",
    "format_nepali_time",
    "normalize_address",
    "number_to_nepali_words",
]
