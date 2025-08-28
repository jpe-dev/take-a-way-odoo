# -*- coding: utf-8 -*-
"""
Script de vérification pour le champ heure_prevue dans les commandes PoS
"""

from odoo import api, fields, models
from datetime import datetime, timedelta
import logging

_logger = logging.getLogger(__name__)

def test_heure_prevue_verification():
    """Test de vérification pour le champ heure_prevue"""
    
    try:
        # Récupérer l'environnement Odoo
        env = api.Environment(cr, uid, {})
        
        # Vérifier si le champ existe dans le modèle
        pos_order_model = env['pos.order']
        
        if hasattr(pos_order_model, 'heure_prevue'):
            _logger.info("✅ Le champ heure_prevue existe dans le modèle pos.order")
        else:
            _logger.error("❌ Le champ heure_prevue n'existe pas dans le modèle pos.order")
            return False
        
        # Vérifier si le champ est accessible
        try:
            # Créer une commande PoS de test
            pos_order = env['pos.order'].create({
                'name': 'Test Heure Prévue Verification',
                'date_order': fields.Datetime.now(),
                'heure_prevue': fields.Datetime.now() + timedelta(hours=1),
                'amount_total': 25.00,
                'state': 'draft'
            })
            
            _logger.info("✅ Commande PoS créée avec succès")
            _logger.info(f"  - ID: {pos_order.id}")
            _logger.info(f"  - Nom: {pos_order.name}")
            _logger.info(f"  - Heure prévue: {pos_order.heure_prevue}")
            
            # Vérifier que le champ peut être modifié
            pos_order.write({
                'heure_prevue': fields.Datetime.now() + timedelta(hours=2)
            })
            
            _logger.info("✅ Le champ heure_prevue peut être modifié")
            _logger.info(f"  - Nouvelle heure prévue: {pos_order.heure_prevue}")
            
            # Vérifier que le champ peut être lu
            heure_prevue = pos_order.heure_prevue
            _logger.info("✅ Le champ heure_prevue peut être lu")
            _logger.info(f"  - Valeur lue: {heure_prevue}")
            
            # Nettoyer - supprimer la commande de test
            pos_order.unlink()
            _logger.info("✅ Commande de test supprimée")
            
            return True
            
        except Exception as e:
            _logger.error(f"❌ Erreur lors du test: {str(e)}")
            return False
            
    except Exception as e:
        _logger.error(f"❌ Erreur lors de l'initialisation: {str(e)}")
        return False

def test_vue_pos_order():
    """Test pour vérifier que les vues PoS sont bien étendues"""
    
    try:
        env = api.Environment(cr, uid, {})
        
        # Vérifier que les vues existent
        vue_form = env.ref('take_a_way_loyalty.view_pos_order_form_inherit_heure_prevue', raise_if_not_found=False)
        vue_tree = env.ref('take_a_way_loyalty.view_pos_order_tree_inherit_heure_prevue', raise_if_not_found=False)
        vue_search = env.ref('take_a_way_loyalty.view_pos_order_search_inherit_heure_prevue', raise_if_not_found=False)
        
        if vue_form:
            _logger.info("✅ Vue formulaire PoS étendue trouvée")
        else:
            _logger.error("❌ Vue formulaire PoS étendue non trouvée")
            
        if vue_tree:
            _logger.info("✅ Vue liste PoS étendue trouvée")
        else:
            _logger.error("❌ Vue liste PoS étendue non trouvée")
            
        if vue_search:
            _logger.info("✅ Vue recherche PoS étendue trouvée")
        else:
            _logger.error("❌ Vue recherche PoS étendue non trouvée")
            
        return vue_form and vue_tree and vue_search
        
    except Exception as e:
        _logger.error(f"❌ Erreur lors du test des vues: {str(e)}")
        return False

if __name__ == "__main__":
    print("=== Test de vérification du champ heure_prevue ===")
    
    # Test du champ
    test_champ = test_heure_prevue_verification()
    
    # Test des vues
    test_vues = test_vue_pos_order()
    
    if test_champ and test_vues:
        print("✅ Tous les tests sont passés avec succès!")
    else:
        print("❌ Certains tests ont échoué") 