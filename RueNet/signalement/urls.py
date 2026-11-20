from django.urls import path
from . import views

app_name = "signalement"

urlpatterns = [
    path("catalogue/", views.CatalogueVue.as_view(), name="liste"),
    path("catalogue/<int:pk>/", views.DetailLieuVue.as_view(), name="detail"),
    # À venir : catalogue/<id>/demande/, mes-demandes/, gestion/
]