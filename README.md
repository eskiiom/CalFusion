# CalFusion

## Documentation

La documentation complète avec captures d'écran est disponible sur [https://eskiiom.github.io/calfusion/](https://eskiiom.github.io/calfusion/)

Vous y trouverez :
- Guide d'installation et de configuration
- Tutoriels d'utilisation avec captures d'écran
- Guide de dépannage
- Liste des raccourcis clavier

## Fonctionnalités

- **Gestion unifiée des calendriers**
  - Support pour Google Calendar, iCloud Calendar et calendriers ICS/iCal
  - Synchronisation personnalisable (1 à 365 jours)
  - Génération sécurisée d'URLs HTTPS pour les calendriers combinés
  - Interface intuitive avec mode sombre

- **Personnalisation avancée**
  - Durée de synchronisation configurable avec préréglages
  - Gestion des fuseaux horaires
  - Personnalisation des couleurs des calendriers
  - Préférences utilisateur persistantes

- **Statistiques et monitoring**
  - Vue d'ensemble des calendriers actifs
  - Compteur d'événements à venir sur la période configurée
  - Répartition par type de calendrier
  - Rafraîchissement dynamique des données

## Fonctionnement

Un identifiant unique et sécurisé est généré pour chaque utilisateur lors de sa première connexion. Cet identifiant reste stable entre les sessions et permet d'accéder au calendrier combiné via une URL HTTPS. La synchronisation des événements est personnalisable, permettant de choisir la période future à synchroniser (de 1 jour à 1 an).

## Interface utilisateur

- **Navigation simplifiée**
  - Barre de navigation intuitive
  - Icônes explicites
  - Mode sombre adaptatif
  - Thème adapté aux préférences système

- **Gestion des calendriers**
  - Vue d'ensemble claire des calendriers
  - Indicateurs de synchronisation en temps réel
  - Aide contextuelle détaillée
  - Rafraîchissement dynamique des données

- **Paramètres utilisateur**
  - Configuration du fuseau horaire
  - Personnalisation de la durée de synchronisation
  - Gestion des préférences d'affichage
  - Options de personnalisation étendues

## Prérequis

- Python 3.10 ou supérieur
- pip (gestionnaire de paquets Python)
- Compte Google avec accès à l'API Calendar
- Compte iCloud avec mot de passe d'application

## Installation

1. Cloner le repository :
```bash
git clone https://github.com/votre-username/calfusion.git
cd calfusion
```

2. Créer un environnement virtuel :
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. Installer les dépendances :
```bash
pip install -r requirements.txt
```

4. Configurer les variables d'environnement :
   - Copier le fichier `.env.example` en `.env`
   - Remplir les variables suivantes :
     ```
     # Google OAuth2 Configuration
     GOOGLE_CLIENT_ID=votre_client_id
     GOOGLE_CLIENT_SECRET=votre_client_secret
     REDIRECT_URI=http://votre-domaine:5000/oauth2callback
     APP_BASE_URL=http://votre-domaine:5000

     # Application Configuration
     FLASK_ENV=development
     FLASK_APP=app.py
     FLASK_HOST=0.0.0.0  # Utiliser 0.0.0.0 pour écouter sur toutes les interfaces
     FLASK_PORT=5000     # Port par défaut, peut être modifié selon vos besoins
     SECRET_KEY=votre_clé_secrète

     # iCloud Configuration
     ICLOUD_CALDAV_URL=https://caldav.icloud.com
     ```

   Notes importantes :
   - Pour le développement local, utilisez votre adresse IP locale (ex: 192.168.0.109) comme domaine
   - Pour la production, utilisez votre nom de domaine réel
   - `FLASK_HOST=0.0.0.0` permet à l'application d'être accessible depuis n'importe quelle adresse
   - Assurez-vous que le port choisi est ouvert sur votre pare-feu

5. Initialiser la base de données :
```bash
flask db init
flask db migrate
flask db upgrade
```

## Configuration

### Google Calendar
1. Aller sur [Google Cloud Console](https://console.cloud.google.com)
2. Créer un nouveau projet
3. Activer l'API Google Calendar
4. Créer des identifiants OAuth2
5. Configurer les URIs de redirection autorisés
6. Copier le Client ID et le Client Secret dans le fichier `.env`

### iCloud
1. Aller sur [Apple ID](https://appleid.apple.com)
2. Générer un mot de passe d'application
3. Utiliser ce mot de passe dans l'application

## Structure du Projet

```
calfusion/
├── app.py                # Application principale
├── requirements.txt      # Dépendances
├── pyproject.toml       # Configuration du projet Python
├── .env.example         # Template des variables d'environnement
├── static/              # Fichiers statiques
│   └── combined_calendar.ics
├── templates/           # Templates HTML
│   ├── index.html
│   ├── add_icloud.html
│   └── base.html
├── tests/              # Tests unitaires
│   ├── conftest.py
│   └── test_app.py
├── .github/            # Configuration GitHub Actions
│   └── workflows/
│       └── python-app.yml
└── instance/           # Base de données SQLite
    └── calfusion.db
```

## Dépendances Principales

- Flask==3.0.2 : Framework web
- SQLAlchemy : ORM pour la base de données
- google-auth-oauthlib==1.2.0 : Authentification Google
- caldav==1.3.9 : Client CalDAV pour iCloud
- vobject==0.9.6.1 : Gestion des fichiers ICS
- pytest : Tests unitaires

## Utilisation

1. Lancer l'application :
```bash
python app.py
```

2. Ouvrir un navigateur et aller à l'URL configurée dans APP_BASE_URL
   - En local : http://votre-ip:5000 (ex: http://192.168.0.109:5000)
   - En production : https://votre-domaine:5000

3. Connecter vos calendriers :
   - Cliquer sur "Ajouter un calendrier Google"
   - Cliquer sur "Ajouter un calendrier iCloud"
   - Suivre les instructions d'authentification

4. Activer/désactiver les calendriers souhaités

5. Télécharger le calendrier combiné :
   - Cliquer sur "Télécharger le calendrier combiné"
   - Importer le fichier ICS dans votre application de calendrier

## Développement

### Style de Code
- PEP 8 pour Python
- ESLint pour JavaScript
- Prettier pour HTML/CSS

### Tests
```bash
python -m pytest
```

### CI/CD
Le projet utilise GitHub Actions pour :
- Exécuter les tests automatiquement
- Vérifier la sécurité des dépendances
- Construire le package Python
- Vérifier la compatibilité Python 3.10

### Contribution
1. Fork le projet
2. Créer une branche (`git checkout -b feature/AmazingFeature`)
3. Commit les changements (`git commit -m 'Add some AmazingFeature'`)
4. Push vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrir une Pull Request

## Sécurité

- Ne jamais commiter le fichier `.env` contenant vos secrets
- Utiliser des mots de passe d'application pour iCloud
- Les secrets GitHub sont utilisés pour les tests CI/CD

## Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

## Support

Pour toute question ou problème, veuillez ouvrir une issue sur GitHub.

## Déploiement avec Docker

### Prérequis
- Docker
- Docker Compose

### Structure des fichiers Docker
```
calfusion/
├── Dockerfile          # Configuration de l'image Docker
├── docker-compose.yml  # Configuration de l'orchestration
└── .dockerignore      # Liste des fichiers à exclure
```

### Configuration Docker

#### Dockerfile
Le Dockerfile utilise Python 3.10-slim comme base et configure l'environnement :
```dockerfile
FROM python:3.10-slim
WORKDIR /app

# Installation des dépendances système
RUN apt-get update && apt-get install -y \
    gcc \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# Installation des dépendances Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Configuration de l'application
COPY . .
RUN useradd -m calfusion && \
    chown -R calfusion:calfusion /app
USER calfusion

ENV FLASK_APP=app.py
ENV FLASK_ENV=production
ENV FLASK_HOST=0.0.0.0
ENV FLASK_PORT=5000

EXPOSE 5000
CMD ["flask", "run", "--host=0.0.0.0"]
```

#### Docker Compose
Le fichier docker-compose.yml configure le service et ses dépendances :
```yaml
version: '3.8'
services:
  web:
    build: .
    ports:
      - "5000:5000"
    environment:
      - FLASK_APP=app.py
      - FLASK_ENV=production
      # Variables à configurer
      - GOOGLE_CLIENT_ID=${GOOGLE_CLIENT_ID}
      - GOOGLE_CLIENT_SECRET=${GOOGLE_CLIENT_SECRET}
      - SECRET_KEY=${SECRET_KEY}
      - APP_BASE_URL=${APP_BASE_URL}
    volumes:
      - ./instance:/app/instance  # Base de données
      - ./static:/app/static      # Fichiers statiques
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

### Utilisation

1. **Préparation de l'environnement**
```bash
# Copier le fichier d'exemple
cp .env.example .env

# Éditer le fichier .env avec vos valeurs
nano .env
```

2. **Construction et démarrage**
```bash
# Construire et démarrer les conteneurs
docker-compose up --build -d

# Voir les logs
docker-compose logs -f

# Arrêter les conteneurs
docker-compose down
```

3. **Commandes utiles**
```bash
# Reconstruire l'image
docker-compose build

# Voir l'état des conteneurs
docker-compose ps

# Redémarrer le service
docker-compose restart web
```

### Configuration pour le développement

Pour le développement, modifiez le docker-compose.yml :
```yaml
services:
  web:
    volumes:
      - .:/app  # Pour le hot-reload
    environment:
      - FLASK_ENV=development
```

## Dépannage

### Problèmes d'authentification Google

1. **Erreur de refresh token**
   Si vous obtenez l'erreur : "The credentials do not contain the necessary fields need to refresh the access token", suivez ces étapes :
   ```bash
   1. Déconnectez-vous de l'application
   2. Allez sur https://myaccount.google.com/permissions
   3. Trouvez l'application CalFusion
   4. Cliquez sur "Révoquer l'accès"
   5. Retournez sur l'application
   6. Reconnectez-vous avec Google
   ```
   Cette procédure permet d'obtenir un nouveau refresh token avec toutes les permissions nécessaires.

2. **Erreur 500 lors de l'authentification**
   - Vérifiez que les variables d'environnement sont correctement configurées :
     ```
     GOOGLE_CLIENT_ID=votre_client_id
     GOOGLE_CLIENT_SECRET=votre_client_secret
     REDIRECT_URI=http://votre-domaine:5000/oauth2callback
     ```
   - Assurez-vous que l'URI de redirection correspond exactement à celle configurée dans la console Google Cloud

### Problèmes de synchronisation

1. **Les calendriers ne se rafraîchissent pas**
   - Vérifiez les logs de l'application
   - Assurez-vous que les credentials sont à jour
   - Vérifiez que la source est connectée dans la page Sources

2. **Calendriers iCloud non visibles**
   - Vérifiez que le mot de passe d'application est correct
   - Assurez-vous que l'URL CalDAV est accessible
   - Vérifiez les permissions des calendriers dans les paramètres iCloud

### Problèmes de base de données

1. **Erreurs SQLite**
   ```bash
   # Sauvegardez d'abord la base de données
   cp instance/calendars.db instance/calendars.db.backup
   
   # Réinitialisez la base de données
   rm instance/calendars.db
   flask db upgrade
   ```

2. **Problèmes de migration**
   - En cas d'erreur lors d'une migration :
     ```bash
     flask db stamp head
     flask db migrate
     flask db upgrade
     ```

### Problèmes de déploiement

1. **Erreurs avec Docker**
   ```bash
   # Reconstruire l'image
   docker-compose build --no-cache
   
   # Vérifier les logs
   docker-compose logs -f
   ```

2. **Problèmes de certificats SSL**
   - Vérifiez la configuration Nginx
   - Renouvelez les certificats Let's Encrypt :
     ```bash
     sudo certbot renew
     ```

### Maintenance

1. **Nettoyage périodique**
   ```bash
   # Supprimer les fichiers temporaires
   rm -rf instance/sessions/*
   rm static/combined_calendar.ics
   ```

2. **Sauvegarde**
   ```bash
   # Sauvegarder la base de données
   cp instance/calendars.db /chemin/vers/backup/calendars_$(date +%Y%m%d).db
   ```

### Logs et Débogage

1. **Activer les logs détaillés**
   ```python
   # Dans .env
   FLASK_ENV=development
   FLASK_DEBUG=1
   ```

2. **Consulter les logs**
   ```bash
   # Logs de l'application
   tail -f logs/app.log
   
   # Logs Docker
   docker-compose logs -f
   ```

### Contact et Support

Si vous rencontrez un problème non résolu :
1. Consultez les [Issues GitHub](https://github.com/votre-username/calfusion/issues)
2. Créez une nouvelle issue avec :
   - Description détaillée du problème
   - Logs pertinents
   - Étapes pour reproduire le problème
   - Environnement (OS, version Python, etc.)

