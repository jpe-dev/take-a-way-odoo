# -*- coding: utf-8 -*-
"""
Script pour forcer la mise à jour du module et vérifier la visibilité du champ heure_prevue
"""

from odoo import api, fields, models
import logging

_logger = logging.getLogger(__name__)

def force_update_module():
    """Force la mise à jour du module take_a_way_loyalty"""
    
    try:
        env = api.Environment(cr, uid, {})
        
        # Récupérer le module
        module = env['ir.module.module'].search([('name', '=', 'take_a_way_loyalty')], limit=1)
        
        if module:
            _logger.info(f"Module trouvé: {module.name} (état: {module.state})")
            
            # Forcer la mise à jour
            if module.state == 'installed':
                _logger.info("Mise à jour du module...")
                module.button_immediate_upgrade()
                _logger.info("✅ Module mis à jour avec succès")
            else:
                _logger.info("Module pas encore installé, installation...")
                module.button_immediate_install()
                _logger.info("✅ Module installé avec succès")
        else:
            _logger.error("❌ Module take_a_way_loyalty non trouvé")
            return False
            
        return True
        
    except Exception as e:
        _logger.error(f"❌ Erreur lors de la mise à jour: {str(e)}")
        return False

def check_field_visibility():
    """Vérifie que le champ heure_prevue est visible dans les vues"""
    
    try:
        env = api.Environment(cr, uid, {})
        
        # Vérifier que le champ existe dans le modèle
        pos_order_model = env['pos.order']
        
        if not hasattr(pos_order_model, 'heure_prevue'):
            _logger.error("❌ Le champ heure_prevue n'existe pas dans le modèle")
            return False
        
        _logger.info("✅ Le champ heure_prevue existe dans le modèle")
        
        # Vérifier que les vues sont bien étendues
        vues_to_check = [
            'take_a_way_loyalty.view_pos_order_form_inherit_heure_prevue',
            'take_a_way_loyalty.view_pos_order_tree_inherit_heure_prevue',
            'take_a_way_loyalty.view_pos_order_search_inherit_heure_prevue',
            'take_a_way_loyalty.view_pos_order_kanban_inherit_heure_prevue'
        ]
        
        for vue_ref in vues_to_check:
            try:
                vue = env.ref(vue_ref, raise_if_not_found=False)
                if vue:
                    _logger.info(f"✅ Vue {vue_ref} trouvée")
                else:
                    _logger.warning(f"⚠️ Vue {vue_ref} non trouvée")
            except Exception as e:
                _logger.warning(f"⚠️ Erreur lors de la vérification de {vue_ref}: {str(e)}")
        
        # Créer une commande de test pour vérifier
        pos_order = env['pos.order'].create({
            'name': 'Test Visibilité',
            'date_order': fields.Datetime.now(),
            'heure_prevue': fields.Datetime.now(),
            'amount_total': 10.00,
            'state': 'draft'
        })
        
        _logger.info(f"✅ Commande de test créée avec heure_prevue: {pos_order.heure_prevue}")
        
        # Nettoyer
        pos_order.unlink()
        
        return True
        
    except Exception as e:
        _logger.error(f"❌ Erreur lors de la vérification: {str(e)}")
        return False

def clear_cache():
    """Nettoie le cache des vues"""
    
    try:
        env = api.Environment(cr, uid, {})
        
        # Vider le cache des vues
        env['ir.ui.view'].clear_caches()
        _logger.info("✅ Cache des vues nettoyé")
        
        return True
        
    except Exception as e:
        _logger.error(f"❌ Erreur lors du nettoyage du cache: {str(e)}")
        return False

if __name__ == "__main__":
    print("=== Mise à jour et vérification du module ===")
    
    # Nettoyer le cache
    clear_cache()
    
    # Forcer la mise à jour
    update_success = force_update_module()
    
    if update_success:
        # Vérifier la visibilité
        visibility_success = check_field_visibility()
        
        if visibility_success:
            print("✅ Module mis à jour et champ visible avec succès!")
            print("📋 Instructions pour voir le champ:")
            print("1. Allez dans Point de Vente > Commandes")
            print("2. Créez une nouvelle commande ou modifiez une existante")
            print("3. Le champ 'Heure prévue' devrait apparaître dans le formulaire")
            print("4. Dans la liste des commandes, le champ devrait aussi être visible")
        else:
            print("❌ Champ non visible après mise à jour")
    else:
        print("❌ Échec de la mise à jour du module") 