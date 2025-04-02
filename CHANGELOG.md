# Changelog

Tous les changements notables de ce projet seront documentés dans ce fichier.

Le format est basé sur [Keep a Changelog](https://keepachangelog.com/fr/1.0.0/),
et ce projet adhère au [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.1] - 2025-04-03

### Ajouté
- Support des couleurs RGBA des calendriers iCloud
- Conversion automatique des couleurs RGBA en RGB pour l'affichage
- Amélioration de l'interface utilisateur pour les icônes de calendriers

### Modifié
- Correction de l'alignement des icônes de calendriers
- Amélioration de l'affichage des couleurs de calendriers
- Optimisation du stockage des couleurs en format RGBA

### Corrigé
- Correction de l'affichage des couleurs noires pour les calendriers iCloud
- Correction de l'alignement des icônes Apple et Google
- Amélioration de la compatibilité avec les couleurs personnalisées

## [1.1.0] - 2025-04-03

### Ajouté
- Support des noms de calendriers iCloud avec emojis et caractères spéciaux
- Récupération des couleurs personnalisées des calendriers iCloud
- Amélioration de la synchronisation des propriétés des calendriers

### Modifié
- Remplacement de la méthode de récupération des propriétés CalDAV par une approche PROPFIND directe
- Correction du problème d'affichage des UUIDs à la place des noms de calendriers
- Amélioration de la gestion des erreurs lors de la récupération des propriétés des calendriers

### Corrigé
- Correction du problème de décodage des réponses CalDAV
- Correction de l'affichage des noms de calendriers spéciaux (home, work, etc.)
- Correction des avertissements de dépréciation liés à datetime.utcnow()

## [1.0.0] - 2025-04-01

### Ajouté
- Version initiale de l'application
- Support des calendriers Google via OAuth2
- Support des calendriers iCloud via CalDAV
- Interface utilisateur multilingue (FR/EN)
- Génération de calendriers ICS combinés
- Système d'activation/désactivation des calendriers
- Documentation complète
- Tests unitaires
- Intégration continue avec GitHub Actions

### Planifié
- Système d'authentification utilisateur via Google OAuth2
- Gestion des utilisateurs avec base de données dédiée
- URLs uniques et sécurisées pour les calendriers combinés
- Interface de gestion de profil utilisateur
- Indicateurs de statut de connexion pour Google et iCloud
- Boutons de déconnexion individuels pour chaque service
- Bouton de déconnexion global de l'application
- Retours visuels améliorés pour les états de connexion

### Ajouté
- Interface responsive pour les appareils mobiles
- Mise en page adaptative pour les petits écrans
- Interactions tactiles optimisées
- Message d'information sur le temps de synchronisation des calendriers
- Mise à jour des tooltips avec des informations sur le temps d'attente
- Indicateur de chargement pendant la synchronisation des calendriers
- Animations de retour visuel pour les actions de calendrier
- Tooltips bilingues (FR/EN) sur tous les éléments interactifs
- Retour visuel amélioré pour la copie d'URL
- Icônes distinctives pour les calendriers Google (logo Google) et iCloud (logo Apple)
- Styles personnalisés pour les boutons d'ajout de calendrier
- Intégration de Font Awesome 6.5.1 pour les icônes
- Variables CSS pour la gestion des couleurs de bordure des calendriers
- Sélecteur de couleur pour personnaliser la couleur de chaque calendrier
- Retour visuel lors du changement de couleur (animation de succès/erreur)
- Tooltips bilingues pour le sélecteur de couleur
- Authentification complète avec Google OAuth2
- Gestion des sessions utilisateur avec Flask-Login
- URLs uniques par utilisateur pour les calendriers combinés
- Page de connexion avec interface moderne
- Nettoyage automatique des sessions et messages flash
- Base de données SQLite pour stocker les utilisateurs et leurs calendriers
- Modèle User pour gérer les comptes utilisateurs
- Token unique par utilisateur pour l'accès aux calendriers

### Modifié
- Optimisation de la mise en page pour les appareils mobiles
- Ajustement des tailles de police et espacements pour le mobile
- Amélioration de l'ergonomie des boutons et contrôles sur mobile
- Amélioration du retour visuel lors de l'activation/désactivation des calendriers
- Remplacement des alertes par des animations et transitions
- Amélioration de l'interface utilisateur avec des couleurs spécifiques pour chaque service
- Mise à jour du style des boutons d'action pour une meilleure cohérence visuelle
- Optimisation du code CSS pour éviter les erreurs de linter
- Remplacement de l'alerte de copie par un tooltip dynamique
- Amélioration de l'interface utilisateur avec des animations fluides
- Optimisation du code JavaScript pour une meilleure gestion des états
- Mise à jour de la ROADMAP pour inclure l'authentification utilisateur
- Sécurisation de toutes les routes avec @login_required
- Amélioration de la gestion des messages flash
- Stockage des calendriers par utilisateur dans la base de données
- Génération des calendriers combinés à la volée
- Interface utilisateur adaptative pour mobile
- Amélioration des retours visuels lors des actions
- Optimisation du code CSS avec des variables

### Supprimé
- Stockage local des fichiers ICS (maintenant générés à la volée)
- Messages flash persistants non désirés

### Technique
- Implémentation de Media Queries pour la réactivité
- Optimisation des performances sur mobile
- Ajout d'animations CSS pour le retour visuel
- Gestion des états de synchronisation avec classes CSS
- Utilisation des CSS Custom Properties pour la gestion des couleurs
- Amélioration de la maintenabilité du code CSS
- Correction des erreurs de linter dans les templates
- Initialisation automatique des tooltips Bootstrap
- Nouvelle route API pour la mise à jour des couleurs de calendrier
- Validation des couleurs côté serveur
- Gestion des erreurs avec restauration automatique 