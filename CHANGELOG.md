# Changelog

Toutes les modifications notables de ce projet seront documentées dans ce fichier.

Le format est basé sur [Keep a Changelog](https://keepachangelog.com/fr/1.1.0/),
et ce projet adhère au [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Non publié]

### Planifié
- Système d'authentification utilisateur via Google OAuth2
- Gestion des utilisateurs avec base de données dédiée
- URLs uniques et sécurisées pour les calendriers combinés
- Interface de gestion de profil utilisateur

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