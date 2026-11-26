import csv
import os
from comptes.models import Utilisateur
from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.models import Q
from django.contrib.auth.hashers import make_password
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

            # Lecture et insertion via l'ORM
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

                with open(chemin_complet, mode='r', encoding='utf-8-sig') as fichier:
                    # DictReader associe automatiquement chaque en-tête à sa valeur sous forme de dictionnaire
                    lecteur = csv.DictReader(fichier, delimiter=delimiteur)

                    if not lecteur.fieldnames:
                        self.stdout.write(
                            self.style.WARNING(
                                f'Le fichier {nom_fichier} est vide.'
                            )
                        )
                        continue

                    instances = []
                    doublons = 0
                    for ligne in lecteur:
                        # Ignorer les lignes totalement vides
                        if not any(ligne.values()):
                            continue

                        # Nettoyage des clés (strip)
                        donnees_propres = {
                            cle.strip(): val
                            for cle, val in ligne.items()
                            if cle is not None
                        }

                        for cle, val in donnees_propres.items():
                            if cle.endswith('_id') and val == '':
                             donnees_propres[cle] = None

                        # Renomme 'objet_id' en 'lieu_id' pour correspondre aux modèles Signalement et Lieu
                        if 'objet_id' in donnees_propres:
                            donnees_propres['lieu_id'] = donnees_propres.pop('objet_id') or None

                        # Remplace les alias de classe Utilisateur par les noms de champs d'origine de AbstractUser pour l'import
                        if modele.__name__ == "Utilisateur":
                            for alias, champ in getattr(modele, "ALIAS_CHAMPS", {}).items():
                                if alias in donnees_propres:
                                    donnees_propres[champ] = donnees_propres.pop(alias)

                        # # Compare uniquement les colonnes présentes dans le CSV
                        # if modele.objects.filter(**donnees_propres).exists():
                        #     doublons += 1
                        #     continue                    # block de détection des doublons désactivé car tables vidées à l'execution du script.

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


        # Changements des mots de passe vides par le mot de passe de demo.
        mdp_demo = 'demo1234'
        mdp_hache = make_password(mdp_demo)
        Utilisateur.objects.filter(Q(password="") | Q(password__isnull=True)).update( password=mdp_hache )

        self.stdout.write("Les mots de passe vides ont été remplacés par le mot de passe de demo.")