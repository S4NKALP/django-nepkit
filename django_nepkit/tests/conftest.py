"""
Pytest configuration and shared fixtures for django-nepkit tests.
"""

import pytest
import django
from django.conf import settings

# Django is configured via DJANGO_SETTINGS_MODULE in pytest.ini
if not settings.configured:
    django.setup()


@pytest.fixture
def nepali_date_sample():
    """Sample nepalidate object for testing."""
    from nepali.datetime import nepalidate

    return nepalidate(2081, 1, 15)  # 2081-01-15


@pytest.fixture
def nepali_datetime_sample():
    """Sample nepalidatetime object for testing."""
    from nepali.datetime import nepalidatetime

    return nepalidatetime(2081, 1, 15, 14, 30, 0)  # 2081-01-15 14:30:00
