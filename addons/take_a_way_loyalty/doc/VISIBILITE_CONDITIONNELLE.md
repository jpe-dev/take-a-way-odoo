# Visibilité Conditionnelle des Champs selon le Type de Mission

## Vue d'ensemble

Cette fonctionnalité permet d'afficher uniquement les champs pertinents selon le type de mission sélectionné lors de la création d'une condition de mission. Cela améliore l'expérience utilisateur en réduisant la confusion et en guidant l'utilisateur vers les champs appropriés.

## Types de Mission Supportés

### 1. ACHAT_PRODUIT
**Champs visibles :**
- `produits_ids` : Sélection des produits spécifiques
- `quantites_produits` : Quantités requises par produit
- `resume_quantites` : Résumé des quantités (lecture seule)
- `quantite` : Quantité globale (si pas de quantités par produit)

### 2. CATEGORIE_PRODUIT
**Champs visibles :**
- `categories_ids` : Sélection des catégories de produits
- `quantite` : Quantité requise dans les catégories sélectionnées

### 3. ACHAT_TOUTES_CATEGORIES
**Champs visibles :**
- `categories_ids` : Catégories du point de vente (lecture seule, auto-remplies)
- Bouton "Réinitialiser les catégories" pour forcer la mise à jour

### 4. PARRAINAGE
**Champs visibles :**
- `quantite` : Nombre de filleuls requis pour compléter la mission

### 5. TOTAL_COMMANDE
**Champs visibles :**
- `montant_minimum` : Montant minimum requis pour la commande

### 6. NOMBRE_COMMANDE
**Champs visibles :**
- `nombre_commandes` : Nombre de commandes requis

### 7. ACHATS_JOUR
**Champs visibles :**
- `quantite` : Nombre d'achats requis dans la même journée (fixé à 2)

### 8. CONSECUTIVE
**Champs visibles :**
- `type_periode` : Type de période (quotidien, hebdomadaire, mensuel)
- `nombre_periodes` : Nombre de périodes consécutives requises
- `type_objectif` : Type d'objectif (commandes ou montant)
- `commandes_par_periode` : Nombre de commandes par période (si type_objectif = 'commandes')
- `montant_par_periode` : Montant minimum par période (si type_objectif = 'montant')

## Implémentation Technique

### Vue XML
La visibilité est contrôlée par les attributs `invisible` et `readonly` dans les vues XML :

```xml
<field name="produits_ids" 
       widget="many2many_tags" 
       invisible="type_condition.code != 'ACHAT_PRODUIT'"
       required="type_condition.code == 'ACHAT_PRODUIT'"/>
```

### JavaScript
Un contrôleur JavaScript personnalisé gère les interactions dynamiques :

- Détection du changement de type de condition
- Mise à jour automatique de la visibilité des champs
- Amélioration de l'expérience utilisateur

### Modèle Python
Le modèle gère automatiquement certaines valeurs par défaut :

```python
@api.onchange('type_condition', 'mission_id')
def _onchange_type_condition(self):
    if record.type_condition.code == 'ACHATS_JOUR':
        record.quantite = 2  # Fixé à 2 achats
```

## Utilisation

1. **Créer une mission** dans le menu Fidélité > Missions
2. **Ajouter une condition** dans l'onglet "Conditions"
3. **Sélectionner le type de condition** dans le champ "Type de condition"
4. **Remplir les champs visibles** selon le type choisi
5. **Sauvegarder** la condition

## Avantages

- **Interface claire** : Seuls les champs pertinents sont affichés
- **Réduction d'erreurs** : L'utilisateur ne peut pas saisir des données inappropriées
- **Guidage utilisateur** : L'interface guide naturellement vers les bonnes actions
- **Performance** : Moins de champs à traiter dans les vues
- **Maintenabilité** : Code plus organisé et facile à maintenir

## Compatibilité

Cette fonctionnalité est compatible avec Odoo 18 et utilise les bonnes pratiques de développement Odoo :

- Attributs `invisible` et `readonly` pour la visibilité
- Contrôleurs JavaScript personnalisés pour les interactions
- Méthodes `@api.onchange` pour la logique métier
- Vues XML optimisées pour les performances