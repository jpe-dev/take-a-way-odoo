#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script de test pour vérifier la fonctionnalité de disponibilité des produits dans le PoS
"""

import logging
from odoo import api, fields, models

_logger = logging.getLogger(__name__)

def test_disponibilite_pos():
    """Test de la fonctionnalité de disponibilité des produits dans le PoS"""
    
    # Récupérer l'environnement Odoo
    env = api.Environment.manage()
    
    try:
        _logger.info("=== Test de disponibilité des produits dans le PoS ===")
        
        # 1. Récupérer tous les produits
        products = env['product.product'].search([])
        _logger.info(f"Nombre total de produits: {len(products)}")
        
        # 2. Compter les produits disponibles et non disponibles
        available_products = products.filtered(lambda p: p.product_tmpl_id.disponibilite_inventaire)
        unavailable_products = products.filtered(lambda p: not p.product_tmpl_id.disponibilite_inventaire)
        
        _logger.info(f"Produits disponibles: {len(available_products)}")
        _logger.info(f"Produits non disponibles: {len(unavailable_products)}")
        
        # 3. Tester la méthode _get_pos_products_domain
        domain = env['product.template']._get_pos_products_domain()
        _logger.info(f"Domaine de filtrage: {domain}")
        
        # 4. Tester la méthode _get_pos_products
        pos_products = env['product.template']._get_pos_products()
        _logger.info(f"Produits retournés par _get_pos_products: {len(pos_products)}")
        
        # 5. Vérifier que seuls les produits disponibles sont retournés
        if len(pos_products) == len(available_products):
            _logger.info("✅ Test réussi: Seuls les produits disponibles sont retournés")
        else:
            _logger.error("❌ Test échoué: Nombre de produits incorrect")
        
        # 6. Tester avec une configuration PoS spécifique
        pos_configs = env['pos.config'].search([])
        if pos_configs:
            pos_config = pos_configs[0]
            _logger.info(f"Test avec la configuration PoS: {pos_config.name}")
            
            # Tester _get_available_products
            available_in_pos = pos_config._get_available_products()
            _logger.info(f"Produits disponibles dans le PoS: {len(available_in_pos)}")
            
            # Tester _get_products_domain
            products_domain = pos_config._get_products_domain()
            _logger.info(f"Domaine des produits du PoS: {products_domain}")
            
            # Vérifier que les produits non disponibles ne sont pas dans la liste
            unavailable_in_pos = available_in_pos.filtered(lambda p: not p.product_tmpl_id.disponibilite_inventaire)
            if not unavailable_in_pos:
                _logger.info("✅ Test réussi: Aucun produit non disponible dans le PoS")
            else:
                _logger.error(f"❌ Test échoué: {len(unavailable_in_pos)} produits non disponibles trouvés dans le PoS")
        
        # 7. Tester les nouvelles méthodes de session PoS
        pos_sessions = env['pos.session'].search([('state', '=', 'opened')])
        if pos_sessions:
            session = pos_sessions[0]
            _logger.info(f"Test avec la session PoS: {session.name}")
            
            # Tester _loader_params_product_product
            try:
                loader_params = session._loader_params_product_product()
                _logger.info(f"Paramètres de chargement des produits: {loader_params}")
                
                if 'domain' in loader_params:
                    domain_filter = [('product_tmpl_id.disponibilite_inventaire', '=', True)]
                    if domain_filter in loader_params['domain']:
                        _logger.info("✅ Test réussi: Filtre de disponibilité présent dans les paramètres de chargement")
                    else:
                        _logger.error("❌ Test échoué: Filtre de disponibilité absent des paramètres de chargement")
                else:
                    _logger.warning("⚠️ Aucun domaine trouvé dans les paramètres de chargement")
            except Exception as e:
                _logger.error(f"❌ Erreur lors du test des paramètres de chargement: {str(e)}")
            
            # Tester _get_pos_products_domain
            try:
                session_domain = session._get_pos_products_domain()
                _logger.info(f"Domaine des produits de la session: {session_domain}")
                
                domain_filter = [('product_tmpl_id.disponibilite_inventaire', '=', True)]
                if domain_filter in session_domain:
                    _logger.info("✅ Test réussi: Filtre de disponibilité présent dans le domaine de la session")
                else:
                    _logger.error("❌ Test échoué: Filtre de disponibilité absent du domaine de la session")
            except Exception as e:
                _logger.error(f"❌ Erreur lors du test du domaine de la session: {str(e)}")
            
            # Tester _load_model_data
            try:
                _logger.info("Test de _load_model_data pour product.product")
                # Cette méthode est appelée lors du chargement des données
                session._load_model_data('product.product')
                _logger.info("✅ Test réussi: _load_model_data appelée sans erreur")
            except Exception as e:
                _logger.error(f"❌ Erreur lors du test de _load_model_data: {str(e)}")
        
        # 8. Test de modification d'un produit
        if products:
            test_product = products[0]
            _logger.info(f"Test avec le produit: {test_product.name}")
            
            # Marquer le produit comme non disponible
            original_status = test_product.product_tmpl_id.disponibilite_inventaire
            test_product.product_tmpl_id.disponibilite_inventaire = False
            
            # Vérifier qu'il n'apparaît plus dans les produits du PoS
            pos_products_after = env['product.template']._get_pos_products()
            if test_product not in pos_products_after:
                _logger.info("✅ Test réussi: Le produit non disponible n'apparaît plus dans le PoS")
            else:
                _logger.error("❌ Test échoué: Le produit non disponible apparaît encore dans le PoS")
            
            # Remettre le statut original
            test_product.product_tmpl_id.disponibilite_inventaire = original_status
        
        # 9. Test des méthodes du modèle ProductProduct
        try:
            product_domain = env['product.product']._get_pos_products_domain()
            _logger.info(f"Domaine des produits (ProductProduct): {product_domain}")
            
            product_pos_products = env['product.product']._get_pos_products()
            _logger.info(f"Produits retournés par ProductProduct._get_pos_products: {len(product_pos_products)}")
            
            # Vérifier que seuls les produits disponibles sont retournés
            if len(product_pos_products) == len(available_products):
                _logger.info("✅ Test réussi: ProductProduct._get_pos_products retourne les bons produits")
            else:
                _logger.error("❌ Test échoué: ProductProduct._get_pos_products retourne un nombre incorrect de produits")
        except Exception as e:
            _logger.error(f"❌ Erreur lors du test des méthodes ProductProduct: {str(e)}")
        
        # 10. Test spécifique pour le produit "Bacon Burger"
        bacon_burger = env['product.product'].search([('name', '=', 'Bacon Burger')])
        if bacon_burger:
            _logger.info(f"Test spécifique pour Bacon Burger (ID: {bacon_burger.id})")
            _logger.info(f"Disponibilité actuelle: {bacon_burger.product_tmpl_id.disponibilite_inventaire}")
            
            # Vérifier s'il apparaît dans les produits du PoS
            pos_products_bacon = env['product.product']._get_pos_products()
            if bacon_burger in pos_products_bacon:
                _logger.info("✅ Bacon Burger apparaît dans les produits du PoS")
            else:
                _logger.info("❌ Bacon Burger n'apparaît pas dans les produits du PoS")
        
        _logger.info("=== Fin des tests ===")
        
    except Exception as e:
        _logger.error(f"❌ Erreur générale lors des tests: {str(e)}")
        import traceback
        _logger.error(f"Traceback: {traceback.format_exc()}")

if __name__ == "__main__":
    test_disponibilite_pos() 