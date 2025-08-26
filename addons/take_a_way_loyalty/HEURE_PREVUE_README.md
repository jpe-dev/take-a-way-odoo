# Fonctionnalité Heure Prévue - Commandes PoS

## Description

Cette fonctionnalité ajoute un champ `heure_prevue` aux commandes PoS (Point of Sale) pour permettre de spécifier l'heure prévue de livraison ou de retrait d'une commande.

## Fonctionnalités

### Champ ajouté
- **heure_prevue** : Champ de type `Datetime` qui permet de spécifier l'heure prévue pour la livraison ou le retrait de la commande

### Actions disponibles
1. **"Définir heure prévue"** : Ouvre le wizard avec options rapides
2. **"Heure prévue +1h"** : Définit automatiquement l'heure prévue dans 1 heure
3. **"Effacer heure prévue"** : Efface le champ heure prévue

## Installation

1. Assurez-vous que le module `take_a_way_loyalty` est installé
2. Le champ sera automatiquement disponible dans les commandes PoS
3. Les actions seront disponibles dans le menu Actions des commandes PoS

## Utilisation

### Via les Actions PoS
1. Allez dans **Point de Vente > Commandes**
2. Sélectionnez une commande PoS
3. Cliquez sur **Actions** dans la barre d'outils
4. Choisissez :
   - **"Définir heure prévue"** : Ouvre le wizard avec options
   - **"Heure prévue +1h"** : Définit rapidement dans 1 heure
   - **"Effacer heure prévue"** : Efface le champ

### Via le Wizard
Le wizard offre plusieurs options :
- **Dans 30 minutes** : Définit l'heure prévue dans 30 minutes
- **Dans 1 heure** : Définit l'heure prévue dans 1 heure
- **Dans 2 heures** : Définit l'heure prévue dans 2 heures
- **Heure personnalisée** : Permet de choisir une heure spécifique

### Via l'API
```python
# Créer une commande PoS avec heure prévue
pos_order = env['pos.order'].create({
    'name': 'Commande Test',
    'date_order': fields.Datetime.now(),
    'heure_prevue': fields.Datetime.now() + timedelta(hours=2),
    'amount_total': 50.00,
    'state': 'draft'
})

# Modifier l'heure prévue
pos_order.write({
    'heure_prevue': fields.Datetime.now() + timedelta(hours=3)
})

# Utiliser l'action rapide
pos_order.action_set_heure_prevue_rapide()

# Ouvrir le wizard
pos_order.action_set_heure_prevue()
```

## Dépannage

### Si les actions ne sont pas visibles

1. **Vérifiez que le module est à jour** :
   ```bash
   # Dans Odoo, allez dans Applications > Mettre à jour la liste des applications
   # Puis mettez à jour le module take_a_way_loyalty
   ```

2. **Videz le cache du navigateur** :
   - Appuyez sur Ctrl+F5 pour forcer le rechargement
   - Ou videz le cache du navigateur

3. **Vérifiez les logs Odoo** :
   - Regardez les logs pour voir s'il y a des erreurs
   - Vérifiez que le wizard est bien créé

4. **Utilisez le script de test** :
   ```python
   # Exécutez le script test_simple_heure_prevue.py
   # pour vérifier que le champ fonctionne
   ```

### Erreurs courantes

#### Module ne se charge pas
Si le module ne se charge pas à cause d'erreurs de vues :
1. Vérifiez que les références de vues sont correctes
2. Supprimez les vues problématiques si nécessaire
3. Redémarrez Odoo

#### Wizard ne s'ouvre pas
Si le wizard ne s'ouvre pas :
1. Vérifiez que le modèle `heure.prevue.wizard` existe
2. Vérifiez les permissions dans `ir.model.access.csv`
3. Redémarrez Odoo

### Scripts de diagnostic

- `test_simple_heure_prevue.py` : Test simple du champ heure_prevue
- `test_wizard_heure_prevue.py` : Test du wizard d'heure prévue
- `test_heure_prevue_complete.py` : Test complet de la fonctionnalité

## Fichiers modifiés

### Modèles
- `addons/take_a_way_loyalty/models/models.py` : Ajout du champ `heure_prevue` et des actions dans la classe `PosOrder`

### Wizards
- `addons/take_a_way_loyalty/wizards/heure_prevue_wizard.py` : Wizard pour définir l'heure prévue
- `addons/take_a_way_loyalty/views/heure_prevue_wizard_views.xml` : Vue du wizard

### Données
- `addons/take_a_way_loyalty/data/pos_actions_data.xml` : Actions dans le menu Actions

### Sécurité
- `addons/take_a_way_loyalty/security/ir.model.access.csv` : Permissions pour le wizard

## Test

Un script de test simple est disponible dans `test_simple_heure_prevue.py` pour vérifier que la fonctionnalité fonctionne correctement.

## Compatibilité

- Compatible avec Odoo 18.0
- Nécessite le module `point_of_sale`
- Compatible avec les fonctionnalités existantes du module `take_a_way_loyalty`

## Corrections apportées

### Version 1.0.3
- ✅ Ajouté un wizard pour définir l'heure prévue
- ✅ Ajouté des actions serveur pour accès rapide
- ✅ Ajouté des options rapides (30min, 1h, 2h)
- ✅ Ajouté les permissions nécessaires
- ✅ Créé un script de test simple
- ✅ Mis à jour la documentation
- ✅ Supprimé les vues PoS problématiques

## Avantages de cette approche

1. **Plus fiable** : Pas de dépendance aux vues PoS qui peuvent changer
2. **Plus flexible** : Interface dédiée avec options rapides
3. **Plus accessible** : Via le menu Actions standard d'Odoo
4. **Plus maintenable** : Code séparé et bien structuré
5. **Plus stable** : Pas d'erreurs de parsing de vues 