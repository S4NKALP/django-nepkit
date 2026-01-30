from django import template
from django.utils import timezone
from nepali.datetime import nepalidate, nepalihumanize
from nepali.number import nepalinumber
import datetime

register = template.Library()


def _coerce_ad_date_to_bs(value):
    """Convert an English (AD) date to a Nepali date."""
    if isinstance(value, datetime.datetime):
        if timezone.is_aware(value):
            value = timezone.localtime(value)
        return nepalidate.from_date(value)
    if isinstance(value, datetime.date):
        return nepalidate.from_date(value)
    return value


@register.filter
def nepali_date(value, format_str="%Y-%m-%d"):
    """Format a date as a Nepali string (e.g. 2080-01-01)."""
    if value is None:
        return ""

    value = _coerce_ad_date_to_bs(value)

    if hasattr(value, "strftime"):
        return value.strftime(format_str)
    return value


@register.filter
def nepali_date_ne(value, format_str="%Y-%m-%d"):
    """Format a date using Nepali digits (e.g. २०८०-०१-०१)."""
    if value is None:
        return ""

    value = _coerce_ad_date_to_bs(value)

    if hasattr(value, "strftime_ne"):
        return value.strftime_ne(format_str)
    return value


@register.filter
def nepali_number(value):
    """Convert any number to Nepali digits (123 -> १२३)."""
    if value is None:
        return ""
    return nepalinumber(value).str_ne()


@register.filter
def nepali_humanize(value, threshold=None, format_str=None):
    """Show 'time ago' in Nepali (like '५ मिनेट अगाडि')."""
    if value is None:
        return ""

    # Threshold and format_str are optional
    kwargs = {}
    if threshold:
        kwargs["threshold"] = threshold
    if format_str:
        kwargs["format"] = format_str

    return nepalihumanize(value, **kwargs)
