from django.shortcuts import render, redirect
from .models import Person
from django import forms


class PersonForm(forms.ModelForm):
    class Meta:
        model = Person
        fields = [
            "name",
            "birth_date",
            "phone_number",
            "province",
            "district",
            "municipality",
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
