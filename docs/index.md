# Guide d'utilisation CalFusion

## Installation et Configuration

### Connexion à l'application
![Page de connexion](./images/login.png)

1. Accédez à la page d'accueil
2. Cliquez sur "Se connecter avec Google"
3. Autorisez l'accès à vos calendriers

### Ajout de calendriers
![Ajout de calendriers](./images/add-calendar.png)

#### Google Calendar
![Configuration iCloud](./images/gmail-setup.png)
1. Cliquez sur "Ajouter un calendrier Google"
2. Sélectionnez les calendriers à synchroniser
3. Les calendriers apparaîtront dans votre liste

#### iCloud Calendar

1. Cliquez sur "Ajouter un calendrier iCloud"
2. Entrez vos identifiants iCloud (mot de passe pour application)
3. Sélectionnez les calendriers à synchroniser

## Utilisation quotidienne

### Page d'accueil
![Interface principale](./images/main-interface.png)

1. Liste des calendriers
2. Options de synchronisation
3. URL du calendrier combiné

### Page de statistiques
![Statistiques](./images/Statistiques.png)

1. Liste des calendriers
2. Options de synchronisation
3. URL du calendrier combiné

### Paramètres
![Paramètres](./images/settings.png)

1. Configuration du fuseau horaire
2. Durée de synchronisation
3. Préférences d'affichage

## Raccourcis clavier
![Raccourcis](./images/shortcuts.png)

- `Ctrl + R` : Rafraîchir les calendriers
- `Ctrl + T` : Changer de thème
- `Ctrl + S` : Accéder aux paramètres 

## Déploiement

### Déploiement avec Docker

1. **Télécharger l'image**
```bash
docker pull ghcr.io/eskiiom/calfusion:latest
```

2. **Variables d'environnement requises**

Créez un fichier `.env` avec les variables suivantes :
```env
# Configuration OAuth2 Google (obligatoire)
GOOGLE_CLIENT_ID=votre_client_id
GOOGLE_CLIENT_SECRET=votre_client_secret
REDIRECT_URI=https://votre-domaine/oauth2callback
APP_BASE_URL=https://votre-domaine

# Configuration de l'application (obligatoire)
SECRET_KEY=votre_secret_key
FLASK_ENV=production

# Configuration iCloud (optionnel)
ICLOUD_CALDAV_URL=https://caldav.icloud.com
```

3. **Lancer avec Docker**
```bash
docker run -d \
  -p 5000:5000 \
  --env-file .env \
  -v ./instance:/app/instance \
  ghcr.io/eskiiom/calfusion:latest
```

4. **Ou avec Docker Compose**

Créez un fichier `docker-compose.yml` :
```yaml
version: '3.8'
services:
  web:
    image: ghcr.io/eskiiom/calfusion:latest
    ports:
      - "5000:5000"
    environment:
      - FLASK_APP=app.py
      - FLASK_ENV=production
      - GOOGLE_CLIENT_ID=${GOOGLE_CLIENT_ID}
      - GOOGLE_CLIENT_SECRET=${GOOGLE_CLIENT_SECRET}
      - REDIRECT_URI=${REDIRECT_URI}
      - APP_BASE_URL=${APP_BASE_URL}
      - SECRET_KEY=${SECRET_KEY}
    volumes:
      - ./instance:/app/instance  # Pour la persistance de la base de données
    restart: unless-stopped
```

Et lancez avec :
```bash
docker-compose up -d
```

### Configuration OAuth2 Google

1. **Configurer OAuth2 dans Google Cloud Console**
   - Allez sur [Google Cloud Console](https://console.cloud.google.com)
   - Créez ou sélectionnez un projet
   - Activez l'API Google Calendar
   - Dans "Credentials", créez un ID client OAuth2
   - Ajoutez les URIs de redirection autorisés :
     ```
     https://votre-domaine/oauth2callback
     ```
   - Notez le Client ID et le Client Secret

2. **Vérification des redirections**
   - Assurez-vous que `REDIRECT_URI` correspond exactement à l'URI configuré dans Google Cloud Console
   - Le domaine dans `APP_BASE_URL` doit correspondre au domaine de votre application
   - En cas d'erreur 500, vérifiez la correspondance des URIs 