import datetime

from django import template
from django.utils.safestring import mark_safe

from nepali.datetime import nepalidate, nepalihumanize
from nepali.number import nepalinumber


register = template.Library()


# --------------------------------------------------
# Internal helpers
# --------------------------------------------------

def _to_nepali_date(value):
    """
    Normalize AD date/datetime or BS date to nepalidate.
    """
    if value is None:
        return None

    if isinstance(value, nepalidate):
        return value

    if isinstance(value, (datetime.date, datetime.datetime)):
        return nepalidate.from_date(value)

    return None


# --------------------------------------------------
# Date filters
# --------------------------------------------------

@register.filter(is_safe=True)
def nepali_date(value, format_str="%Y-%m-%d"):
    """
    Format a date/datetime as Nepali (BS) date.
    """
    nd = _to_nepali_date(value)
    if not nd:
        return ""

    return nd.strftime(format_str)


@register.filter(is_safe=True)
def nepali_date_ne(value, format_str="%Y-%m-%d"):
    """
    Format a date/datetime as Nepali (BS) date in Devanagari.
    """
    nd = _to_nepali_date(value)
    if not nd:
        return ""

    return nd.strftime_ne(format_str)


# --------------------------------------------------
# Number filter
# --------------------------------------------------

@register.filter(is_safe=True)
def nepali_number(value):
    """
    Convert a number to Nepali (Devanagari) digits.
    """
    if value in (None, ""):
        return ""

    try:
        return nepalinumber(value).str_ne()
    except Exception:
        return value


# --------------------------------------------------
# Humanize filter
# --------------------------------------------------

@register.filter(is_safe=True)
def nepali_humanize(value, threshold=None, format_str=None):
    """
    Human-readable Nepali time difference.
    """
    if value is None:
        return ""

    kwargs = {}
    if threshold is not None:
        kwargs["threshold"] = threshold
    if format_str is not None:
        kwargs["format"] = format_str

    try:
        return nepalihumanize(value, **kwargs)
    except Exception:
        return value
