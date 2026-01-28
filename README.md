# django-nepkit

`django-nepkit` is a lightweight Django utility package for Nepali projects. It provides model fields, validators, and admin helpers for:

- **Bikram Sambat (BS)** date, time, and datetime
- **Nepali phone number** validation
- **Chained address selects** (province → district → municipality)

It also includes Django admin enhancements:

- `NepaliModelAdmin` automatically wires the Nepali datepicker
- `NepaliDateFilter` for filtering BS dates by year

Optional Django REST Framework (DRF) serializer fields are available (install with `django-nepkit[drf]`).

## Notes

- The package depends on [`py-nepali`](https://github.com/opensource-nepal/py-nepali).
- The date picker UI is implemented from [`sajanm/nepali-date-picker`](https://github.com/sajanm/nepali-date-picker).

---

## Table of Contents

- [Installation](#installation)
- [Requirements](#requirements)
- [Setup](#setup)
- [Quick Start](#quick-start)
- [Model Fields](#model-fields)
- [Address Fields (Chained Selects)](#address-fields-chained-selects)
- [Django Admin](#django-admin)
- [Django REST Framework](#django-rest-framework)
- [Public API](#public-api)
- [Contributing](#contributing)
- [License](#license)

---

## Installation

```bash
pip install django-nepkit
```

### Optional: DRF Serializer Fields

```bash
pip install "django-nepkit[drf]"
```

---

## Requirements

- Python `>=3.11`
- Django `>=4.2`
- `nepali>=1.1.3`

---

## Setup

### Add to `INSTALLED_APPS`

```python
INSTALLED_APPS = [
    # ...
    "django.contrib.staticfiles",
    "django_nepkit",
]
```

---

## Quick Start

```python
# models.py
from django.db import models
from django_nepkit import NepaliDateField, NepaliDateTimeField, NepaliPhoneNumberField

class Person(models.Model):
    name = models.CharField(max_length=100)
    birth_date = NepaliDateField()
    created_at = NepaliDateTimeField(auto_now_add=True)
    phone_number = NepaliPhoneNumberField()
```

```python
# admin.py
from django.contrib import admin
from django_nepkit import NepaliModelAdmin
from .models import Person

@admin.register(Person)
class PersonAdmin(NepaliModelAdmin):
    list_display = ("name", "birth_date", "created_at", "phone_number")
```

`NepaliModelAdmin` automatically loads the Nepali datepicker assets and applies the widget—no custom forms required.

---

## Model Fields

### `NepaliDateField` (BS date)

Stores a BS date in the DB as a string (`YYYY-MM-DD`). In Python, it returns/accepts `nepali.datetime.nepalidate`.

```python
from django_nepkit import NepaliDateField

class Event(models.Model):
    event_date = NepaliDateField()
```

**Notes:**

- Stored as a string, not SQL DATE
- Accepts BS strings like `"2081-10-15"`, `nepalidate`, and AD `datetime.date` (converted to BS)

---

### `NepaliDateTimeField` (BS datetime)

Stores a BS datetime string (`YYYY-MM-DD HH:MM:SS`) in the DB and uses `nepalidatetime` in Python.

```python
from django_nepkit import NepaliDateTimeField

class Log(models.Model):
    created_at = NepaliDateTimeField(auto_now_add=True)
    updated_at = NepaliDateTimeField(auto_now=True)
```

---

### `NepaliTimeField`

A normal Django `TimeField` for consistency.

```python
from django_nepkit import NepaliTimeField

class Shift(models.Model):
    start_time = NepaliTimeField()
```

---

### `NepaliPhoneNumberField`

A `CharField` with Nepali phone number validation.

```python
from django_nepkit import NepaliPhoneNumberField

class Contact(models.Model):
    phone_number = NepaliPhoneNumberField()
```

---

## Address Fields (Chained Selects)

Chained fields: province → district → municipality.

```python
from django.db import models
from django_nepkit import ProvinceField, DistrictField, MunicipalityField

class Address(models.Model):
    province = ProvinceField()
    district = DistrictField()
    municipality = MunicipalityField()
```

### URLs required for chaining

```python
# urls.py
from django.urls import include, path

urlpatterns = [
    # ...
    path("nepkit/", include("django_nepkit.urls")),
]
```

---

## Django Admin

### `NepaliModelAdmin`

- Auto-wires datepicker for BS fields
- Provides `format_nepali_date(...)` and `format_nepali_datetime(...)`
- Includes `NepaliDateFilter`

```python
from django.contrib import admin
from django_nepkit import NepaliModelAdmin

@admin.register(MyModel)
class MyModelAdmin(NepaliModelAdmin):
    pass
```

### `NepaliDateFilter`

Filter `NepaliDateField` by BS year:

```python
from django_nepkit import NepaliDateFilter, NepaliModelAdmin

@admin.register(MyModel)
class MyModelAdmin(NepaliModelAdmin):
    list_filter = (("my_nepali_date_field", NepaliDateFilter),)
```

**Datepicker assets used:**

- JS: `https://nepalidatepicker.sajanmaharjan.com.np/v5/nepali.datepicker/js/nepali.datepicker.v5.0.6.min.js`
- CSS: `https://nepalidatepicker.sajanmaharjan.com.np/v5/nepali.datepicker/css/nepali.datepicker.v5.0.6.min.css`

---

## Django REST Framework

Install the extra:

```bash
pip install "django-nepkit[drf]"
```

### `NepaliDateSerializerField`

```python
from rest_framework import serializers
from django_nepkit.serializers import NepaliDateSerializerField

class PersonSerializer(serializers.Serializer):
    birth_date = NepaliDateSerializerField(format="%Y/%m/%d")
```

### `NepaliDateTimeSerializerField`

```python
from rest_framework import serializers
from django_nepkit.serializers import NepaliDateTimeSerializerField

class LogSerializer(serializers.Serializer):
    created_at = NepaliDateTimeSerializerField()
```

---

## Public API

```python
from django_nepkit import (
    NepaliDateField,
    NepaliTimeField,
    NepaliDateTimeField,
    NepaliPhoneNumberField,
    ProvinceField,
    DistrictField,
    MunicipalityField,
    NepaliDateFilter,
    NepaliModelAdmin,
    NepaliAdminMixin,
)
```

DRF fields live in `django_nepkit.serializers`.

---

## Contributing

Contributions are welcome. If you find a bug or want an improvement, please open an issue or submit a pull request.

### Local setup

Clone the repo and install dependencies (this project uses `uv`):

```bash
git clone <your-fork-url>
cd prod-django-nepkit
uv sync
```

### Run the example project

The repository contains an example Django project under `example/`.

```bash
cd example
uv run manage.py migrate
uv run manage.py createsuperuser
uv run manage.py runserver
```

### Code quality (recommended before every commit)

Install and run pre-commit:

```bash
uv run pre-commit install
uv run pre-commit run --all-files
```

You can also run Ruff directly:

```bash
uv run ruff format .
uv run ruff check .
```

### Pull request guidelines

- Keep PRs focused and small when possible.
- Update `README.md` if behavior or public API changes.
- If you add a new feature, include a minimal example and tests if applicable.

---

## License

MIT. See [`LICENSE`](LICENSE).
