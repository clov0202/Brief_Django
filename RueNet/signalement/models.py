from django.conf import settings
from django.db import models
from django.utils import timezone


class Categorie(models.Model):
    nom = models.CharField(max_length=100)

    class Meta:
        ordering = ["nom"]
        verbose_name = "catégorie"
        verbose_name_plural = "catégories"

    def __str__(self):
        return self.nom


class Lieu(models.Model):
    nom = models.CharField(max_length=200)
    categorie = models.ForeignKey(Categorie, on_delete=models.PROTECT, related_name="lieux")
    quartier = models.CharField(max_length=100)
    adresse = models.CharField(max_length=255)
    latitude = models.FloatField()
    longitude = models.FloatField()

    class Meta:
        ordering = ["nom"]
        verbose_name = "lieu"
        verbose_name_plural = "lieux"

    def __str__(self):
        return self.nom


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
    lieu = models.ForeignKey(Lieu, on_delete=models.PROTECT, related_name="signalements")
    etat = models.CharField(max_length=20, choices=ETATS, default=NOUVEAU)
    description = models.TextField()
    motif_rejet = models.TextField(blank=True)
    regroupe_avec = models.ForeignKey("self", null=True, blank=True, on_delete=models.SET_NULL, related_name="rattaches")
    # Pas d'auto_now : on garde les dates du CSV
    date_creation = models.DateTimeField(default=timezone.now)
    date_modification = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["-date_creation"]
        verbose_name = "signalement"
        verbose_name_plural = "signalements"

    def __str__(self):
        return f"Signalement n°{self.pk} - {self.lieu} ({self.get_etat_display()})"