"""
Tests for location utility helpers in utils.py:
  - get_districts_by_province
  - get_municipalities_by_district
  - _normalize_nepali_text
  - _matches_location_name
  - _is_nepali_text
"""


class TestGetDistrictsByProvince:
    """Tests for get_districts_by_province."""

    def test_returns_districts_for_valid_province(self):
        from django_nepkit.utils import get_districts_by_province

        result = get_districts_by_province("Bagmati Province")
        assert isinstance(result, list)
        assert len(result) > 0
        # Each item should have 'id' and 'text'
        assert all("id" in item and "text" in item for item in result)

    def test_includes_known_district(self):
        from django_nepkit.utils import get_districts_by_province

        result = get_districts_by_province("Bagmati Province")
        district_names = [item["text"] for item in result]
        assert "Kathmandu" in district_names

    def test_returns_empty_for_invalid_province(self):
        from django_nepkit.utils import get_districts_by_province

        result = get_districts_by_province("Nonexistent Province")
        assert result == []

    def test_returns_nepali_names_when_ne_true(self):
        from django_nepkit.utils import get_districts_by_province
        import re

        result = get_districts_by_province("Bagmati Province", ne=True)
        assert len(result) > 0
        has_devanagari = any(
            re.search(r"[\u0900-\u097F]", item["text"]) for item in result
        )
        assert has_devanagari

    def test_finds_province_by_nepali_name(self):
        from django_nepkit.utils import get_districts_by_province

        # बागमती प्रदेश is the Nepali name for Bagmati Province
        result = get_districts_by_province("बागमती प्रदेश", ne=True)
        assert len(result) > 0

    def test_koshi_province(self):
        from django_nepkit.utils import get_districts_by_province

        result = get_districts_by_province("Koshi Province")
        assert len(result) > 0
        district_names = [item["text"] for item in result]
        assert "Taplejung" in district_names or any(
            "Taplejung" in n for n in district_names
        )


class TestGetMunicipalitiesByDistrict:
    """Tests for get_municipalities_by_district."""

    def test_returns_municipalities_for_valid_district(self):
        from django_nepkit.utils import get_municipalities_by_district

        result = get_municipalities_by_district("Kathmandu")
        assert isinstance(result, list)
        assert len(result) > 0
        assert all("id" in item and "text" in item for item in result)

    def test_includes_kathmandu_metro(self):
        from django_nepkit.utils import get_municipalities_by_district

        result = get_municipalities_by_district("Kathmandu")
        names = [item["text"] for item in result]
        assert any("Kathmandu" in n for n in names)

    def test_returns_empty_for_invalid_district(self):
        from django_nepkit.utils import get_municipalities_by_district

        result = get_municipalities_by_district("Nonexistent District")
        assert result == []

    def test_returns_nepali_names_when_ne_true(self):
        from django_nepkit.utils import get_municipalities_by_district
        import re

        result = get_municipalities_by_district("Kathmandu", ne=True)
        assert len(result) > 0
        has_devanagari = any(
            re.search(r"[\u0900-\u097F]", item["text"]) for item in result
        )
        assert has_devanagari


class TestNormalizeNepaliText:
    """Tests for _normalize_nepali_text internal helper."""

    def test_returns_none_for_falsy(self):
        from django_nepkit.utils import _normalize_nepali_text

        assert _normalize_nepali_text(None) is None
        assert _normalize_nepali_text("") == ""

    def test_replaces_chandrabindu_with_anusvara(self):
        from django_nepkit.utils import _normalize_nepali_text

        # ँ (chandrabindu) → ं (anusvara)
        result = _normalize_nepali_text("काठमाडौँ")
        assert "ँ" not in result
        assert "ं" in result

    def test_plain_text_unchanged(self):
        from django_nepkit.utils import _normalize_nepali_text

        text = "Kathmandu"
        assert _normalize_nepali_text(text) == text


class TestMatchesLocationName:
    """Tests for _matches_location_name internal helper."""

    def test_exact_nepali_match(self):
        from django_nepkit.utils import _matches_location_name

        assert _matches_location_name("Kathmandu", "काठमाडौं", "काठमाडौं", "काठमाडौं")

    def test_exact_english_match_case_insensitive(self):
        from django_nepkit.utils import _matches_location_name

        assert _matches_location_name("Kathmandu", "काठमाडौं", "kathmandu", "kathmandu")

    def test_partial_english_match(self):
        from django_nepkit.utils import _matches_location_name

        # "Pokhara" is contained in "Pokhara Metropolitan City"
        assert _matches_location_name(
            "Pokhara Metropolitan City", "पोखरा महानगरपालिका", "Pokhara", "Pokhara"
        )

    def test_short_token_no_partial_english_match(self):
        from django_nepkit.utils import _matches_location_name

        # Token shorter than 4 chars should not trigger partial English match
        assert not _matches_location_name("Kathmandu", "काठमाडौं", "Kat", "Kat")

    def test_no_match(self):
        from django_nepkit.utils import _matches_location_name

        assert not _matches_location_name("Lalitpur", "ललितपुर", "Pokhara", "Pokhara")


class TestIsNepaliText:
    """Tests for _is_nepali_text internal helper."""

    def test_devanagari_detected(self):
        from django_nepkit.utils import _is_nepali_text

        assert _is_nepali_text(["काठमाडौं"])

    def test_english_not_detected(self):
        from django_nepkit.utils import _is_nepali_text

        assert not _is_nepali_text(["Kathmandu", "Bagmati"])

    def test_mixed_tokens(self):
        from django_nepkit.utils import _is_nepali_text

        # If any token has Devanagari, returns True
        assert _is_nepali_text(["Kathmandu", "काठमाडौं"])

    def test_empty_list(self):
        from django_nepkit.utils import _is_nepali_text

        assert not _is_nepali_text([])
