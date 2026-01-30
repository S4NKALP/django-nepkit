# 🇳🇵 django-nepkit

<div align="center">

[![PyPI version](https://badge.fury.io/py/django-nepkit.svg)](https://badge.fury.io/py/django-nepkit)
[![Python Versions](https://img.shields.io/pypi/pyversions/django-nepkit.svg)](https://pypi.org/project/django-nepkit/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**The essential toolkit for Django developers building for Nepal.**

`django-nepkit` handles the specific localization needs of Nepali web applications with elegance. From correct Bikram Sambat (BS) date handling to smart address management and phone validation.

[Features](#-key-features) • [Installation](#-installation) • [Configuration](#-global-configuration) • [Usage](#-quick-start) • [Storage & TZ](#-date-storage--timezone-behavior) • [API Support](#-api-support-drf--filters)

</div>

---

## ✨ Key Features

- **📅 Bikram Sambat (BS) Support**: Specialized `NepaliDateField` and `NepaliDateTimeField` for your models.
- **🗺️ Administrative Locations**: Out-of-the-box support for Provinces, Districts, and Municipalities with chained selects.
- **📱 Smart Validation**: Built-in validation for Nepali phone numbers.
- **🇳🇵 Bilingual by Design**: Seamlessly switch between English and Devanagari (Nepali) output.
- **🔌 Zero-Config Admin**: Automatic integration with the Nepali datepicker and formatted list displays.
- **🚀 API Ready**: First-class support for Django REST Framework and filtering.
- **⚡ HTMX Friendly**: Effortless server-side chained selects using HTMX.

---

## 🛠 Installation

Install the core package via pip:

```bash
pip install django-nepkit
```

### 1. Add to `INSTALLED_APPS`

In your `settings.py`:

```python
INSTALLED_APPS = [
    # ...
    "django.contrib.staticfiles",
    "django_nepkit",
]
```

### 2. (Optional) DRF & Filters Support

If you plan to use it with Django REST Framework:

```bash
pip install "django-nepkit[drf]"
```

---

## ⚙️ Global Configuration

Customize the library's behavior globally in your `settings.py`:

```python
NEPKIT = {
    "DEFAULT_LANGUAGE": "en",           # "en" or "ne" (default: "en")
    "DATE_INPUT_FORMATS": [             # Supported parsing formats
        "%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y"
    ],
    "ADMIN_DATEPICKER": True,            # Toggle Nepali datepicker in admin
    "TIME_FORMAT": 12,                   # 12 or 24 hour display in admin
}
```

---

## 🚀 Quick Start

### 1. Model Fields

`django-nepkit` fields act like standard Django fields but handle BS dates and Nepali validation.

```python
from django.db import models
from django_nepkit import (
    NepaliDateField,
    NepaliDateTimeField,
    NepaliPhoneNumberField
)

class Citizen(models.Model):
    name = models.CharField(max_length=100)
    dob = NepaliDateField() # Stores as BS "YYYY-MM-DD"
    phone = NepaliPhoneNumberField() # Validates Nepali patterns
```

### 2. Zero-Config Admin

Simply inherit from `NepaliModelAdmin` to get automatic datepickers and formatted list displays.

```python
from django.contrib import admin
from django_nepkit import NepaliModelAdmin
from .models import Citizen

@admin.register(Citizen)
class CitizenAdmin(NepaliModelAdmin):
    list_display = ("name", "dob", "phone")
```

> [!TIP]
> If you have a custom base Admin class, use **`NepaliAdminMixin`** to inject Nepali formatting capabilities.

---

## 🗺️ Address Management

Model Nepal's administrative structure with automatic filtering: **Province → District → Municipality**.

### Standard Usage (Internal JS)

```python
from django_nepkit import ProvinceField, DistrictField, MunicipalityField

class Address(models.Model):
    province = ProvinceField()
    district = DistrictField()
    municipality = MunicipalityField()
```

### HTMX Usage (Server-side)

For a more modern approach without writing JavaScript, enable HTMX chaining:

```python
class AddressForm(forms.Form):
    province = ProvinceField(htmx=True)
    district = DistrictField(htmx=True)
    municipality = MunicipalityField()
```

> [!IMPORTANT]
> Ensure the [HTMX](https://htmx.org/) library is loaded in your templates when using `htmx=True`.

---

## 🔌 API Support (DRF & Filters)

Full integration with Django REST Framework and Django-Filter.

### Serializers
Fields automatically respect your `DEFAULT_LANGUAGE` but can be localized individually.

```python
from django_nepkit.serializers import NepaliDateSerializerField

class CitizenSerializer(serializers.ModelSerializer):
    dob = NepaliDateSerializerField() # Outputs BS formatted date
```

### Filters
Filter your API results by BS Year or Date range effortlessly.

```python
from django_nepkit.filters import NepaliDateYearFilter

class CitizenFilter(filters.FilterSet):
    # Filter by BS Year (e.g., /api/citizens/?birth_year=2080)
    birth_year = NepaliDateYearFilter(field_name="dob")
```

---

## 🕒 Date Storage & Timezone Behavior

| Aspect | Behavior |
| :--- | :--- |
| **Database Storage** | Stored as `VARCHAR(10)` or `VARCHAR(19)` in BS format (`YYYY-MM-DD`). |
| **Why strings?** | Avoids redundant AD/BS conversion overhead and ensures data integrity. |
| **Object Type** | Retrieved as `nepalidate` or `nepalidatetime` objects (via `nepali` lib). |
| **Timezone** | Respects `USE_TZ`. Converts UTC `now()` to your local time before BS conversion. |

---

## 🛠️ Utility Functions

```python
from django_nepkit import format_nepali_date

# Example: "Magh 17, 2081" or "माघ १७, २०८१"
formatted = format_nepali_date(my_date, format_string="%B %d, %Y")
```

---

## 🤝 Contributing

We welcome contributions to make this toolkit even better!

1.  **Clone**: `git clone https://github.com/S4NKALP/django-nepkit`
2.  **Setup**: `uv sync` (We use [uv](https://github.com/astral-sh/uv) for project management)
3.  **Test**: `uv run pytest`
4.  **Try**: `cd example && python manage.py runserver`

---

## 📄 License

MIT License. Crafted with ❤️ for the Nepali Django community.
