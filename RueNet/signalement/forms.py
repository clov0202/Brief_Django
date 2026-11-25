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
class FormulaireGestionSignalement(forms.ModelForm):
    class Meta:
        model = Signalement
        fields = ["etat", "motif_rejet"]
        widgets = {
            "etat": forms.Select(attrs={"class": "border rounded p-2 w-full"}),
            "motif_rejet": forms.Textarea(attrs={"class": "border rounded p-2 w-full", "rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtre les états proposés selon les règles TRANSITIONS du modèle
        if self.instance and self.instance.pk:
            etat_actuel = self.instance.etat
            etats_autorises = [etat_actuel] + self.instance.TRANSITIONS.get(etat_actuel, [])
            self.fields["etat"].choices = [
                (code, libelle) for code, libelle in Signalement.ETATS if code in etats_autorises
            ]

    def clean(self):
        cleaned_data = super().clean()
        etat = cleaned_data.get("etat")
        motif = cleaned_data.get("motif_rejet", "").strip()

        # Exige un motif si le gestionnaire passe l'état à "rejete"
        if etat == Signalement.REJETE and not motif:
            self.add_error("motif_rejet", "Veuillez indiquer un motif de rejet.")
        return cleaned_data
