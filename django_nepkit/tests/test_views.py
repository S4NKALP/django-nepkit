"""
Tests for django-nepkit views (views.py).
Covers district_list_view, municipality_list_view, and private helpers.
"""

import pytest
from django.test import RequestFactory


@pytest.fixture
def rf():
    return RequestFactory()


class TestRenderOptions:
    """Tests for _render_options internal helper."""

    def test_renders_placeholder_option(self):
        from django_nepkit.views import _render_options

        response = _render_options([], "Select District")
        html = response.content.decode()
        assert 'value=""' in html
        assert "Select District" in html

    def test_renders_data_options(self):
        from django_nepkit.views import _render_options

        data = [{"id": "Kathmandu", "text": "Kathmandu"}]
        response = _render_options(data, "Select")
        html = response.content.decode()
        assert 'value="Kathmandu"' in html
        assert ">Kathmandu<" in html

    def test_renders_multiple_options(self):
        from django_nepkit.views import _render_options

        data = [
            {"id": "Kathmandu", "text": "Kathmandu"},
            {"id": "Lalitpur", "text": "Lalitpur"},
        ]
        response = _render_options(data, "Select")
        html = response.content.decode()
        assert "Kathmandu" in html
        assert "Lalitpur" in html


class TestGetPrimaryParam:
    """Tests for _get_primary_param internal helper."""

    def test_returns_named_param(self, rf):
        from django_nepkit.views import _get_primary_param

        request = rf.get("/", {"province": "Bagmati Province"})
        value = _get_primary_param(request, "province")
        assert value == "Bagmati Province"

    def test_falls_back_to_first_non_internal_param(self, rf):
        from django_nepkit.views import _get_primary_param

        # No "province" key, but has "field" key (not an internal param)
        request = rf.get("/", {"field": "Bagmati Province"})
        value = _get_primary_param(request, "province")
        assert value == "Bagmati Province"

    def test_internal_params_excluded_from_fallback(self, rf):
        from django_nepkit.views import _get_primary_param

        # Only internal params (ne, en, html) present — should return None
        request = rf.get("/", {"ne": "true", "en": "true", "html": "true"})
        value = _get_primary_param(request, "province")
        assert value is None

    def test_returns_none_when_no_params(self, rf):
        from django_nepkit.views import _get_primary_param

        request = rf.get("/")
        value = _get_primary_param(request, "province")
        assert value is None


class TestParseLanguageParams:
    """Tests for _parse_language_params internal helper."""

    def test_defaults_to_english(self, rf):
        from django_nepkit.views import _parse_language_params

        request = rf.get("/")
        ne, en = _parse_language_params(request)
        assert ne is False
        assert en is True

    def test_ne_true_from_query(self, rf):
        from django_nepkit.views import _parse_language_params

        request = rf.get("/", {"ne": "true"})
        ne, en = _parse_language_params(request)
        assert ne is True
        assert en is False

    def test_en_true_from_query(self, rf):
        from django_nepkit.views import _parse_language_params

        request = rf.get("/", {"en": "true"})
        ne, en = _parse_language_params(request)
        assert en is True

    def test_ne_false_from_query(self, rf):
        from django_nepkit.views import _parse_language_params

        request = rf.get("/", {"ne": "false"})
        ne, en = _parse_language_params(request)
        assert ne is False
        assert en is True


class TestShouldReturnHtml:
    """Tests for _should_return_html internal helper."""

    def test_html_param_true(self, rf):
        from django_nepkit.views import _should_return_html

        request = rf.get("/", {"html": "true"})
        assert _should_return_html(request) is True

    def test_html_param_false(self, rf):
        from django_nepkit.views import _should_return_html

        request = rf.get("/", {"html": "false"})
        assert _should_return_html(request) is False

    def test_htmx_request_header(self, rf):
        from django_nepkit.views import _should_return_html

        request = rf.get("/", HTTP_HX_REQUEST="true")
        assert _should_return_html(request) is True

    def test_no_html_indicator(self, rf):
        from django_nepkit.views import _should_return_html

        request = rf.get("/")
        assert _should_return_html(request) is False


class TestDistrictListView:
    """Tests for district_list_view."""

    def test_returns_json_for_valid_province(self, rf):
        from django_nepkit.views import district_list_view

        request = rf.get("/", {"province": "Bagmati Province"})
        response = district_list_view(request)

        assert response.status_code == 200
        import json

        data = json.loads(response.content)
        assert isinstance(data, list)
        assert len(data) > 0
        # Each item has id and text
        assert "id" in data[0]
        assert "text" in data[0]

    def test_returns_empty_json_when_no_province(self, rf):
        from django_nepkit.views import district_list_view

        request = rf.get("/")
        response = district_list_view(request)

        assert response.status_code == 200
        import json

        data = json.loads(response.content)
        assert data == []

    def test_returns_html_when_html_true(self, rf):
        from django_nepkit.views import district_list_view

        request = rf.get("/", {"province": "Bagmati Province", "html": "true"})
        response = district_list_view(request)

        assert response.status_code == 200
        assert "text/html" in response["Content-Type"]
        assert b"<option" in response.content

    def test_returns_nepali_names_when_ne_true(self, rf):
        from django_nepkit.views import district_list_view
        import json

        request = rf.get("/", {"province": "Bagmati Province", "ne": "true"})
        response = district_list_view(request)

        data = json.loads(response.content)
        assert len(data) > 0
        # Nepali names should contain Devanagari characters
        import re

        has_devanagari = any(
            re.search(r"[\u0900-\u097F]", item["text"]) for item in data
        )
        assert has_devanagari

    def test_returns_html_with_nepali_placeholder(self, rf):
        from django_nepkit.views import district_list_view

        request = rf.get(
            "/", {"province": "Bagmati Province", "html": "true", "ne": "true"}
        )
        response = district_list_view(request)

        # Placeholder should contain Devanagari text (जिल्ला छान्नुहोस्)
        decoded = response.content.decode("utf-8")
        assert "जिल्ला" in decoded


class TestMunicipalityListView:
    """Tests for municipality_list_view."""

    def test_returns_json_for_valid_district(self, rf):
        from django_nepkit.views import municipality_list_view
        import json

        request = rf.get("/", {"district": "Kathmandu"})
        response = municipality_list_view(request)

        assert response.status_code == 200
        data = json.loads(response.content)
        assert isinstance(data, list)
        assert len(data) > 0

    def test_returns_empty_json_when_no_district(self, rf):
        from django_nepkit.views import municipality_list_view
        import json

        request = rf.get("/")
        response = municipality_list_view(request)

        assert response.status_code == 200
        data = json.loads(response.content)
        assert data == []

    def test_returns_html_when_html_true(self, rf):
        from django_nepkit.views import municipality_list_view

        request = rf.get("/", {"district": "Kathmandu", "html": "true"})
        response = municipality_list_view(request)

        assert response.status_code == 200
        assert "text/html" in response["Content-Type"]
        assert b"<option" in response.content

    def test_returns_nepali_names_when_ne_true(self, rf):
        from django_nepkit.views import municipality_list_view
        import json
        import re

        request = rf.get("/", {"district": "Kathmandu", "ne": "true"})
        response = municipality_list_view(request)

        data = json.loads(response.content)
        assert len(data) > 0
        has_devanagari = any(
            re.search(r"[\u0900-\u097F]", item["text"]) for item in data
        )
        assert has_devanagari

    def test_htmx_request_returns_html(self, rf):
        from django_nepkit.views import municipality_list_view

        request = rf.get("/", {"district": "Kathmandu"}, HTTP_HX_REQUEST="true")
        response = municipality_list_view(request)

        assert "text/html" in response["Content-Type"]
        assert b"<option" in response.content
