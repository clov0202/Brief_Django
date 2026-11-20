from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import Utilisateur


class FormulaireInscription(UserCreationForm):
    email = forms.EmailField(required=True, label="Adresse e-mail")

    class Meta(UserCreationForm.Meta):
        model = Utilisateur
        fields = ("username", "first_name", "last_name", "email", "quartier")
        labels = {
            "username": "Identifiant",
            "first_name": "Prénom",
            "last_name": "Nom",
        }