# Projet FastAPI généré avec Orion Studio

Ce projet a été généré automatiquement par [Orion Studio](https://orionstudio.cloud) à partir d'un modèle visuel. Il contient un backend FastAPI complet : modèles SQLModel, schémas Pydantic, routes CRUD et authentification JWT.

## Prérequis

- Python 3.11 ou supérieur
- pip
- Une base de données PostgreSQL accessible (créée au préalable)

## 1. Installation

Placez-vous à la racine du projet, puis créez un environnement virtuel :

```bash
python -m venv venv
```

Activez-le :

```bash
# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

Installez les dépendances :

```bash
pip install -r requirements.txt
```

## 2. Configuration

Un fichier `.env` a déjà été généré à la racine du projet avec les valeurs saisies dans Orion Studio (clés d'API, configuration de base de données, secrets JWT). Ouvrez-le et vérifiez/ajustez les valeurs avant de démarrer :

```bash
# .env
DB_USERNAME=...
DB_PASSWORD=...
DATABASE_URL=...
```

Assurez-vous que la base de données `` existe déjà sur votre serveur postgresql avant de continuer — le projet ne la crée pas automatiquement, seules les tables le sont.

## 3. Créer les tables de la base de données

Les modèles SQLModel sont définis dans `modeles/models.py`. Les tables sont créées automatiquement au démarrage de l'application grâce à l'événement `startup` défini dans `main.py` (fonction `create_db_and_tables`) — aucune action manuelle n'est requise pour un premier lancement.

> Ce projet ne contient pas encore de système de migration (type Alembic). Toute modification ultérieure du schéma (ajout de colonne, etc.) nécessite de recréer les tables ou d'écrire une migration manuelle.

## 4. Lancer le serveur

```bash
fastapi dev main.py
```

Le serveur démarre par défaut sur `http://127.0.0.1:8000`, avec rechargement automatique à chaque modification de fichier.

> La commande `fastapi` (CLI) est fournie par l'extra `fastapi[standard]`, déjà présent dans `requirements.txt`. Si vous obtenez une erreur du type *"please install fastapi[standard]"*, vérifiez que votre environnement virtuel est bien activé et que `pip install -r requirements.txt` a été exécuté dedans.

La documentation interactive générée automatiquement par FastAPI est disponible sur :

- Swagger UI : `http://127.0.0.1:8000/docs`
- Redoc : `http://127.0.0.1:8000/redoc`

## 5. Structure du projet

```
.
├── main.py                # Point d'entrée, enregistrement des routers
├── config.py              # Configuration de l'application
├── database.py             # Connexion, engine et session SQLModel
├── modeles/
│   └── models.py           # Modèles SQLModel (tables)
├── schemas/
│   └── *.py               # Schémas Pydantic (Base / Create / Update / Public)
├── routes/
│   └── *.py               # Routes CRUD par modèle (APIRouter)
├── securites/
│   └── securite.py          # Configuration JWT / OAuth2
├── erreurs/                # Gestion des erreurs
├── utils/                  # Fonctions utilitaires
└── .env                  # Variables d'environnement
```

## 6. Authentification (JWT)

Ce projet utilise l'authentification JWT. Les routes de connexion/inscription se trouvent dans `routes/auth.py`. Le token est ensuite attendu dans l'en-tête `Authorization: Bearer <token>` pour accéder aux routes protégées (marquées `protege` dans le modèle).

## 7. Déploiement

Pour un déploiement en production, deux options :

```bash
# Option 1 : via le CLI FastAPI (mode production, sans rechargement automatique)
fastapi run main.py

# Option 2 : via Gunicorn + worker Uvicorn (déjà présents avec fastapi[standard] et gunicorn)
gunicorn main:app -k uvicorn.workers.UvicornWorker
```

Pensez à définir des secrets robustes dans `.env` avant toute mise en production.