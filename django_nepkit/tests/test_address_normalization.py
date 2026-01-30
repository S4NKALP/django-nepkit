from django_nepkit.utils import normalize_address


def test_normalize_address_empty():
    assert normalize_address("") == {
        "province": None,
        "district": None,
        "municipality": None,
    }
    assert normalize_address(None) == {
        "province": None,
        "district": None,
        "municipality": None,
    }


def test_normalize_address_english_basic():
    # Kathmandu is a district and a municipality
    result = normalize_address("Kathmandu")
    assert result["district"] == "Kathmandu"
    assert result["municipality"] == "Kathmandu Metropolitan City"
    assert result["province"] == "Bagmati Province"


def test_normalize_address_english_full():
    result = normalize_address("Pokhara, Kaski, Gandaki")
    assert result["province"] == "Gandaki Province"
    assert result["district"] == "Kaski"
    assert result["municipality"] == "Pokhara Metropolitan City"


def test_normalize_address_nepali_basic():
    result = normalize_address("काठमाडौं")
    assert result["district"] == "काठमाडौं"
    assert result["municipality"] == "काठमाडौँ महानगरपालिका"
    assert result["province"] == "बागमती प्रदेश"


def test_normalize_address_nepali_full():
    result = normalize_address("पोखरा, कास्की, गण्डकी")
    assert result["province"] == "गण्डकी प्रदेश"
    assert result["district"] == "कास्की"
    assert result["municipality"] == "पोखरा महानगरपालिका"


def test_normalize_address_koshi_mapping():
    # Test "Koshi" mapping to "Province 1" internally and then back to "Koshi Province"
    result = normalize_address("Biratnagar, Koshi")
    assert result["province"] == "Koshi Province"
    assert result["municipality"] == "Biratnagar Metropolitan City"

    result_ne = normalize_address("विराटनगर, कोशी")
    assert result_ne["province"] == "कोशी प्रदेश"
    assert result_ne["municipality"] == "विराटनगर महानगरपालिका"


def test_normalize_address_with_extra_info():
    result = normalize_address("House No 123, Ward 4, Bharatpur, Chitwan")
    assert result["district"] == "Chitawan"
    assert result["municipality"] == "Bharatpur Metropolitan City"
    assert result["province"] == "Bagmati Province"


def test_normalize_address_partial_tokens():
    # "Lalitpur" matches both district and municipality
    result = normalize_address("Lalitpur")
    assert result["district"] == "Lalitpur"
    assert result["municipality"] == "Lalitpur Metropolitan City"
