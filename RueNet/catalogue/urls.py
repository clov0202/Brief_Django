from django.urls import path
from . import views

app_name = "catalogue"

urlpatterns = [
    path("", views.CatalogueView.as_view(), name="liste"),
    path("<int:pk>/", views.LieuDetailView.as_view(), name="detail"),
]