from nepali.datetime import nepalidate, nepalidatetime
from rest_framework import serializers

# --------------------------------------------------
# Base Serializer Field
# --------------------------------------------------


class BaseNepaliBSField(serializers.Field):
    """
    Base DRF field for Nepali (BS) Date / DateTime.
    """

    format = None
    nepali_type = None
    error_messages = {"invalid": "Invalid Bikram Sambat format. Expected {format}."}

    def to_representation(self, value):
        if value is None:
            return None

        if isinstance(value, self.nepali_type):
            return value.strftime(self.format)

        # Fallback: DB string
        return str(value)

    def to_internal_value(self, data):
        if data in (None, ""):
            return None

        if isinstance(data, self.nepali_type):
            return data

        if isinstance(data, str):
            try:
                return self.nepali_type.strptime(data.strip(), self.format)
            except Exception:
                self.fail("invalid", format=self.format)

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
