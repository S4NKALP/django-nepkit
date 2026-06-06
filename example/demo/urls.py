from django.urls import path

from . import views

app_name = "demo"

urlpatterns = [
    path("", views.person_list, name="person-list"),
    path("add/", views.person_create, name="person-create"),
    path("transactions/add/", views.transaction_create, name="transaction-create"),
    path("normalize/", views.address_normalize_demo, name="address-normalize"),
    # JSON API (plain Django — no DRF, no django-filter)
    path("api/persons.json", views.person_api, name="person-api"),
    path("api/citizens.json", views.citizen_api, name="citizen-api"),
    path("api/audited.json", views.audited_api, name="audited-api"),
    path("api/transactions.json", views.transaction_api, name="transaction-api"),
]
