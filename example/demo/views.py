from django import forms
from django.shortcuts import render, redirect
from rest_framework import viewsets, filters as drf_filters
from django_filters import rest_framework as django_filters
from django_nepkit.filters import NepaliDateYearFilter, NepaliDateMonthFilter
from .models import Person, Citizen, AuditedPerson
from .serializers import PersonSerializer, CitizenSerializer, AuditedPersonSerializer


class PersonForm(forms.ModelForm):
    class Meta:
        model = Person
        fields = [
            "name",
            "birth_date",
            "birth_date_ne",
            "phone_number",
            "province",
            "province_ne",
            "district",
            "district_ne",
            "municipality",
            "municipality_ne",
        ]


def person_list(request):
    persons = Person.objects.all()
    return render(request, "demo/person_list.html", {"persons": persons})


def person_create(request):
    if request.method == "POST":
        form = PersonForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("demo:person-list")
    else:
        form = PersonForm()
    return render(request, "demo/person_form.html", {"form": form})


# --- API Support (DRF) ---


class PersonViewSet(viewsets.ModelViewSet):
    queryset = Person.objects.all()
    serializer_class = PersonSerializer

    # Sort and Search work automatically with BS date strings
    filter_backends = [
        django_filters.DjangoFilterBackend,
        drf_filters.SearchFilter,
        drf_filters.OrderingFilter,
    ]

    ordering_fields = ["birth_date", "created_at"]
    search_fields = ["name", "birth_date", "phone_number"]

    # Simple exact date filter
    filterset_fields = {
        "birth_date": ["exact"],
    }

    class PersonFilter(django_filters.FilterSet):
        year = NepaliDateYearFilter(field_name="birth_date")
        month = NepaliDateMonthFilter(field_name="birth_date")

        class Meta:
            model = Person
            fields = ["province", "district"]

    filterset_class = PersonFilter


class CitizenViewSet(viewsets.ModelViewSet):
    queryset = Citizen.objects.all()
    serializer_class = CitizenSerializer
    filter_backends = [drf_filters.OrderingFilter]
    ordering_fields = ["province", "district"]


class AuditedPersonViewSet(viewsets.ModelViewSet):
    queryset = AuditedPerson.objects.all()
    serializer_class = AuditedPersonSerializer
    filter_backends = [drf_filters.SearchFilter, drf_filters.OrderingFilter]
    search_fields = ["name", "birth_date"]
    ordering_fields = ["created_at"]
