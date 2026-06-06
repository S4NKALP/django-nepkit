import threading

from django.conf import settings

DEFAULTS = {
    "DEFAULT_LANGUAGE": "en",
    "DATE_INPUT_FORMATS": ["%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y"],
    "TIME_INPUT_FORMATS": ["%H:%M:%S", "%H:%M", "%I:%M %p", "%I:%M:%S %p"],
    "ADMIN_DATEPICKER": True,
    "TIME_FORMAT": 12,
    "BS_DATE_FORMAT": "%Y-%m-%d",
    "BS_DATETIME_FORMAT": "%Y-%m-%d %H:%M:%S",
    "BS_TIME_FORMAT": "%I:%M %p",
}


class NepkitSettings:
    """
    Lazy NEPKIT settings accessor.

    Settings are re-read from ``settings.NEPKIT`` on **every** attribute
    access so that ``override_settings`` and ``setting_changed`` are honoured
    in tests and runtime.

    When constructed with an explicit ``user_settings`` dict (e.g. in unit
    tests that instantiate ``NepkitSettings(...)`` directly), that dict is
    used verbatim and the live ``settings.NEPKIT`` is ignored.  The
    module-level ``nepkit_settings`` instance below does *not* pass
    ``user_settings``, so it always reflects the project's current
    ``NEPKIT`` setting.
    """

    def __init__(self, user_settings=None, defaults=None):
        self._explicit_user_settings = user_settings
        self.defaults = defaults or DEFAULTS
        # Lock only used when ``user_settings`` is None — the live case
        # uses ``getattr(settings, ...)`` which is already thread-safe.
        self._lock = threading.Lock()

    def _user_settings(self):
        if self._explicit_user_settings is not None:
            return self._explicit_user_settings
        return getattr(settings, "NEPKIT", {}) or {}

    def __getattr__(self, attr):
        # Avoid intercepting dunder / private lookups (copy, deepcopy, etc.)
        if attr.startswith("_") or attr in {
            "choices",
            "does_not_exist",
        }:
            raise AttributeError(attr)
        if attr not in self.defaults:
            raise AttributeError(f"Invalid NEPKIT setting: '{attr}'")
        try:
            with self._lock:
                user = self._user_settings()
            val = user[attr]
        except (KeyError, AttributeError, TypeError):
            val = self.defaults[attr]
        return val

    def __setattr__(self, attr, value):
        if attr.startswith("_") or attr == "defaults":
            super().__setattr__(attr, value)
        else:
            raise AttributeError(
                f"NepkitSettings is read-only; to override {attr!r} set "
                f"settings.NEPKIT['{attr}'] = {value!r}"
            )


nepkit_settings = NepkitSettings(defaults=DEFAULTS)
