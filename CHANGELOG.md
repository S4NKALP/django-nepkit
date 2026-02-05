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
