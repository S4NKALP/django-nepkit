"""
Language parameter utilities for django-nepkit.
Helper functions to resolve Nepali/English language parameters consistently.
"""

from django_nepkit.conf import nepkit_settings


def resolve_language_params(ne=None, en=None, **kwargs):
    """
    Resolve language parameters with fallback to default settings.
    """
    default_lang = nepkit_settings.DEFAULT_LANGUAGE

    # Extract from kwargs if provided
    if ne is None and "ne" in kwargs:
        ne = kwargs.get("ne")
    if en is None and "en" in kwargs:
        en = kwargs.get("en")

    # Set defaults
    if ne is None:
        ne = default_lang == "ne"

    # Handle en parameter logic
    explicit_en = en is not None
    if en is None:
        en = not ne

    # If ne is True and en wasn't explicitly set, en should be False
    if ne and not explicit_en:
        en = False

    return ne, en


def pop_language_params(kwargs):
    """
    Pop ne/en parameters from kwargs dict and return resolved values.
    """
    default_lang = nepkit_settings.DEFAULT_LANGUAGE
    ne = kwargs.pop("ne", default_lang == "ne")

    explicit_en = "en" in kwargs
    en_value = kwargs.pop("en", not ne)

    if ne and not explicit_en:
        en = False
    else:
        en = en_value

    return ne, en
