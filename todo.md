# Features TODO

## Localization & Formatting

- [x] **Nepali Currency Formatter**: Template tag for formatting money using the Nepali numbering system (Lakhs, Crores).
- [x] **Numbers to Words**: Convert digits like `1234` into Nepali text (`एक हजार दुई सय चौंतीस`).
- [x] **Unicode Helpers**: Built-in filters for converting common text/numbers into Nepali Unicode equivalent.

## Integration

- [x] **Framework-agnostic API**: Drop DRF / django-filter dependency; expose `django_nepkit.api` helpers usable from any view layer.

## Address & Location

- [x] **Address Normalization**: Implement a way to verify or suggest standardized Nepali addresses.

## Validation & Robustness (audit, v0.2.2)

- [x] Fix settings TOCTOU (`NepkitSettings` re-reads `settings.NEPKIT` on every access).
- [x] Fix XSS in `_render_options`.
- [x] `format_nepali_currency` end-to-end `Decimal`, raise on non-finite.
- [x] `number_to_nepali_words` handles negatives; raises on non-numeric.
- [x] `BaseNepaliBSField.to_python` / `get_prep_value` raise on bad input.
- [x] `_parse_language_params` `strict` mode + canonical-value whitelist.
- [x] `_get_primary_param` only falls back when there's a single non-internal param.
- [x] Narrow `except Exception: pass` in `admin.py` to `(FieldDoesNotExist, AttributeError)`.
- [x] Log `NoReverseMatch` in widgets (with hint to include `django_nepkit.urls`).
- [x] `strict` flag on every `django_nepkit.api.serialize_*` / `deserialize_*` / `to_decimal`.
- [x] `_looks_numeric` rejects `inf` / `nan` / `1e1000`.
- [x] Demo API: validate `?order=`, `?year=`, `?month=`, `?amount_range=`, `?date_range=`; return 400 on bad input.
- [x] `address-chaining.js`: scope MutationObserver; suppress init-time `change` events; log fetch errors.
- [x] `nepali-time-init.js`: support Nepali-digit input; ship default CSS for `.nepkit-time-invalid`.
- [x] Rank location matches in `_find_location_in_tokens` (exact > substring).
- [x] Catch `nepali.exceptions.FormatNotMatchException` in the parsers.
- [x] `NepaliTimeField.from_db_value` (validate on read).
- [x] `NepkitSettings.__setattr__` blocks accidental writes (read-only).

## Still open / nice-to-haves

_Nothing left — the perf and escaping improvements below are merged._

- [x] Cache parsed `BaseNepaliBSField` values per row in admin list views (perf).
- [x] Replace the `format_html_join` helper in `_render_options` with a `<template>`-based renderer for better escaping control.
