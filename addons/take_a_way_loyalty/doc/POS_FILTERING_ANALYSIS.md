# Analyse du Filtrage PoS - Problème et Solution

## Résumé du Problème

Le produit "Bacon Burger" reste visible dans l'interface PoS malgré le fait que `disponibilite_inventaire = False`.

## Tests Effectués

### 1. Test Backend (Réussi ✅)
- **Script**: `test_pos_filtering.py`
- **Résultat**: Le Bacon Burger est **correctement filtré** au niveau backend
- **Preuve**: `"Bacon Burger dans la liste des produits disponibles: False"`
- **Conclusion**: Notre logique de filtrage fonctionne correctement

### 2. Test Frontend (Échec ❌)
- **Interface PoS**: Le Bacon Burger reste visible et sélectionnable
- **Problème**: Le frontend PoS n'utilise pas les données filtrées

## Analyse Technique

### Méthodes Overridées (Backend)
```python
# ProductTemplate
def _get_pos_products_domain(self)
def _get_pos_products(self, pos_config_id=None)

# ProductProduct  
def _get_pos_products_domain(self)
def _get_pos_products(self, pos_config_id=None)
def search_read(self, domain=None, fields=None, ...)

# PosConfig
def _get_available_products(self)
def _get_products_domain(self)

# PosSession
def _loader_params_product_product(self)
def _get_pos_products_domain(self)
def _load_model_data(self, model_name, domain=None, fields=None)
def load_data(self, models_to_load=None)
def _loader_params(self, model_name)
```

### Problème Identifié
1. **Méthodes Privées**: Les méthodes overridées sont privées et ne sont pas exposées via XML-RPC
2. **Cache Frontend**: Le PoS frontend utilise probablement un cache local
3. **Mécanisme de Chargement Différent**: Le PoS utilise un mécanisme de chargement différent

## Solution Proposée

### Option 1: Override des Méthodes Publiques (Recommandée)
Override les méthodes publiques que le PoS utilise réellement pour charger les produits.

```python
# PosSession - Méthodes publiques
def load_data(self, models_to_load=None):
    """Override pour filtrer les produits lors du chargement"""
    result = super().load_data(models_to_load)
    
    # Filtrer les produits dans le résultat
    if 'product.product' in result:
        products = result['product.product']
        filtered_products = []
        for product in products:
            if product.get('product_tmpl_id') and product['product_tmpl_id'][2].get('disponibilite_inventaire', True):
                filtered_products.append(product)
        result['product.product'] = filtered_products
    
    return result
```

### Option 2: Override de la Méthode de Recherche
Override la méthode `search_read` sur `product.product` pour filtrer automatiquement.

```python
def search_read(self, domain=None, fields=None, offset=0, limit=None, order=None):
    """Override pour filtrer automatiquement les produits non disponibles"""
    if domain is None:
        domain = []
    
    # Ajouter le filtre de disponibilité
    domain += [('product_tmpl_id.disponibilite_inventaire', '=', True)]
    
    return super().search_read(domain, fields, offset, limit, order)
```

### Option 3: Méthode de Rechargement Forcé
Créer une méthode pour forcer le rechargement complet du PoS.

```python
def force_pos_reload(self):
    """Force le rechargement complet du PoS"""
    # Invalider tous les caches
    self.env.cr.execute("SELECT 1")  # Force un commit
    
    # Redémarrer la session PoS
    active_sessions = self.env['pos.session'].search([('state', '=', 'opened')])
    for session in active_sessions:
        session.action_pos_session_close()
        session.action_pos_session_open()
```

## Recommandation

**Utiliser l'Option 1** car elle cible directement le mécanisme de chargement des données du PoS.

## Prochaines Étapes

1. Implémenter l'override de `load_data` dans `PosSession`
2. Tester avec un rechargement complet du PoS
3. Vérifier que le Bacon Burger n'apparaît plus dans l'interface

## Logs de Debug

Pour diagnostiquer le problème, ajouter des logs dans les méthodes suivantes:
- `PosSession.load_data()`
- `ProductProduct.search_read()`
- `PosSession._loader_params_product_product()`

## Test de Validation

```python
# Script de test pour valider la solution
def test_pos_frontend_filtering():
    # 1. Ouvrir le PoS
    # 2. Vérifier que le Bacon Burger n'apparaît pas
    # 3. Changer la disponibilité
    # 4. Recharger le PoS
    # 5. Vérifier que le produit apparaît/disparaît
``` 