from django import template
from nepali.datetime import nepalidate, nepalihumanize
from nepali.number import nepalinumber
import datetime

register = template.Library()


def _coerce_ad_date_to_bs(value):
    """
    Internal helper: if value is AD date/datetime, convert to `nepalidate`.
    Does NOT attempt to parse strings (keeps template behavior minimal).
    """
    if isinstance(value, (datetime.datetime, datetime.date)):
        return nepalidate.from_date(value)
    return value


@register.filter
def nepali_date(value, format_str="%Y-%m-%d"):
    """
    Formats a date or datetime object into a Nepali date string.
    """
    if value is None:
        return ""

    value = _coerce_ad_date_to_bs(value)

    if hasattr(value, "strftime"):
        return value.strftime(format_str)
    return value


@register.filter
def nepali_date_ne(value, format_str="%Y-%m-%d"):
    """
    Formats a date or datetime object into a Nepali date string (Devanagari).
    """
    if value is None:
        return ""

    value = _coerce_ad_date_to_bs(value)

    if hasattr(value, "strftime_ne"):
        return value.strftime_ne(format_str)
    return value


@register.filter
def nepali_number(value):
    """
    Converts a number to Devanagari.
    """
    if value is None:
        return ""
    return nepalinumber(value).str_ne()


@register.filter
def nepali_humanize(value, threshold=None, format_str=None):
    """
    Returns a human-readable "time ago" string in Nepali.
    """
    if value is None:
        return ""

    # Threshold and format_str are optional
    kwargs = {}
    if threshold:
        kwargs["threshold"] = threshold
    if format_str:
        kwargs["format"] = format_str

    return nepalihumanize(value, **kwargs)
