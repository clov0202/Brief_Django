import csv
import os
from comptes.models import Utilisateur
from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import transaction
from signalement.models import Categorie, Lieu, Signalement


class Command(BaseCommand):
    """
        Charge les 4 fichiers CSV de donnees/signalements via l'ORM Django.
    """
    help = "Charge les 4 fichiers CSV de donnees/signalements via l'ORM Django."

    def handle(self, *args, **options):
        # Configuration : associer chaque fichier CSV directement à sa classe Modèle
        # en respectant l'ordre des dépendances (les tables parentes avant les clés étrangères)
        mapping_fichiers_modeles = {
            'utilisateurs.csv': Utilisateur,
            'categories.csv': Categorie,
            'objets.csv': Lieu,
            'actions.csv': Signalement,
        }

        dossier_csv = os.path.join(settings.BASE_DIR, 'donnees', 'signalements')
        delimiteur = ','

        with transaction.atomic():
            # Étape optionnelle : Vider les tables dans l'ordre inverse des dépendances (enfants avant parents)
            # pour éviter les erreurs de contraintes de clés étrangères (IntegrityError)
            for modele in reversed(list(mapping_fichiers_modeles.values())):
                modele.objects.all().delete()

            # Étape 2 : Lecture et insertion via l'ORM
            for nom_fichier, modele in mapping_fichiers_modeles.items():
                chemin_complet = os.path.join(dossier_csv, nom_fichier)

                if not os.path.exists(chemin_complet):
                    self.stdout.write(
                        self.style.WARNING(
                            f'Fichier introuvable ignoré : {chemin_complet}'
                        )
                    )
                    continue

                self.stdout.write(
                    f'Traitement de {nom_fichier} -> modèle {modele.__name__}...'
                )

                with open(chemin_complet, mode='r', encoding='utf-8-sig') as f:
                    # DictReader associe automatiquement chaque en-tête à sa valeur sous forme de dictionnaire
                    lecteur = csv.DictReader(f, delimiter=delimiteur)

                    if not lecteur.fieldnames:
                        self.stdout.write(
                            self.style.WARNING(
                                f'Le fichier {nom_fichier} est vide.'
                            )
                        )
                        continue

                    instances = []
                    for ligne in lecteur:
                        # Ignorer les lignes totalement vides
                        if not any(ligne.values()):
                            continue

                        # Nettoyage des clés (strip) et conversion des chaînes vides en None
                        donnees_propres = {
                            cle.strip(): (val) #if val != '' else None)
                            for cle, val in ligne.items()
                            if cle is not None
                        }

                        # Renomme 'objet_id' en 'lieu_id' pour correspondre aux modèles Signalement et Lieu
                        if 'objet_id' in donnees_propres:
                            donnees_propres['lieu_id'] = donnees_propres.pop('objet_id') or None

                        # Instanciation de l'objet ORM (sans sauvegarde immédiate en base)
                        instances.append(modele(**donnees_propres))

                    # Insertion en masse (équivalent ORM de executemany)
                    if instances:
                        modele.objects.bulk_create(instances)
                        self.stdout.write(
                            self.style.SUCCESS(
                                f'  -> {len(instances)} objets insérés pour {modele.__name__}.'
                            )
                        )
                    else:
                        self.stdout.write(
                            self.style.WARNING(
                                f'  -> Aucune donnée à insérer pour {nom_fichier}.'
                            )
                        )

        self.stdout.write(self.style.SUCCESS('Importation terminée avec succès !'))
