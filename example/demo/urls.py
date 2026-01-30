from . import views
from rest_framework.routers import DefaultRouter
from django.urls import path

app_name = "demo"

router = DefaultRouter()
router.register("api/persons", views.PersonViewSet, basename="person-api")
router.register("api/citizens", views.CitizenViewSet, basename="citizen-api")
router.register("api/audited", views.AuditedPersonViewSet, basename="audited-api")

urlpatterns = [
    path("", views.person_list, name="person-list"),
    path("add/", views.person_create, name="person-create"),
] + router.urls
