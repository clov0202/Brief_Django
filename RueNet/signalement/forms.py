from django import forms

from .models import Signalement


class SignalementForm(forms.ModelForm):
    class Meta:
        model = Signalement
        fields = ["description"]
        labels = {
            "description": "Description du problème",
        }
        widgets = {
            "description": forms.Textarea(
                attrs={
                    "rows": 4,
                    "placeholder": "Décrivez l'anomalie constatée sur ce lieu...",
                    "class": "w-full border rounded px-3 py-2",
                }
            )
        }