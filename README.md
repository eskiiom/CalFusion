# Calfusion

Calfusion est une application web qui permet de fusionner des calendriers Google et iCloud en un seul calendrier ICS. Elle offre une interface simple pour gérer et synchroniser vos calendriers.

## Fonctionnalités

- Connexion aux calendriers Google via OAuth2
- Connexion aux calendriers iCloud via CalDAV
- Activation/désactivation des calendriers
- Génération d'un calendrier ICS combiné
- Interface utilisateur intuitive
- Support multilingue (FR/EN)
- Intégration continue avec GitHub Actions

## Fonctionnement

### URL du Calendrier Combiné
Lors de la création d'un compte, un token unique et permanent est généré pour chaque utilisateur. Ce token est utilisé pour créer l'URL du calendrier combiné (ex: http://votre-domaine/calendar/[token]/combined.ics). Cette URL reste stable tant que le compte existe et peut être utilisée de manière permanente dans vos applications de calendrier.

### Gestion des Événements
- Les événements sont récupérés en temps réel lors de l'accès au calendrier combiné
- En cas d'erreur de connexion à une source, les événements des autres sources restent disponibles
- Les événements sont automatiquement convertis dans le fuseau horaire local de l'utilisateur
- Les modifications d'événements sont reflétées immédiatement dans le calendrier combiné

### Personnalisation
- Chaque calendrier peut être personnalisé avec une couleur spécifique
- L'ordre d'affichage des calendriers peut être modifié via l'interface
- Les descriptions des calendriers sont synchronisées avec les sources
- Les modifications de couleur et d'ordre sont sauvegardées localement

### Limitations et Quotas
- Google Calendar API : 1 million de requêtes par jour
- Taille maximale du calendrier combiné : 50 Mo
- Limite de requêtes CalDAV iCloud : 100 requêtes par minute
- Conservation des événements : 1 an dans le passé, 3 ans dans le futur

### Maintenance
#### Sauvegarde
La base de données SQLite est stockée dans `instance/calfusion.db`. Pour sauvegarder :
```bash
cp instance/calfusion.db instance/calfusion.db.backup
```

#### Mise à jour
1. Arrêter l'application
2. Sauvegarder la base de données
3. Pull les changements : `git pull`
4. Mettre à jour les dépendances : `pip install -r requirements.txt`
5. Appliquer les migrations : `flask db upgrade`
6. Redémarrer l'application

#### Logs
Les logs sont stockés dans :
- Développement : console stdout
- Production : `/var/log/calfusion/app.log`

Niveau de log configurable via `FLASK_ENV` :
- development : DEBUG
- production : INFO

### Sécurité
#### Tokens Google
- Validité du token d'accès : 1 heure
- Renouvellement automatique via refresh token
- Le refresh token est permanent sauf révocation par l'utilisateur

#### iCloud
- Utiliser un mot de passe d'application dédié
- Changer le mot de passe en cas de compromission
- L'authentification à deux facteurs doit être activée

### Rafraîchissement des Sources
Le bouton "Rafraîchir" sur chaque source de calendrier permet de :
- Pour Google Calendar : détecter les nouveaux calendriers ajoutés à votre compte
- Pour iCloud : détecter les nouveaux calendriers ajoutés à votre compte
- Pour les calendriers ICS : vérifier que l'URL est toujours valide

Note : Le rafraîchissement met à jour uniquement la liste des calendriers disponibles, pas les événements eux-mêmes. Les événements sont toujours récupérés en temps réel lorsque le calendrier combiné est consulté.

Quand rafraîchir ?
- Après avoir ajouté de nouveaux calendriers dans votre compte Google ou iCloud
- Après avoir supprimé des calendriers
- Après avoir modifié les permissions d'accès à vos calendriers

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
   - En production : http://votre-domaine:5000

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