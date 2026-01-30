# 🇳🇵 django-nepkit

<div align="center">

[![PyPI version](https://badge.fury.io/py/django-nepkit.svg)](https://badge.fury.io/py/django-nepkit)
[![Python Versions](https://img.shields.io/pypi/pyversions/django-nepkit.svg)](https://pypi.org/project/django-nepkit/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

</div>


**The essential toolkit for Django developers building for Nepal.**

`django-nepkit` handles the specific localization needs of Nepali web applications with elegance and ease. From correct Bikram Sambat (BS) date handling to smart address management and phone validation, we've got you covered.

---

## ✨ Key Features

- **📅 Bikram Sambat (BS) Support**: Full support for Nepali dates and datetimes in models and forms.
- **📱 Smart Validation**: Built-in validators for Nepali phone numbers.
- **🗺️ Administrative Locations**: Chained selects for Provinces, Districts, and Municipalities.
- **🇳🇵 Bilingual Support**: Seamlessly switch between English and Nepali (Devanagari) output for locations and dates.
- **🔌 Zero-Config Admin**: `NepaliModelAdmin` automatically integrates the Nepali datepicker and formats list displays.
- **🚀 API Ready**: Optional DRF serializers with Devanagari support.

---

## 🛠 Installation

Install via pip:

```bash
pip install django-nepkit
```

### Add to `INSTALLED_APPS`

In your `settings.py`:

```python
INSTALLED_APPS = [
    # ...
    "django.contrib.staticfiles",
    "django_nepkit",
]
```

---

## 🚀 Quick Start

### 1. Model Fields

Define your models with Nepali-specific requirements effortlessly.

```python
from django.db import models
from django_nepkit import (
    NepaliDateField,
    NepaliDateTimeField,
    NepaliPhoneNumberField
)

class Citizen(models.Model):
    name = models.CharField(max_length=100)

    # Stores dates as YYYY-MM-DD strings (BS)
    dob = NepaliDateField()

    # Use ne=True for Devanagari digits/names in forms/admin
    appointment = NepaliDateTimeField(ne=True)

    # Validates correct Nepali phone patterns
    phone = NepaliPhoneNumberField()
```

### 2. Admin Integration

`NepaliModelAdmin` provides a zero-config experience. It:
- Automatically attaches the **Nepali Datepicker**.
- Formats `NepaliDateField` and `NepaliDateTimeField` in `list_display`.
- Registers `NepaliDateFilter` for easy year-based filtering.

```python
from django.contrib import admin
from django_nepkit import NepaliModelAdmin
from .models import Citizen

@admin.register(Citizen)
class CitizenAdmin(NepaliModelAdmin):
    list_display = ("name", "dob", "phone")
```

> [!TIP]
> If you already have a custom base Admin class, use **`NepaliAdminMixin`** to get all formatting and filter benefits.

---

## 📝 Forms & Widgets

Need to build a custom form? `django-nepkit` provides specialized fields and widgets.

```python
from django import forms
from django_nepkit.forms import NepaliDateFormField, NepaliPhoneNumberFormField
from django_nepkit.widgets import NepaliDatePickerWidget

class RegistrationForm(forms.Form):
    # Field with built-in validation
    birth_date = NepaliDateFormField()

    # Or apply the widget to a standard field
    event_date = forms.CharField(
        widget=NepaliDatePickerWidget(ne=True) # Devanagari support
    )

    phone = NepaliPhoneNumberFormField()
```

---

## 🗺️ Address Management (Chained Selects)

Model Nepal's administrative structure with automatic filtering: Province → District → Municipality.

### Step 1: Define Fields

```python
from django_nepkit import ProvinceField, DistrictField, MunicipalityField

class Address(models.Model):
    # For English names
    province = ProvinceField()
    district = DistrictField()
    municipality = MunicipalityField()

    # For Devanagari (बगती, काठमाडौँ, etc.)
    # province = ProvinceField(ne=True)
```

### Step 2: Include URLs (Crucial)

For the chained selects to fetch data dynamically, you **must** include the package URLs in your project's `urls.py`:

```python
# urls.py
from django.urls import include, path

urlpatterns = [
    # ...
    path("nepkit/", include("django_nepkit.urls")),
]
```

---

## 🔌 API Support (Django REST Framework)

Install the optional dependency for serializer fields:
```bash
pip install "django-nepkit[drf]"
```

Use them in your serializers with optional Devanagari (`ne=True`) output:

```python
from rest_framework import serializers
from django_nepkit.serializers import NepaliDateSerializerField

class CitizenSerializer(serializers.ModelSerializer):
    # Output: "२०८१-१०-१७" if ne=True
    dob = NepaliDateSerializerField(format="%Y-%m-%d", ne=True)

    class Meta:
        model = Citizen
        fields = "__all__"
```

---

## 🛠️ Utility Functions

Need to format a date in your logic or views?

```python
from django_nepkit import format_nepali_date

# Result: "Magh 17, 2081" (or "माघ १७, २०८१" if ne=True)
formatted = format_nepali_date(my_date, format_string="%B %d, %Y", ne=False)
```

---

## 🤝 Contributing

We love contributions!

1.  Clone the repo: `git clone https://github.com/S4NKALP/django-nepkit`
2.  Install dependencies: `uv sync`
3.  Run the tests: `uv run pytest`
4.  Run the example project: `cd example && python manage.py runserver`

---

## 📄 License

MIT License. Made with ❤️ for the Nepali Django community.
