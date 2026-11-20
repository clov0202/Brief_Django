from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
class Utilisateur(AbstractUser):
    class Role(models.TextChoices):
        UTILISATEUR = "utilisateur", "Habitant"
        GESTIONNAIRE = "gestionnaire", "Agent de la ville"

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.UTILISATEUR,
        verbose_name="Rôle",
    )
    quartier = models.CharField(
        max_length=100,
        blank=True,
        default="",
        verbose_name="Quartier",
    )

    class Meta:
        verbose_name = "Utilisateur"
        verbose_name_plural = "Utilisateurs"

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"