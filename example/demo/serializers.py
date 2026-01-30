from rest_framework import serializers
from django_nepkit.serializers import NepaliDateSerializerField
from .models import Person, Citizen, AuditedPerson


class PersonSerializer(serializers.ModelSerializer):
    birth_date = NepaliDateSerializerField()

    class Meta:
        model = Person
        fields = "__all__"


class CitizenSerializer(serializers.ModelSerializer):
    class Meta:
        model = Citizen
        fields = "__all__"


class AuditedPersonSerializer(serializers.ModelSerializer):
    birth_date = NepaliDateSerializerField()

    class Meta:
        model = AuditedPerson
        fields = "__all__"
