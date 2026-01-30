from unittest.mock import MagicMock, patch
from django_nepkit.serializers import NepaliCurrencySerializerField, NepaliLocalizedSerializerMixin
from django_nepkit.models import NepaliCurrencyField, NepaliDateField
from django_nepkit.filters import NepaliCurrencyRangeFilter, NepaliDateRangeFilter

def test_nepali_currency_serializer_field():
    field = NepaliCurrencySerializerField()
    assert field.to_representation(123456) == "Rs. 1,23,456.00"
    assert field.to_representation(None) is None

def test_nepali_localized_serializer_mixin_logic():
    from nepali.datetime import nepalidate
    
    # Mock model and fields
    class MockModel:
        class _meta:
            @staticmethod
            def get_field(name):
                if name == 'amount':
                    return NepaliCurrencyField()
                if name == 'birth_date':
                    return NepaliDateField()
                raise Exception("Field not found")

    instance = MagicMock()
    instance.amount = 100000
    instance.birth_date = nepalidate(2080, 1, 1)
    
    # We test the mixin by creating a class that inherits from it
    class TestSerializer(NepaliLocalizedSerializerMixin):
        def __init__(self, context):
            self.context = context
            self.Meta = MagicMock()
            self.Meta.model = MockModel
        
        def to_representation(self, instance):
            # We don't want to call super().to_representation(instance)
            # because we don't have a real base class with that method.
            # Instead, we just want to test our local logic.
            # So we'll patch the call to super() or just mock the return value.
            pass

    # Actually, the mixin DOES call super().to_representation(instance).
    # To test it, we can use a class that provides that method.
    class Base:
        def to_representation(self, instance):
            return {'amount': 100000, 'birth_date': '2080-01-01'}

    class RealTestSerializer(NepaliLocalizedSerializerMixin, Base):
        def __init__(self, context):
            self.context = context
            self.Meta = MagicMock()
            self.Meta.model = MockModel

    serializer = RealTestSerializer(context={'ne': True})
    data = serializer.to_representation(instance)
    
    assert 'amount_ne' in data
    assert data['amount_ne'] == "१,००,०००.००"
    assert 'birth_date_ne' in data
    assert data['birth_date_ne'] == "२०८०-०१-०१"

def test_currency_range_filter():
    from django.db.models import QuerySet
    
    qs = MagicMock(spec=QuerySet)
    f = NepaliCurrencyRangeFilter(field_name='amount')
    
    # Test range
    f.filter(qs, "1000,5000")
    qs.filter.assert_any_call(amount__range=("1000", "5000"))
    
    # Test min, (gte)
    f.filter(qs, "1000,")
    qs.filter.assert_any_call(amount__gte="1000")
    
    # Test ,max (lte)
    f.filter(qs, ",5000")
    qs.filter.assert_any_call(amount__lte="5000")

    # Test exact (single value)
    f.filter(qs, "2000")
    qs.filter.assert_any_call(amount="2000")

def test_date_range_filter():
    from django.db.models import QuerySet
    
    qs = MagicMock(spec=QuerySet)
    f = NepaliDateRangeFilter(field_name='birth_date')
    
    # Test range
    f.filter(qs, "2080-01-01,2080-01-30")
    qs.filter.assert_any_call(birth_date__range=("2080-01-01", "2080-01-30"))
    
    # Test exact
    f.filter(qs, "2080-01-01")
    qs.filter.assert_any_call(birth_date="2080-01-01")
