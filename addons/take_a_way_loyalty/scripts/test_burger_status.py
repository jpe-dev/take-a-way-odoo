#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script simple pour vérifier le statut du Bacon Burger
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

def test_burger_status():
    """Test du statut du Bacon Burger"""
    
    try:
        # Connexion à Odoo
        common = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/common')
        uid = common.authenticate(ODOO_DB, ODOO_USERNAME, ODOO_PASSWORD, {})
        
        if not uid:
            logger.error("Échec de l'authentification")
            return False
        
        models = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/object')
        
        logger.info("=== Vérification du statut du Bacon Burger ===")
        
        # Rechercher le Bacon Burger
        burger_product = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'product.product', 'search_read', 
                                         [[('name', '=', 'Bacon Burger')]], 
                                         {'fields': ['name', 'product_tmpl_id', 'pos_categ_id']})
        
        if burger_product:
            burger = burger_product[0]
            logger.info(f"Produit trouvé: {burger['name']}")
            
            # Récupérer le template du produit
            template_id = burger['product_tmpl_id'][0]
            template = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'product.template', 'read', 
                                       [template_id], {'fields': ['name', 'disponibilite_inventaire']})
            
            if template:
                logger.info(f"Template: {template[0]['name']}")
                logger.info(f"Disponibilité template: {template[0].get('disponibilite_inventaire', 'Non défini')}")
        
        # Rechercher tous les produits avec disponibilite_inventaire = True
        available_products = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'product.product', 'search_read', 
                                             [[('product_tmpl_id.disponibilite_inventaire', '=', True)]], 
                                             {'fields': ['name']})
        
        logger.info(f"Nombre total de produits disponibles: {len(available_products)}")
        
        # Vérifier si le Bacon Burger est dans la liste
        burger_in_list = any(p['name'] == 'Bacon Burger' for p in available_products)
        logger.info(f"Bacon Burger dans la liste des produits disponibles: {burger_in_list}")
        
        # Rechercher tous les produits (sans filtre)
        all_products = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'product.product', 'search_read', 
                                        [[]], {'fields': ['name', 'product_tmpl_id']})
        
        logger.info(f"Nombre total de produits: {len(all_products)}")
        
        # Vérifier si le Bacon Burger est dans la liste totale
        burger_in_all = any(p['name'] == 'Bacon Burger' for p in all_products)
        logger.info(f"Bacon Burger dans la liste totale des produits: {burger_in_all}")
        
        logger.info("=== Test terminé ===")
        return True
        
    except Exception as e:
        logger.error(f"Erreur générale: {e}")
        return False

if __name__ == "__main__":
    test_burger_status() 