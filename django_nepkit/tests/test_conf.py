"""
Tests for django-nepkit configuration (conf.py).
"""

import pytest


class TestNepkitSettings:
    """Tests for NepkitSettings configuration handling."""

    def test_default_language_is_english(self):
        """Default language should be 'en'."""
        from django_nepkit.conf import NepkitSettings, DEFAULTS

        settings = NepkitSettings(user_settings={}, defaults=DEFAULTS)
        assert settings.DEFAULT_LANGUAGE == "en"

    def test_default_date_formats(self):
        """Default date input formats should be present."""
        from django_nepkit.conf import NepkitSettings, DEFAULTS

        settings = NepkitSettings(user_settings={}, defaults=DEFAULTS)
        assert "%Y-%m-%d" in settings.DATE_INPUT_FORMATS
        assert "%d/%m/%Y" in settings.DATE_INPUT_FORMATS
        assert "%d-%m-%Y" in settings.DATE_INPUT_FORMATS

    def test_default_bs_date_format(self):
        """Default BS date format should be '%Y-%m-%d'."""
        from django_nepkit.conf import NepkitSettings, DEFAULTS

        settings = NepkitSettings(user_settings={}, defaults=DEFAULTS)
        assert settings.BS_DATE_FORMAT == "%Y-%m-%d"

    def test_default_bs_datetime_format(self):
        """Default BS datetime format should include time."""
        from django_nepkit.conf import NepkitSettings, DEFAULTS

        settings = NepkitSettings(user_settings={}, defaults=DEFAULTS)
        assert settings.BS_DATETIME_FORMAT == "%Y-%m-%d %H:%M:%S"

    def test_default_time_format(self):
        """Default time format should be 12-hour."""
        from django_nepkit.conf import NepkitSettings, DEFAULTS

        settings = NepkitSettings(user_settings={}, defaults=DEFAULTS)
        assert settings.TIME_FORMAT == 12

    def test_default_admin_datepicker(self):
        """Admin datepicker should be enabled by default."""
        from django_nepkit.conf import NepkitSettings, DEFAULTS

        settings = NepkitSettings(user_settings={}, defaults=DEFAULTS)
        assert settings.ADMIN_DATEPICKER is True

    def test_user_setting_overrides_default(self):
        """User settings should override defaults."""
        from django_nepkit.conf import NepkitSettings, DEFAULTS

        settings = NepkitSettings(
            user_settings={"DEFAULT_LANGUAGE": "ne"}, defaults=DEFAULTS
        )
        assert settings.DEFAULT_LANGUAGE == "ne"

    def test_invalid_setting_raises_attribute_error(self):
        """Accessing an invalid setting key should raise AttributeError."""
        from django_nepkit.conf import NepkitSettings, DEFAULTS

        settings = NepkitSettings(user_settings={}, defaults=DEFAULTS)
        with pytest.raises(AttributeError, match="Invalid NEPKIT setting"):
            _ = settings.NONEXISTENT_SETTING

    def test_django_settings_override(self):
        """nepkit_settings reads from Django's NEPKIT dict at import time."""
        # The module-level nepkit_settings already uses NEPKIT from settings.py
        from django_nepkit.conf import nepkit_settings

        # Our test settings.py sets DEFAULT_LANGUAGE = "en"
        assert nepkit_settings.DEFAULT_LANGUAGE == "en"

    def test_user_setting_partial_override(self):
        """Only explicitly set keys are overridden; others use defaults."""
        from django_nepkit.conf import NepkitSettings, DEFAULTS

        settings = NepkitSettings(user_settings={"TIME_FORMAT": 24}, defaults=DEFAULTS)
        assert settings.TIME_FORMAT == 24
        # Others still use defaults
        assert settings.DEFAULT_LANGUAGE == "en"
        assert settings.ADMIN_DATEPICKER is True
