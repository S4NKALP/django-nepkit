import datetime

from django import template
from nepali.datetime import nepalidate, nepalihumanize
from nepali.number import nepalinumber

register = template.Library()


@register.filter
def nepali_date(value, format_str="%Y-%m-%d"):
    """
    Formats a date or datetime object into a Nepali date string.
    """
    if value is None:
        return ""

    if isinstance(value, (datetime.datetime, datetime.date)):
        value = nepalidate.from_date(value)

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

    if isinstance(value, (datetime.datetime, datetime.date)):
        value = nepalidate.from_date(value)

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
