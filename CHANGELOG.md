# Changelog

Tous les changements notables de ce projet seront documentés dans ce fichier.

Le format est basé sur [Keep a Changelog](https://keepachangelog.com/fr/1.0.0/),
et ce projet adhère au [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.2.1] - 2025-04-03

### Ajouté
- Indicateur de chargement (spinner) pendant le calcul du nombre d'événements
- Tooltip indiquant que le nombre d'événements concerne les 30 prochains jours
- Amélioration de la lisibilité de la liste des calendriers

### Modifié
- Correction de l'affichage des dates de synchronisation pour respecter le fuseau horaire de l'utilisateur
- Optimisation du calcul du nombre d'événements avec mise en cache
- Amélioration de la gestion des fuseaux horaires dans toute l'application

### Technique
- Correction de la gestion des fuseaux horaires dans les templates Jinja2
- Amélioration de la conversion des dates en UTC dans la base de données
- Optimisation de l'affichage des dates côté client

## [1.2.0] - 2024-04-03

### Ajouté
- Bouton d'ajout de calendrier ICS/iCal dans la page principale
- Infobulles d'aide pour une meilleure expérience utilisateur
- Modales de confirmation pour toutes les actions importantes

### Modifié
- Simplification de la barre de navigation
- Suppression des éléments en double dans l'interface
- Amélioration de la présentation des informations d'aide
- Optimisation de l'espace d'affichage
- Harmonisation des styles des boutons et des modales

### Amélioré
- Meilleure ergonomie de l'interface utilisateur
- Clarification des instructions pour l'ajout de calendriers
- Réduction de l'encombrement visuel

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

## [1.1.0] - 2024-04-02

### Ajouté
- Modales de confirmation pour les actions importantes (déconnexion, rafraîchissement, purge)
- Amélioration de l'interface utilisateur avec des indicateurs visuels plus clairs
- Documentation détaillée sur le fonctionnement des sources de calendriers
- Meilleure gestion des erreurs avec des messages plus explicites

### Modifié
- Refonte de l'interface de gestion des sources
- Amélioration de la présentation des calendriers avec leurs couleurs
- Optimisation des messages de confirmation et d'erreur
- Mise à jour de la documentation utilisateur

### Corrigé
- Problèmes d'alignement des icônes dans l'interface
- Affichage des couleurs des calendriers
- Messages d'erreur peu clairs lors des actions sur les sources

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

## [1.2.2] - 2024-04-04

### Ajouté
- Sécurisation des URLs avec HTTPS forcé
- Nouvelle fonction `secure_url_for` pour générer des URLs sécurisées
- Gestion améliorée des fuseaux horaires dans l'affichage des dates de synchronisation

### Modifié
- Correction de l'affichage des dates de dernière synchronisation pour respecter le fuseau horaire de l'utilisateur
- Mise à jour de l'URL du calendrier combiné pour utiliser HTTPS
- Amélioration des infobulles avec des informations plus détaillées

### Technique
- Import du module timezone dans les templates
- Optimisation de la gestion des fuseaux horaires dans les templates Jinja2
- Correction de la génération des URLs pour forcer HTTPS 

## [1.2.3] - 2024-04-04

### Ajouté
- Raccourcis clavier pour les actions principales :
  - Ctrl+R : Rafraîchir les calendriers
  - Ctrl+T : Basculer le thème (clair/sombre)
  - Ctrl+S : Accéder à la page des sources
  - Ctrl+L : Se déconnecter
- Bouton d'aide pour les raccourcis clavier dans la barre de navigation
- Support des raccourcis avec la touche Cmd sur macOS

### Modifié
- Amélioration de l'accessibilité avec des raccourcis clavier
- Optimisation de l'interface utilisateur pour les actions rapides 