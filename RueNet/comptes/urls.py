from django.urls import path
from .views import VueConnexion, VueDeconnexion, VueInscription

app_name = "comptes"

urlpatterns = [
    path("inscription/", VueInscription.as_view(), name="inscription"),
    path("connexion/", VueConnexion.as_view(), name="connexion"),
    path("deconnexion/", VueDeconnexion.as_view(), name="deconnexion"),
]