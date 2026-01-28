from __future__ import annotations

from typing import Any, Optional, Type

from nepali.datetime import nepalidate, nepalidatetime

try:
    from rest_framework import serializers
except ModuleNotFoundError as e:
    raise ModuleNotFoundError(
        "django-nepkit DRF support is optional. Install with `django-nepkit[drf]` "
        "to use `django_nepkit.serializers`."
    ) from e

from django_nepkit.utils import try_parse_nepali_date, try_parse_nepali_datetime

# --------------------------------------------------
# Base Serializer Field
# --------------------------------------------------


class BaseNepaliBSField(serializers.Field):
    """
    Base DRF field for Nepali (BS) Date / DateTime.

    - **Input**: BS string, or an already-parsed `nepalidate`/`nepalidatetime`
    - **Output**: formatted BS string (configurable)
    """

    format: str = ""
    nepali_type: Type[object] = object

    default_error_messages = {
        "invalid": "Invalid Bikram Sambat value. Expected format: {format}.",
        "invalid_type": "Invalid type. Expected a string.",
    }

    def __init__(self, *, format: Optional[str] = None, **kwargs: Any) -> None:
        """
        Args:
            format: Optional `strftime` format used for representation.
                    If not provided, uses the class default.
        """
        if format is not None:
            self.format = format
        super().__init__(**kwargs)

    def _parse(self, value: str):
        if self.nepali_type is nepalidate:
            return try_parse_nepali_date(value)
        if self.nepali_type is nepalidatetime:
            return try_parse_nepali_datetime(value)
        return None

    def to_representation(self, value: Any) -> Optional[str]:
        if value is None:
            return None

        if isinstance(value, self.nepali_type):
            return value.strftime(self.format)  # type: ignore[attr-defined]

        # If DB returns string, try to normalize it.
        if isinstance(value, str):
            parsed = self._parse(value)
            if parsed is not None:
                return parsed.strftime(self.format)  # type: ignore[attr-defined]

        # Fallback: best-effort stringify (keeps behavior non-breaking)
        return str(value)

    def to_internal_value(self, data: Any):
        if data in (None, ""):
            return None

        if isinstance(data, self.nepali_type):
            return data

        if not isinstance(data, str):
            self.fail("invalid_type")

        parsed = self._parse(data)
        if parsed is not None:
            return parsed

        self.fail("invalid", format=self.format)


# --------------------------------------------------
# Nepali Date (BS)
# --------------------------------------------------


class NepaliDateSerializerField(BaseNepaliBSField):
    """
    DRF field for Nepali BS Date (YYYY-MM-DD)
    """

    format = "%Y-%m-%d"
    nepali_type = nepalidate


# --------------------------------------------------
# Nepali DateTime (BS)
# --------------------------------------------------


class NepaliDateTimeSerializerField(BaseNepaliBSField):
    """
    DRF field for Nepali BS DateTime (YYYY-MM-DD HH:MM:SS)
    """

    format = "%Y-%m-%d %H:%M:%S"
    nepali_type = nepalidatetime
