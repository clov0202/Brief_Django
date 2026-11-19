from django.urls import path
from . import views

app_name = "catalogue"

urlpatterns = [
    path("", views.CatalogueVue.as_view(), name="liste"),
    path("<int:pk>/", views.DetailLieuVue.as_view(), name="detail"),
]