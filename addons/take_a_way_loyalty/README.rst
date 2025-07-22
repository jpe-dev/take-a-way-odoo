Module de Fidélité - Take A Way
==============================

Ce module gère un système de fidélité complet avec des missions, des points et des récompenses.

Fonctionnalités Principales
--------------------------

1. **Gestion des Missions**
   - Création de missions avec conditions personnalisables
   - Différents types de conditions (achat de produits, montant, nombre de commandes, etc.)
   - Suivi de la progression des participants
   - Missions avec dates de début et de fin

2. **Système de Points**
   - Attribution automatique de points lors de la complétion des missions
   - Suivi des points par utilisateur
   - Interface de consultation des points

3. **Automatisation des Contacts** ⭐ **NOUVEAU**
   - Ajout automatique des nouveaux contacts aux missions actives
   - Création automatique des enregistrements de points

4. **Intégration Point de Vente**
   - Vérification automatique des conditions lors des achats
   - Support des catégories de produits PoS
   - Missions liées à des points de vente spécifiques

Types de Conditions Supportées
-----------------------------

- **ACHAT_PRODUIT** : Achat d'un ou plusieurs produits spécifiques
- **TOTAL_COMMANDE** : Montant minimum par commande
- **NOMBRE_COMMANDE** : Nombre minimum de commandes
- **CATEGORIE_PRODUIT** : Achat dans des catégories spécifiques
- **ACHAT_TOUTES_CATEGORIES** : Achat dans toutes les catégories d'un PoS
- **CONSECUTIVE** : Missions consécutives (quotidiennes, hebdomadaires, mensuelles)
- **ACHATS_JOUR** : 2 achats dans la même journée

Installation
-----------

1. Installer le module via l'interface Odoo
2. Configurer les types de missions dans les données
3. Créer des missions avec les conditions souhaitées

Utilisation
----------

### Création d'une Mission
1. Aller dans **Fidélité > Missions**
2. Créer une nouvelle mission
3. Définir les dates de début et de fin
4. Ajouter des conditions
5. Ajouter des participants ou utiliser l'automatisation

### Automatisation des Contacts
- Les nouveaux contacts sont automatiquement ajoutés aux missions actives

### Suivi des Points
- Consulter **Fidélité > Points de fidélité** pour voir les points de tous les utilisateurs

Documentation Détaillée
----------------------

- `doc/AUTOMATISATION_CONTACTS.md` : Documentation de l'automatisation des contacts
- `doc/RELEASE_NOTES.md` : Notes de version

Support
-------

Pour toute question ou problème, consulter les logs Odoo avec le préfixe `[FIDELITE]`. 