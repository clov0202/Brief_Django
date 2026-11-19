from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class User(AbstractUser):
    ROLES = [("utilisateur", "Utilisateur"), ("gestionnaire", "Gestionnaire")]
    role = models.CharField(max_length=20, choices=ROLES, default="utilisateur")
    quartier = models.CharField(max_length=100, blank=True)


class Signalement(models.Model):
    NOUVEAU = "nouveau"
    PRIS_EN_COMPTE = "pris_en_compte"
    EN_COURS = "en_cours"
    RESOLU = "resolu"
    REJETE = "rejete"

    ETATS = [
        (NOUVEAU, "Nouveau"),
        (PRIS_EN_COMPTE, "Pris en compte"),
        (EN_COURS, "En cours"),
        (RESOLU, "Résolu"),
        (REJETE, "Rejeté"),
    ]

    # Transitions autorisées pour le gestionnaire (fiche du thème)
    TRANSITIONS = {
        NOUVEAU: [PRIS_EN_COMPTE, REJETE],
        PRIS_EN_COMPTE: [EN_COURS, REJETE],
        EN_COURS: [RESOLU],
        RESOLU: [],
        REJETE: [],
    }

    utilisateur = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="signalements")
    lieu = models.ForeignKey("catalogue.Lieu", on_delete=models.PROTECT, related_name="signalements")
    etat = models.CharField(max_length=20, choices=ETATS, default=NOUVEAU)
    description = models.TextField()
    motif_rejet = models.TextField(blank=True)
    regroupe_avec = models.ForeignKey("self", null=True, blank=True, on_delete=models.SET_NULL, related_name="rattaches")
    # Pas d'auto_now : on garde les dates du CSV
    date_creation = models.DateTimeField(default=timezone.now)
    date_modification = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["-date_creation"]

    def __str__(self):
        return f"Signalement #{self.pk} - {self.lieu} ({self.get_etat_display()})"