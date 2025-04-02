# Calfusion

Calfusion est une application web qui permet de fusionner des calendriers Google et iCloud en un seul calendrier ICS. Elle offre une interface simple pour gérer et synchroniser vos calendriers.

## Fonctionnalités

- Connexion aux calendriers Google via OAuth2
- Connexion aux calendriers iCloud via CalDAV
- Activation/désactivation des calendriers
- Génération d'un calendrier ICS combiné
- Interface utilisateur intuitive
- Support multilingue (FR/EN)

## Prérequis

- Python 3.8 ou supérieur
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
     GOOGLE_CLIENT_ID=votre_client_id
     GOOGLE_CLIENT_SECRET=votre_client_secret
     REDIRECT_URI=http://localhost:5000/oauth2callback
     SECRET_KEY=votre_clé_secrète
     ICLOUD_CALDAV_URL=https://caldav.icloud.com
     ```

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
├── app.py              # Application principale
├── requirements.txt    # Dépendances
├── .env               # Configuration
├── static/            # Fichiers statiques
│   └── combined_calendar.ics
├── templates/         # Templates HTML
│   ├── index.html
│   ├── add_icloud.html
│   └── base.html
└── instance/          # Base de données SQLite
    └── calfusion.db
```

## Dépendances Principales

- Flask : Framework web
- SQLAlchemy : ORM pour la base de données
- google-auth-oauthlib : Authentification Google
- caldav : Client CalDAV pour iCloud
- icalendar : Gestion des fichiers ICS

## Utilisation

1. Lancer l'application :
```bash
python app.py
```

2. Ouvrir un navigateur et aller à `http://localhost:5000`

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

### Contribution
1. Fork le projet
2. Créer une branche (`git checkout -b feature/AmazingFeature`)
3. Commit les changements (`git commit -m 'Add some AmazingFeature'`)
4. Push vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrir une Pull Request

## Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

## Support

Pour toute question ou problème, veuillez ouvrir une issue sur GitHub. 