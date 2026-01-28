from django.urls import path
from . import views

app_name = "demo"

urlpatterns = [
    path("", views.person_list, name="person-list"),
    path("add/", views.person_create, name="person-create"),
]
