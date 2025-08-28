# Disponibilité des Produits dans le Point de Vente (PoS)

## Vue d'ensemble

Cette fonctionnalité permet de contrôler la disponibilité des produits dans le Point de Vente (PoS) en utilisant un champ booléen `disponibilite_inventaire` ajouté au modèle des produits. Lorsqu'un produit est marqué comme non disponible, il ne peut plus être sélectionné dans les commandes PoS.

## Problème Identifié

Le problème principal est que les méthodes que nous avons surchargées ne sont pas les bonnes méthodes utilisées par le frontend PoS d'Odoo. Le PoS utilise des mécanismes de cache et des méthodes spécifiques qui ne sont pas celles que nous avons surchargées.

## Solution Alternative

### 1. Utilisation des Vraies Méthodes PoS

Le PoS d'Odoo utilise principalement les méthodes suivantes pour charger les produits :

- `pos.session._loader_params_product_product()` : Paramètres de chargement des produits
- `pos.session._load_model_data()` : Chargement des données de modèle
- `product.product._get_pos_products()` : Récupération des produits pour le PoS

### 2. Surcharges Correctes

#### PosSession

```python
class PosSession(models.Model):
    _inherit = 'pos.session'

    def _loader_params_product_product(self):
        """Surcharge pour filtrer les produits non disponibles lors du chargement de la session PoS"""
        params = super(PosSession, self)._loader_params_product_product()
        
        # Ajouter le filtre de disponibilité au domaine
        if 'domain' in params:
            params['domain'] += [('product_tmpl_id.disponibilite_inventaire', '=', True)]
        else:
            params['domain'] = [('product_tmpl_id.disponibilite_inventaire', '=', True)]
        
        return params

    def _load_model_data(self, model_name, domain=None, fields=None):
        """Surcharge pour filtrer les produits lors du chargement des données"""
        if model_name == 'product.product':
            if domain is None:
                domain = []
            domain += [('product_tmpl_id.disponibilite_inventaire', '=', True)]
        
        return super(PosSession, self)._load_model_data(model_name, domain, fields)
```

#### ProductProduct

```python
class ProductProduct(models.Model):
    _inherit = 'product.product'

    @api.model
    def _get_pos_products(self, pos_config_id=None):
        """Surcharge pour retourner les produits disponibles pour le PoS"""
        domain = [('product_tmpl_id.disponibilite_inventaire', '=', True)]
        
        # Ajouter les filtres standard du PoS si nécessaire
        if pos_config_id:
            pos_config = self.env['pos.config'].browse(pos_config_id)
            if pos_config.iface_available_categ_ids:
                domain += [('pos_categ_id', 'in', pos_config.iface_available_categ_ids.ids)]
        
        return self.search(domain)
```

### 3. Mécanisme de Rechargement

Pour forcer le rechargement des sessions PoS quand la disponibilité change :

```python
class ProductTemplate(models.Model):
    _inherit = 'product.template'

    def write(self, vals):
        """Override pour forcer le rechargement des sessions PoS quand la disponibilité change"""
        result = super(ProductTemplate, self).write(vals)
        
        # Si la disponibilité a changé, forcer le rechargement des sessions PoS
        if 'disponibilite_inventaire' in vals:
            active_sessions = self.env['pos.session'].search([('state', '=', 'opened')])
            for session in active_sessions:
                try:
                    # Forcer le rechargement en modifiant un champ de la session
                    session.write({'update_stock_at_closing': session.update_stock_at_closing})
                except Exception as e:
                    _logger.error("Erreur lors du rechargement de la session %s: %s", session.id, str(e))
        
        return result
```

## Tests et Débogage

### Scripts de Test

1. **test_disponibilite_pos.py** : Test complet de toutes les méthodes
2. **test_direct.py** : Test via l'API Odoo
3. **run_test.py** : Script d'exécution des tests

### Logs de Débogage

Les méthodes surchargées incluent des logs détaillés pour déboguer :

```python
_logger.info("[DISPO_POS] _loader_params_product_product appelée pour la session %s", self.id)
_logger.info("[DISPO_POS] Paramètres initiaux: %s", params)
_logger.info("[DISPO_POS] Paramètres finaux: %s", params)
```

## Utilisation

### 1. Marquer un Produit comme Non Disponible

1. Aller dans **Produits** > **Produits**
2. Sélectionner le produit à modifier
3. Décocher la case "Disponible en inventaire"
4. Sauvegarder

### 2. Vérifier l'Effet dans le PoS

1. Ouvrir le Point de Vente
2. Vérifier que le produit non disponible n'apparaît plus dans la liste des produits
3. Si une session PoS est déjà ouverte, elle sera automatiquement rechargée

### 3. Vérifier dans les Missions

1. Aller dans **Fidélité** > **Missions**
2. Créer ou modifier une mission avec condition "ACHAT_PRODUIT"
3. Vérifier que seuls les produits disponibles apparaissent dans la sélection

## Problèmes Connus

1. **Cache du Frontend** : Le frontend PoS peut mettre en cache les produits
2. **Méthodes Non Surchargées** : Certaines méthodes du PoS peuvent ne pas être surchargées
3. **Rechargement Manuel** : Il peut être nécessaire de recharger manuellement le PoS

## Solutions de Contournement

### 1. Rechargement Manuel

Si le produit reste visible dans le PoS :
1. Fermer la session PoS
2. Rouvrir le PoS
3. Vérifier que le produit n'apparaît plus

### 2. Vérification des Logs

Vérifier les logs pour s'assurer que les méthodes sont bien appelées :
```bash
docker-compose logs web | grep "DISPO_POS"
```

### 3. Test Direct

Utiliser le script de test pour vérifier le bon fonctionnement :
```bash
python3 addons/take_a_way_loyalty/scripts/test_direct.py
```

## Avantages

1. **Contrôle Granulaire**: Possibilité de contrôler la disponibilité produit par produit
2. **Automatisation**: Filtrage automatique dans tous les contextes PoS
3. **Cohérence**: Même logique appliquée dans les missions de fidélité
4. **Simplicité**: Interface utilisateur claire et intuitive
5. **Rechargement Automatique**: Les sessions PoS se rechargent automatiquement quand la disponibilité change

## Limitations

- Le filtrage s'applique uniquement au niveau du PoS et des missions de fidélité
- Les produits non disponibles restent visibles dans d'autres modules (ventes, achats, etc.)
- Aucun historique des changements de disponibilité n'est conservé
- Le rechargement des sessions PoS peut prendre quelques secondes
- Le cache du frontend peut nécessiter un rechargement manuel 