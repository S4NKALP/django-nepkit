# Test Suite for django-nepkit

## Overview

Comprehensive pytest test suite covering all major components of the
django-nepkit library. The library is **framework-agnostic** — there is
no longer any DRF or django-filter dependency.

## Running Tests

```bash
# Run all tests
DJANGO_SETTINGS_MODULE=django_nepkit.tests.settings uv run pytest django_nepkit/tests/ -v

# Run specific test file
DJANGO_SETTINGS_MODULE=django_nepkit.tests.settings uv run pytest django_nepkit/tests/test_models.py -v

# Run with coverage
DJANGO_SETTINGS_MODULE=django_nepkit.tests.settings uv run pytest django_nepkit/tests/ --cov=django_nepkit
```

## Test Coverage

### ✅ Models (`test_models.py`)
- `NepaliDateField`, `NepaliDateTimeField`, `NepaliTimeField`: storage, retrieval, language settings
- `NepaliPhoneNumberField`: valid / invalid phone numbers
- Location fields: province, district, municipality choices and language support

### ✅ Forms (`test_forms.py`)
- `NepaliDateFormField`: input validation, multiple formats, required/optional handling

### ✅ Validators (`test_validators.py`)
- `validate_nepali_phone_number`: mobile and landline validation patterns

### ✅ Utilities (`test_utils.py`)
- `try_parse_nepali_date` / `try_parse_nepali_datetime`
- `try_parse_nepali_time` / `format_nepali_time`

### ✅ API helpers (`test_api.py`)
- `serialize_nepali_date` / `deserialize_nepali_date`
- `serialize_nepali_datetime` / `deserialize_nepali_datetime`
- `serialize_nepali_time` / `deserialize_nepali_time`
- `serialize_nepali_currency` / `deserialize_nepali_currency`
- `to_decimal`
- `build_localized_payload`

### ✅ Admin (`test_admin_currency.py`, `test_admin_media.py`)
- Currency formatting helpers
- Address-chaining media wiring

### ✅ Address chaining JS (`test_address_chaining_js.py`)
- Static-analysis checks for the JavaScript init / change handlers

### ✅ Widgets (`test_widgets.py`)
- `NepaliDatePickerWidget`, `NepaliTimeWidget`, location select widgets

## Dependencies

- `pytest`
- `pytest-django` (via `DJANGO_SETTINGS_MODULE`)
- `Django`
- `nepali`
