## V.0.2.2 — 2026-06-06

### 💥 Breaking changes

- **Drop DRF and django-filter dependencies.** The package no longer ships
  `django_nepkit.serializers`, `django_nepkit.ninja`, or
  `django_nepkit.filters`. All serialization is now exposed as
  framework-agnostic helpers in `django_nepkit.api` (see
  `serialize_nepali_date`, `serialize_nepali_time`,
  `serialize_nepali_currency`, `build_localized_payload`, etc.). If you
  were using the DRF `NepaliDateSerializerField` / `NepaliCurrencySerializerField`
  or the `NepaliDateYearFilter` / `NepaliDateMonthFilter` / range filters,
  write a thin adapter against `django_nepkit.api` (or just use plain
  Django views — see the updated `example/demo`).
- `BaseNepaliBSField.to_python` and `get_prep_value` now raise
  `ValidationError` on bad input instead of silently returning
  `str(value)`. Code that was relying on the silent passthrough (e.g.
  persisting `"not-a-date"` strings to the DB) will now fail loudly
  at the form / save boundary, which is the correct behaviour.
- `format_nepali_currency` and `number_to_nepali_words` now raise
  `ValueError` on un-parseable input instead of returning `str(value)`
  / crashing with `IndexError` on negative numbers. Negative numbers
  are now rendered as `"ऋणात्मक …"`.

### ✨ Features

- New `NepaliTimeField` (real `TimeField` with Devanagari digit output,
  `auto_now` / `auto_now_add` support, `BS_TIME_FORMAT` setting).
- New `NepaliTimeWidget` and JS init for client-side time validation.
- New `strict` flag on every `django_nepkit.api.serialize_*` /
  `deserialize_*` and on `to_decimal` for callers that want to opt
  into hard validation errors instead of best-effort passthrough.
- Admin address-chaining fixed: districts / municipalities are now
  filtered on init when a parent value is preselected (e.g. when
  editing an existing record).
- `MunicipalitySelectWidget` now also supports `htmx=True` like its
  district sibling.
- `_render_options` escapes its HTML output via `format_html` /
  `format_html_join` (XSS fix).
- `BaseLocationField.choices` is now a live property that re-evaluates
  on every access from the current `nepkit_settings`.  An explicit
  `ne=True` / `ne=False` constructor arg pins the language for the
  field's lifetime (only the implicit default re-reads the setting).
  `refresh_choices()` is kept as a no-op for backwards compatibility.
- `normalize_address` is now backed by an `lru_cache(1024)`-decorated
  inner function so the heavy `_find_location_in_tokens` work runs at
  most once per unique address string. The public function still
  returns a fresh dict per call so callers can mutate safely.
- Demo JSON views (`person_api`, `audited_api`, `transaction_api`)
  accept `?strict=1` to thread `strict=True` through the
  `serialize_nepali_date` / `serialize_nepali_datetime` calls — handy
  for smoke-testing the strict path against live data.
- `NEPKIT_ONES` constant `NEGATIVE_PREFIX` is now part of the public
  API for callers that want to render negative numbers themselves.

### 🐛 Bug fixes

- **TOCTOU on settings** — `NepkitSettings` now re-reads
  `settings.NEPKIT` on every attribute access; `override_settings` and
  `setting_changed` are honoured.  The `BS_*_FORMAT` constants are
  re-exported via a module-level `__getattr__` so direct
  `from django_nepkit.utils import BS_DATE_FORMAT` re-reads too.
- **XSS in `_render_options`** — `id` / `text` / placeholder values
  are now HTML-escaped. Fixes a latent reflected/stored XSS sink
  reachable from `?html=true` and the `HX-Request: true` paths.
- **`format_nepali_currency` precision loss** — switched from `float`
  to `Decimal` end-to-end.  `Decimal("123456789012345.67")` now
  formats as `"Rs. 1,23,45,67,89,01,234.57"` instead of truncated
  float garbage.
- **`format_nepali_currency` non-finite rejection** — `inf` / `nan`
  / `"1e1000"` now raise `ValueError` instead of producing `"inf"`.
- **`number_to_nepali_words` negative crash** — negative numbers
  now render with the `"ऋणात्मक"` prefix instead of raising
  `IndexError`.
- **`NepaliDatePickerWidget.format_value` EN-mode leak** — passing a
  `nepalidate` in English mode no longer leaks its Python repr
  (`"nepalidate(2081, 1, 15)"`) into the rendered HTML; unknown
  value types render as `""`.
- **`NepaliTimeWidget.format_value` EN-mode leak** — same fix for
  time values.
- **`_parse_language_params` silent coercion** — `?ne=banana` now
  falls back to the project default instead of silently returning
  `False`; with `strict=True` it raises `ValueError`.
- **`_get_primary_param` ambiguous fallback** — when the URL has
  multiple non-internal params, the named parameter takes priority
  and the "first non-internal" fallback is skipped.
- **`address-chaining.js` `change`-event storm** — the init path no
  longer fires synthetic `change` events, so user-defined change
  handlers don't run during page load.
- **`address-chaining.js` MutationObserver scope** — the observer
  now only triggers init on additions of `form` /
  `.nepkit-province-select` / `.nepkit-district-select` instead of
  every DOM mutation.
- **`address-chaining.js` silent fetch failure** — server errors are
  now logged via `console.error` instead of swallowed silently.
- **`nepali-time-init.js` invalid-state styling** — the
  `.nepkit-time-invalid` class now ships with default CSS (red
  border + soft red background).
- **`nepali-time-init.js` Nepali-digit input** — `०१:००` is now
  normalised to ASCII before regex matching.
- **Address normalisation fuzzy match** — `_find_location_in_tokens`
  now ranks candidates (exact > substring) so `"Pokhara"` no longer
  loses to `"Pokhara Metropolitan City"` (or vice versa) for the
  same token.
- **Exception narrowing** — `_try_parse_nepali` /
  `try_parse_nepali_time` now catch `nepali.exceptions.FormatNotMatchException`
  explicitly instead of relying on it happening to be a `ValueError`.
- **Admin `except Exception: pass`** — replaced with narrow
  `except (FieldDoesNotExist, AttributeError)` so genuine bugs
  surface instead of being swallowed.
- **`NoReverseMatch` swallowed in widgets** — the missing-URL case
  is now logged at WARNING with a hint pointing at the URLconf.
- **Demo API input validation** — `?order=…`, `?year=…`, `?month=…`,
  `?amount_range=…` and `?date_range=…` all return 400 on bad input
  (out-of-range month, non-numeric range, unknown order field, …)
  instead of 500-ing the request.
- **`Accept-Language` fallback** — the demo's `_ne_flag` now
  honours `Accept-Language: ne` in addition to `?ne=true`.

### ♻️ Refactoring

- Extracted framework-agnostic serialization logic into
  `django_nepkit.api` (the only public serialization surface).
- `NepaliDatePickerWidget._configure_attrs` now chains to `super()`.
- `__init__.py` is now safe to import with no extra packages
  installed, and re-exports `nepkit_settings` for live access.
- `NepkitSettings` re-reads `settings.NEPKIT` on every access
  (so `override_settings` finally works) and refuses attribute
  assignment (it's read-only — change `settings.NEPKIT` instead).
- `BaseNepaliBSField.format_str` is now a `@property` so it
  re-reads the current `BS_DATE_FORMAT` / `BS_DATETIME_FORMAT`
  setting at call time.
- `BaseNepaliBSField.pre_save` shared helper factored out; the
  date / datetime subclasses no longer duplicate the TZ
  normalization logic.
- `_render_options` escapes its HTML output (fixes latent XSS
  sink) and now uses `format_html_join`.
- `format_nepali_date` / `format_nepali_datetime` exposed in
  `django_nepkit.utils` (previously only `format_nepali_time` was
  available there).

## V.0.2.1 — 2027-02-05

### ✨ Features

- upgrade nepali package to 1.2.0 and remove hardcoded Koshi Province mapping

### ♻️ Refactoring

- remove code redundancy and improve maintainability
- extract duplicate view logic into reusable helper functions in views.py
- create constants.py for centralized hardcoded values (Nepali words, placeholders)
- simplify number_to_nepali_words function from 157 to 42 lines
- refactor normalize_address with extracted helper functions
- add lang_utils.py for consistent language parameter handling
- reduce JavaScript duplication in address-chaining.js with helper functions
- move circular import from module level to method scope in models.py
- remove ~160+ lines of redundant code while preserving all logic

## V.0.2.0 — 2026-01-31

### ✨ Features

- implement address normalization
- REST API enhancements
- add Nepali currency field, number to words, and unicode helpers
- add English datepicker support and comprehensive documentation improvements
- implement HTMX support, DRF filters, and professionalized documentation
- implement zero-config address chaining and revamp documentation
- revamp localization support with Devanagari (BS) integration

### 📚 Documentation

- added showcase
- updated readme

### 🧹 Other Changes

- fixed workflow
- added todo
- added workflow
- added comprehensive pytest test suite with 67% coverage
- global project refinement, DRY consolidation, and documentation overhaul

## V.0.1.0 — 2026-01-29

- Initial release
