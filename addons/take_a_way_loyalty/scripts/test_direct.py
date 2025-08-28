#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script pour tester directement la disponibilité des produits dans le PoS via l'API Odoo
"""

import xmlrpc.client
import logging

# Configuration de logging
logging.basicConfig(level=logging.INFO)
_logger = logging.getLogger(__name__)

def test_disponibilite_direct():
    """Test direct de la disponibilité des produits via l'API Odoo"""
    
    try:
        # Connexion à Odoo
        url = "http://localhost:8069"
        db = "db-odoo-ta"
        username = "admin"
        password = "admin"
        
        _logger.info("Connexion à Odoo...")
        common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
        uid = common.authenticate(db, username, password, {})
        
        if not uid:
            _logger.error("Échec de l'authentification")
            return
        
        _logger.info(f"Authentification réussie, UID: {uid}")
        
        models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))
        
        # 1. Récupérer tous les produits
        products = models.execute_kw(db, uid, password, 'product.product', 'search_read', [[]], {
            'fields': ['id', 'name', 'product_tmpl_id']
        })
        _logger.info(f"Nombre total de produits: {len(products)}")
        
        # 2. Récupérer les templates de produits avec le champ disponibilite_inventaire
        product_templates = models.execute_kw(db, uid, password, 'product.template', 'search_read', [[]], {
            'fields': ['id', 'name', 'disponibilite_inventaire']
        })
        _logger.info(f"Nombre de templates de produits: {len(product_templates)}")
        
        # 3. Compter les produits disponibles et non disponibles
        available_templates = [pt for pt in product_templates if pt.get('disponibilite_inventaire', True)]
        unavailable_templates = [pt for pt in product_templates if not pt.get('disponibilite_inventaire', True)]
        
        _logger.info(f"Templates disponibles: {len(available_templates)}")
        _logger.info(f"Templates non disponibles: {len(unavailable_templates)}")
        
        # 4. Tester la méthode _get_pos_products
        try:
            pos_products = models.execute_kw(db, uid, password, 'product.product', '_get_pos_products', [])
            _logger.info(f"Produits retournés par _get_pos_products: {len(pos_products)}")
        except Exception as e:
            _logger.error(f"Erreur lors de l'appel à _get_pos_products: {str(e)}")
        
        # 5. Tester avec une configuration PoS
        pos_configs = models.execute_kw(db, uid, password, 'pos.config', 'search_read', [[]], {
            'fields': ['id', 'name']
        })
        
        if pos_configs:
            pos_config = pos_configs[0]
            _logger.info(f"Test avec la configuration PoS: {pos_config['name']}")
            
            try:
                available_in_pos = models.execute_kw(db, uid, password, 'pos.config', '_get_available_products', [pos_config['id']])
                _logger.info(f"Produits disponibles dans le PoS: {len(available_in_pos)}")
            except Exception as e:
                _logger.error(f"Erreur lors de l'appel à _get_available_products: {str(e)}")
        
        # 6. Test spécifique pour le produit "Bacon Burger"
        bacon_burger = models.execute_kw(db, uid, password, 'product.product', 'search_read', [[('name', '=', 'Bacon Burger')]], {
            'fields': ['id', 'name', 'product_tmpl_id']
        })
        
        if bacon_burger:
            burger = bacon_burger[0]
            _logger.info(f"Test spécifique pour Bacon Burger (ID: {burger['id']})")
            
            # Récupérer le template du burger
            template = models.execute_kw(db, uid, password, 'product.template', 'read', [burger['product_tmpl_id'][0]], {
                'fields': ['disponibilite_inventaire']
            })
            
            if template:
                disponibilite = template[0].get('disponibilite_inventaire', True)
                _logger.info(f"Disponibilité actuelle du Bacon Burger: {disponibilite}")
                
                if not disponibilite:
                    _logger.info("✅ Bacon Burger est marqué comme non disponible")
                else:
                    _logger.info("❌ Bacon Burger est marqué comme disponible")
        
        _logger.info("=== Test terminé ===")
        
    except Exception as e:
        _logger.error(f"Erreur générale: {str(e)}")
        import traceback
        _logger.error(f"Traceback: {traceback.format_exc()}")

if __name__ == "__main__":
    test_disponibilite_direct() 