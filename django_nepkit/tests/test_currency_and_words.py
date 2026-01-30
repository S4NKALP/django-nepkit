from django_nepkit.utils import (
    format_nepali_currency,
    number_to_nepali_words,
    english_to_nepali_unicode,
)
from django_nepkit.models import NepaliCurrencyField


def test_format_nepali_currency():
    assert format_nepali_currency(1234567) == "Rs. 12,34,567.00"
    assert format_nepali_currency(112000, currency_symbol="") == "1,12,000.00"
    assert format_nepali_currency(1234567, currency_symbol="") == "12,34,567.00"
    assert format_nepali_currency(100.5) == "Rs. 100.50"
    assert format_nepali_currency(None) == ""


def test_number_to_nepali_words():
    assert number_to_nepali_words(0) == "शून्य"
    assert number_to_nepali_words(1) == "एक"
    assert number_to_nepali_words(10) == "दश"
    assert number_to_nepali_words(25) == "पच्चीस"
    assert number_to_nepali_words(100) == "एक सय"
    assert number_to_nepali_words(123) == "एक सय तेईस"
    assert number_to_nepali_words(1000) == "एक हजार"
    assert number_to_nepali_words(1234) == "एक हजार दुई सय चौंतीस"
    assert number_to_nepali_words(100000) == "एक लाख"
    assert number_to_nepali_words(1234567) == "बाह्र लाख चौंतीस हजार पाँच सय सतसट्ठी"
    # Note: 12,34,567 -> 12 Lakhs 34 Thousand 5 Hundred 67


def test_english_to_nepali_unicode():
    assert english_to_nepali_unicode("123") == "१२३"
    assert english_to_nepali_unicode("Price: 100") == "Price: १००"
    assert english_to_nepali_unicode(None) == ""


def test_nepali_currency_field():
    field = NepaliCurrencyField(max_digits=10, decimal_places=2)
    assert field.max_digits == 10
    assert field.decimal_places == 2

    default_field = NepaliCurrencyField()
    assert default_field.max_digits == 19
    assert default_field.decimal_places == 2
