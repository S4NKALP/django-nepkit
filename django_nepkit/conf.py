from django.conf import settings

DEFAULTS = {
    "DEFAULT_LANGUAGE": "en",
    "DATE_INPUT_FORMATS": ["%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y"],
    "ADMIN_DATEPICKER": True,
    "TIME_FORMAT": 12,
}


class NepkitSettings:
    """
    A settings object that allows items to be accessed as properties.
    """

    def __init__(self, user_settings=None, defaults=None):
        self._user_settings = user_settings or {}
        self.defaults = defaults or DEFAULTS

    def __getattr__(self, attr):
        if attr not in self.defaults:
            raise AttributeError(f"Invalid NEPKIT setting: '{attr}'")

        try:
            # Check for user setting
            val = self._user_settings[attr]
        except KeyError:
            # Fall back to defaults
            val = self.defaults[attr]

        return val


nepkit_settings = NepkitSettings(getattr(settings, "NEPKIT", {}), DEFAULTS)
