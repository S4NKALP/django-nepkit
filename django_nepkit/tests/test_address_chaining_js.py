"""
Static-analysis tests for the address-chaining JavaScript. These don't run
the JS but make sure the file contains the behaviours we depend on.
"""

import re
from pathlib import Path

JS_PATH = (
    Path(__file__).resolve().parent.parent
    / "static"
    / "django_nepkit"
    / "js"
    / "address-chaining.js"
)


def _read_js():
    assert JS_PATH.exists(), f"address-chaining.js missing at {JS_PATH}"
    return JS_PATH.read_text(encoding="utf-8")


class TestAddressChainingScript:
    def test_defines_placeholders(self):
        js = _read_js()
        assert "प्रदेश छान्नुहोस्" in js
        assert "Select Province" in js
        assert "जिल्ला छान्नुहोस्" in js
        assert "Select District" in js
        assert "नगरपालिका छान्नुहोस्" in js
        assert "Select Municipality" in js

    def test_has_preserve_selection_logic(self):
        js = _read_js()
        # The init function must filter child selects when the parent has
        # a value (the admin bug fix).
        assert re.search(r"if\s*\(\s*provinceSelect\.value\s*\)\s*\{", js), (
            "provinceSelect.value is not checked on init"
        )
        assert re.search(
            r"if\s*\(\s*districtSelect\s*&&\s*districtSelect\.value\s*\)", js
        ), "districtSelect.value is not checked on init"

    def test_has_preserve_selection_parameter(self):
        js = _read_js()
        assert "preserveSelection" in js

    def test_watches_mutations(self):
        js = _read_js()
        assert "MutationObserver" in js

    def test_handles_district_only_forms(self):
        js = _read_js()
        # District-only flow (no province) is handled separately.
        assert "districtOnlySelects" in js or "nepkit-district-select" in js

    def test_orders_data_before_chaining(self):
        """When the JS is referenced, the data file must come first."""
        from django_nepkit.widgets import ChainedSelectWidget

        media = ChainedSelectWidget().media  # resolve the property
        media_js = list(media._js)
        data_idx = media_js.index("django_nepkit/js/nepal-data.js")
        chain_idx = media_js.index("django_nepkit/js/address-chaining.js")
        assert data_idx < chain_idx

    def test_init_does_not_dispatch_change(self):
        """The init path must pass ``false`` for dispatchChange so we don't
        fire synthetic change events on page load."""
        js = _read_js()
        # Look for the initForm function and check it calls updateOptions /
        # updateDependentSelect with a `false` literal (the dispatchChange
        # opt-out).  We use a permissive pattern because the call sites
        # include nested function calls whose ``)`` would break a strict
        # ``[^)]*``-anchored regex.
        assert re.search(r"updateOptions\([^;]+,\s*false\s*,\s*false\s*\)\s*;", js), (
            "initForm should call updateOptions(..., false, false)"
        )

    def test_logs_fetch_errors(self):
        """fetchData must log an error to the console on failure."""
        js = _read_js()
        assert "console.error" in js, "fetchData should log fetch errors"

    def test_observer_filters_to_nepkit_forms(self):
        """The MutationObserver should not run init on every DOM mutation —
        only on additions of forms / nepkit selects."""
        js = _read_js()
        assert "addedNodes" in js
        assert "nepkit-province-select" in js
        assert "nepkit-district-select" in js
