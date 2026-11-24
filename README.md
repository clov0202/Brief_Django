# RueNet — Service de signalements citoyens

> Application web Django de gestion : un **service de signalements citoyens** dont le **catalogue** est fait d'**équipements de la ville** (les *lieux*) et dont les **demandes** sont des **signalements**.

Projet de groupe réalisé dans le cadre de la formation *Développeur·se intelligence artificielle* (Simplon.co) — brief « Application de gestion avec Django » (3 personnes, 10 jours).

---

## Sommaire

1. [Présentation](#présentation)
2. [Fonctionnalités](#fonctionnalités)
3. [Stack technique](#stack-technique)
4. [Architecture du projet](#architecture-du-projet)
5. [Modèle de données](#modèle-de-données)
6. [Cycle de vie d'un signalement](#cycle-de-vie-dun-signalement)
7. [Installation](#installation)
8. [Lancer le projet](#lancer-le-projet)
9. [Import des données](#import-des-données)
10. [Organisation du travail (Git)](#organisation-du-travail-git)
11. [Tests](#tests)
12. [Équipe](#équipe)
13. [Pistes d'amélioration](#pistes-damélioration)

---

## Présentation

Le brief s'articule autour de deux notions :

| Notion du brief | Dans RueNet |
|---|---|
| **Catalogue** | Les **lieux** : équipements de la ville, classés par catégorie et par quartier, avec adresse et coordonnées GPS |
| **Demande** | Les **signalements** déposés par les utilisateurs sur un lieu |

Un utilisateur parcourt le catalogue des équipements et signale un problème sur l'un d'eux. Un gestionnaire traite ensuite le signalement en le faisant avancer dans un cycle de vie encadré (prise en compte, traitement, résolution ou rejet motivé).

## Fonctionnalités

**Catalogue** *(disponible)*
- Liste des lieux (équipements de la ville), triés par nom
- Page de détail d'un lieu (catégorie, quartier, adresse, coordonnées GPS) avec lien de retour au catalogue
- **Recherche par mot-clé** (nom, adresse ou quartier du lieu)
- **Filtre par catégorie**, combinable avec la recherche

**Signalements (utilisateur)**
- Inscription (identifiant, prénom, nom, e-mail obligatoire, quartier) avec connexion automatique à la création du compte
- Connexion / déconnexion ; un utilisateur déjà connecté est redirigé vers le catalogue
- Barre de navigation commune : liens Connexion / Inscription pour un visiteur, prénom et bouton Déconnexion (formulaire POST) pour un utilisateur connecté, lien **Gestion** visible uniquement pour le rôle `gestionnaire` *(page à venir)*
- Messages de confirmation affichés en haut de page
- Dépôt d'un signalement depuis la page d'un lieu, avec une description *(à venir)*
- Suivi de l'état de ses signalements via « Mes demandes » *(à venir)*

**Gestion (gestionnaire)** *(à venir)*
- Liste de tous les signalements, du plus récent au plus ancien
- Changement d'état selon les **transitions autorisées** uniquement
- **Rejet motivé** : un signalement rejeté conserve son motif
- **Regroupement de doublons** : un signalement peut être rattaché à un signalement principal
- Administration des catégories, lieux et signalements via l'admin Django

## Stack technique

- **Python** 3.12+ (requis par Django 6)
- **Django** 6.x
- **SQLite** (développement), chemin configurable via `.env`
- **python-dotenv** pour les variables d'environnement
- Interface en **français** (`fr-fr`), fuseau **Europe/Paris**
- **Templates Django** (HTML) avec **Tailwind CSS**, chargé via le CDN (`cdn.tailwindcss.com`) : une connexion internet est nécessaire, et ce mode est prévu pour le développement uniquement
- **Git / GitHub**

## Architecture du projet

Le projet Django s'appelle **RueNet** et contient deux applications :

```
Brief_Django/
├── RueNet/                 # Configuration (settings.py, urls.py, wsgi.py, asgi.py)
├── comptes/                # App « comptes » : utilisateurs et authentification
│   ├── models.py           #   Utilisateur (AbstractUser + role + quartier)
│   ├── forms.py            #   FormulaireInscription
│   ├── views.py            #   VueInscription, VueConnexion, VueDeconnexion
│   ├── urls.py             #   app_name = "comptes"
│   ├── admin.py            #   UtilisateurAdmin
│   ├── migrations/
│   └── templates/comptes/  #   inscription.html, connexion.html
├── signalement/            # App « signalement » : cœur métier
│   ├── models.py           #   Categorie, Lieu, Signalement
│   ├── views.py            #   CatalogueVue, DetailLieuVue (vues basées sur les classes)
│   ├── urls.py             #   app_name = "signalement"
│   ├── admin.py            #   Categorie, Lieu, Signalement enregistrés dans l'admin
│   ├── migrations/         #   0001_initial
│   ├── management/commands/#   charger_donnees.py (import des CSV)
│   └── templates/catalogue/#   liste.html, detail.html
├── templates/              # base.html (gabarit commun : barre de navigation, messages)
├── donnees/
│   └── signalements/       # Fichiers CSV du thème
├── manage.py
├── .env                    # Variables d'environnement (non versionné)
├── requirements.txt
├── .gitignore
└── README.md
```

| App | Responsabilité |
|---|---|
| `comptes` | Modèle `Utilisateur` personnalisé (`AUTH_USER_MODEL`) avec rôle et quartier, inscription, connexion, déconnexion |
| `signalement` | Modèles `Categorie`, `Lieu`, `Signalement`, **catalogue** (liste avec recherche et filtre, détail) et, à venir, dépôt de signalement et **gestion** |

> Vérifie l'arborescence réelle avec l'explorateur de VS Code et corrige ce bloc si besoin.

## Modèle de données

```
Categorie ──< Lieu ──< Signalement >── Utilisateur (comptes)
                           │
                           └── regroupe_avec ──> Signalement (auto-référence)
```

### `Utilisateur` (app `comptes`)

Modèle utilisateur personnalisé, qui hérite de `AbstractUser` (identifiant, mot de passe, prénom, nom, e-mail, etc.) et ajoute :

| Champ | Type | Description |
|---|---|---|
| `role` | `CharField(20)` | `utilisateur` (affiché « Utilisateur », par défaut) ou `gestionnaire` (affiché « Gestionnaire ») |
| `quartier` | `CharField(100)` | Quartier de résidence (facultatif) |

Le rôle distingue les utilisateurs, qui déposent des signalements, des gestionnaires (agents de la ville), qui les traitent dans la partie gestion.

Le modèle expose aussi deux alias de lecture/écriture : `prenom` (→ `first_name`) et `nom` (→ `last_name`).

### `Categorie`

| Champ | Type | Description |
|---|---|---|
| `nom` | `CharField(100)` | Nom de la catégorie (tri alphabétique) |

### `Lieu` (le catalogue)

| Champ | Type | Description |
|---|---|---|
| `nom` | `CharField(200)` | Nom de l'équipement |
| `categorie` | `ForeignKey(Categorie)` | Catégorie (`PROTECT` : impossible de supprimer une catégorie utilisée) |
| `quartier` | `CharField(100)` | Quartier |
| `adresse` | `CharField(255)` | Adresse |
| `latitude` | `FloatField` | Coordonnée GPS |
| `longitude` | `FloatField` | Coordonnée GPS |

### `Signalement` (la demande)

| Champ | Type | Description |
|---|---|---|
| `utilisateur` | `ForeignKey(AUTH_USER_MODEL)` | Auteur (`CASCADE`) |
| `lieu` | `ForeignKey(Lieu)` | Équipement concerné (`PROTECT`) |
| `etat` | `CharField(20)` | État courant (voir ci-dessous), `nouveau` par défaut |
| `description` | `TextField` | Description du problème |
| `motif_rejet` | `TextField` | Renseigné en cas de rejet (vide sinon) |
| `regroupe_avec` | `ForeignKey("self")` | Signalement principal en cas de doublon (`SET_NULL`) |
| `date_creation` | `DateTimeField` | Date de création (conservée depuis le CSV, pas d'`auto_now`) |
| `date_modification` | `DateTimeField` | Date de dernière modification (idem) |

## Cycle de vie d'un signalement

Cinq états, avec des transitions strictement contrôlées (constante `Signalement.TRANSITIONS`) :

```
                ┌──────────────► Rejeté
                │                  ▲
Nouveau ──► Pris en compte ──► En cours ──► Résolu
   │                │
   └────────────────┘ (rejet possible)
```

| État actuel | Transitions autorisées |
|---|---|
| `nouveau` | `pris_en_compte`, `rejete` |
| `pris_en_compte` | `en_cours`, `rejete` |
| `en_cours` | `resolu` |
| `resolu` | — (état final) |
| `rejete` | — (état final) |

Un rejet doit s'accompagner d'un `motif_rejet`.

## Installation

### Prérequis

- Python 3.12 ou plus récent (requis par Django 6)
- Git

### 1. Cloner le dépôt

```powershell
git clone https://github.com/clov0202/Brief_Django.git
cd Brief_Django
```

### 2. Environnement virtuel

**Windows (PowerShell)**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

> Si PowerShell bloque l'activation : `Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned`

**macOS / Linux**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Dépendances

```powershell
pip install -r requirements.txt
```

### 4. Variables d'environnement

Crée un fichier `.env` à la racine du projet (à côté de `manage.py`) :

```env
SECRET_KEY=remplace-par-une-longue-cle-secrete
DEBUG=True
DATABASE_NAME=db.sqlite3
```

| Variable | Rôle | Valeur par défaut |
|---|---|---|
| `SECRET_KEY` | Clé secrète Django | `default_secret_key` (**à ne jamais utiliser en production**) |
| `DEBUG` | Mode debug (`True` ou `False`) | `True` |
| `DATABASE_NAME` | Chemin de la base SQLite | `db.sqlite3` à la racine |

> Le fichier `.env` ne doit **jamais** être committé. Vérifie qu'il figure dans `.gitignore`.

### 5. Migrations

Le projet utilise un modèle utilisateur personnalisé (`AUTH_USER_MODEL = "comptes.Utilisateur"`, déjà configuré dans `settings.py`). Ne change pas cette valeur après la première migration.

```powershell
python manage.py makemigrations
python manage.py migrate
```

### 6. Super-utilisateur

```powershell
python manage.py createsuperuser
```

> Un super-utilisateur est créé avec le rôle `utilisateur` par défaut. Pour qu'il ait accès à la gestion, ouvre-le dans l'admin (`/admin/`) et passe son **rôle** à *Gestionnaire*. Les comptes gestionnaires se créent aussi depuis l'admin, section « Informations RueNet ».

## Lancer le projet

```powershell
python manage.py runserver
```

| Page | URL | Nom de la route | Statut |
|---|---|---|---|
| Accueil | http://127.0.0.1:8000/ | `accueil` | ✅ redirige vers le catalogue |
| Inscription | http://127.0.0.1:8000/comptes/inscription/ | `comptes:inscription` | ✅ disponible |
| Connexion | http://127.0.0.1:8000/comptes/connexion/ | `comptes:connexion` | ✅ disponible |
| Déconnexion | http://127.0.0.1:8000/comptes/deconnexion/ | `comptes:deconnexion` | ✅ disponible |
| Catalogue des lieux | http://127.0.0.1:8000/catalogue/ (paramètres `?mot_cle=...&categorie=<id>`) | `signalement:liste` | ✅ disponible |
| Détail d'un lieu | http://127.0.0.1:8000/catalogue/<id>/ | `signalement:detail` | ✅ disponible |
| Déposer un signalement sur un lieu | `/catalogue/<id>/demande/` | — | 🚧 à venir |
| Mes signalements | `/mes-demandes/` | — | 🚧 à venir |
| Gestion des signalements | `/gestion/` | — | 🚧 à venir |
| Administration | http://127.0.0.1:8000/admin/ | — | ✅ disponible |

> Les URLs de `comptes` sont préfixées par `/comptes/` ; celles de `signalement` sont à la racine du site (`path("", include("signalement.urls"))`). Les routes sont nommées avec les namespaces `comptes` et `signalement`.


## Import des données

Les jeux de données du thème sont quatre fichiers **CSV** placés dans `donnees/signalements/`. Ils sont chargés par la commande de gestion `charger_donnees` (`signalement/management/commands/charger_donnees.py`).

```powershell
python manage.py charger_donnees
```

| Fichier CSV | Modèle | Ordre |
|---|---|---|
| `utilisateurs.csv` | `Utilisateur` | 1 |
| `categories.csv` | `Categorie` | 2 |
| `objets.csv` | `Lieu` | 3 |
| `actions.csv` | `Signalement` | 4 |

L'ordre respecte les clés étrangères (les tables parentes d'abord). Tout se passe dans une transaction : si une ligne est invalide, rien n'est inséré.

**À savoir**
- La commande **vide d'abord** les quatre tables, puis recharge les CSV : elle peut donc être relancée sans doublons. Les **super-utilisateurs** (comptes admin) sont conservés.
- Les en-têtes CSV doivent porter les **noms des champs du modèle**. Pour les clés étrangères, utilise le suffixe `_id` (`categorie_id`, `utilisateur_id`, `lieu_id`, `regroupe_avec_id`).
- Les colonnes `id` des CSV sont conservées, ce qui permet aux fichiers de se référencer entre eux. Évite qu'un `id` d'`utilisateurs.csv` soit celui d'un super-utilisateur déjà présent.
- Les mots de passe en clair des CSV sont **hachés** à l'import ; ceux déjà hachés sont laissés tels quels.
- Une cellule vide devient `NULL` pour un champ nullable (`regroupe_avec_id`) et une chaîne vide pour un champ texte (`motif_rejet`).
- Les dates sans fuseau sont interprétées dans le fuseau du projet (Europe/Paris) et conservées telles quelles (pas d'`auto_now`).

## Organisation du travail (Git)

| Branche | Usage |
|---|---|
| `main` | Version stable, uniquement des merges validés |
| `feature/models` | Création des modèles |
| `feature/<nom>` | Une branche par fonctionnalité |

```powershell
git checkout main
git pull
git checkout -b feature/ma-fonctionnalite
git add .
git commit -m "Ajout de ma fonctionnalité"
git push -u origin feature/ma-fonctionnalite
# puis ouvrir une Pull Request sur GitHub
```

Règles de l'équipe :
- toujours faire `git pull` avant de commencer (surtout en changeant de machine) ;
- messages de commit clairs ;
- pas de commit direct sur `main` ;
- ne jamais committer `venv/` ni `db.sqlite3` (couverts par `.gitignore`).

## Tests

```powershell
python manage.py test
```

## Équipe

| Membre | Contribution |
|---|---|
| Matisse Guerguet ([@guerguet-matisse](https://github.com/guerguet-matisse)) | App `signalement` (modèles, catalogue, gestion) |
| _Coéquipier 2_ | App `comptes` (utilisateurs, authentification) |
| _Coéquipier 3_ | _À compléter_ |

## Pistes d'amélioration

- Carte interactive des lieux et signalements (Leaflet), grâce aux coordonnées GPS déjà stockées
- Photos jointes aux signalements
- Historique des changements d'état
- Notifications par e-mail
- Tableau de bord statistique (par quartier, catégorie, délai de résolution)
- API REST (Django REST Framework)

## Licence

Projet pédagogique — usage éducatif.
