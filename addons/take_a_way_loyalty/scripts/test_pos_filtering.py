#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script de test pour vérifier le filtrage des produits dans le PoS
"""

import xmlrpc.client
import logging

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration de la connexion Odoo
ODOO_URL = "http://localhost:8069"
ODOO_DB = "db-odoo-ta"
ODOO_USERNAME = "admin"
ODOO_PASSWORD = "admin"

def test_pos_filtering():
    """Test du filtrage des produits dans le PoS"""
    
    try:
        # Connexion à Odoo
        common = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/common')
        uid = common.authenticate(ODOO_DB, ODOO_USERNAME, ODOO_PASSWORD, {})
        
        if not uid:
            logger.error("Échec de l'authentification")
            return False
        
        models = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/object')
        
        logger.info("=== Test du filtrage des produits dans le PoS ===")
        
        # 1. Vérifier l'état du produit "Bacon Burger"
        burger_product = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'product.product', 'search_read', 
                                         [[('name', '=', 'Bacon Burger')]], 
                                         {'fields': ['name', 'product_tmpl_id', 'disponibilite_inventaire']})
        
        if burger_product:
            burger = burger_product[0]
            logger.info(f"Produit trouvé: {burger['name']}")
            logger.info(f"Disponibilité: {burger.get('disponibilite_inventaire', 'Non défini')}")
            
            # Récupérer le template du produit
            template_id = burger['product_tmpl_id'][0]
            template = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'product.template', 'read', 
                                       [template_id], {'fields': ['name', 'disponibilite_inventaire']})
            
            if template:
                logger.info(f"Template: {template[0]['name']}")
                logger.info(f"Disponibilité template: {template[0].get('disponibilite_inventaire', 'Non défini')}")
        
        # 2. Tester la méthode _get_pos_products_domain sur ProductTemplate
        logger.info("\n=== Test ProductTemplate._get_pos_products_domain ===")
        try:
            domain = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'product.template', '_get_pos_products_domain', [])
            logger.info(f"Domaine retourné: {domain}")
        except Exception as e:
            logger.error(f"Erreur lors de l'appel à _get_pos_products_domain: {e}")
        
        # 3. Tester la méthode _get_pos_products sur ProductTemplate
        logger.info("\n=== Test ProductTemplate._get_pos_products ===")
        try:
            products = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'product.template', '_get_pos_products', [])
            logger.info(f"Nombre de produits retournés: {len(products)}")
            if products:
                logger.info(f"Premier produit: {products[0]}")
        except Exception as e:
            logger.error(f"Erreur lors de l'appel à _get_pos_products: {e}")
        
        # 4. Tester la méthode _get_pos_products_domain sur ProductProduct
        logger.info("\n=== Test ProductProduct._get_pos_products_domain ===")
        try:
            domain = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'product.product', '_get_pos_products_domain', [])
            logger.info(f"Domaine retourné: {domain}")
        except Exception as e:
            logger.error(f"Erreur lors de l'appel à _get_pos_products_domain: {e}")
        
        # 5. Tester la méthode _get_pos_products sur ProductProduct
        logger.info("\n=== Test ProductProduct._get_pos_products ===")
        try:
            products = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'product.product', '_get_pos_products', [])
            logger.info(f"Nombre de produits retournés: {len(products)}")
            if products:
                logger.info(f"Premier produit: {products[0]}")
        except Exception as e:
            logger.error(f"Erreur lors de l'appel à _get_pos_products: {e}")
        
        # 6. Tester la méthode _get_available_products sur PosConfig
        logger.info("\n=== Test PosConfig._get_available_products ===")
        try:
            # Récupérer la première configuration PoS
            pos_configs = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'pos.config', 'search_read', 
                                          [[]], {'fields': ['name']})
            if pos_configs:
                config_id = pos_configs[0]['id']
                logger.info(f"Test avec la config PoS: {pos_configs[0]['name']}")
                
                products = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'pos.config', '_get_available_products', 
                                           [config_id])
                logger.info(f"Nombre de produits retournés: {len(products)}")
                if products:
                    logger.info(f"Premier produit: {products[0]}")
        except Exception as e:
            logger.error(f"Erreur lors de l'appel à _get_available_products: {e}")
        
        # 7. Tester la méthode _get_products_domain sur PosConfig
        logger.info("\n=== Test PosConfig._get_products_domain ===")
        try:
            domain = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'pos.config', '_get_products_domain', [config_id])
            logger.info(f"Domaine retourné: {domain}")
        except Exception as e:
            logger.error(f"Erreur lors de l'appel à _get_products_domain: {e}")
        
        # 8. Rechercher directement les produits avec le filtre de disponibilité
        logger.info("\n=== Test recherche directe avec filtre de disponibilité ===")
        try:
            products = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'product.product', 'search_read', 
                                       [[('product_tmpl_id.disponibilite_inventaire', '=', True)]], 
                                       {'fields': ['name', 'product_tmpl_id']})
            logger.info(f"Nombre de produits disponibles: {len(products)}")
            
            # Vérifier si le Bacon Burger est dans la liste
            burger_in_list = any(p['name'] == 'Bacon Burger' for p in products)
            logger.info(f"Bacon Burger dans la liste des produits disponibles: {burger_in_list}")
            
        except Exception as e:
            logger.error(f"Erreur lors de la recherche directe: {e}")
        
        logger.info("\n=== Test terminé ===")
        return True
        
    except Exception as e:
        logger.error(f"Erreur générale: {e}")
        return False

if __name__ == "__main__":
    test_pos_filtering() 