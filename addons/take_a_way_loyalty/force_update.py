# -*- coding: utf-8 -*-
"""
Script pour forcer la mise à jour du module take_a_way_loyalty
"""

from odoo import api, fields, models
import logging

_logger = logging.getLogger(__name__)

def force_update_module():
    """Force la mise à jour du module"""
    
    try:
        # Récupérer l'environnement Odoo
        env = api.Environment(cr, uid, {})
        
        # Récupérer le module
        module = env['ir.module.module'].search([
            ('name', '=', 'take_a_way_loyalty')
        ], limit=1)
        
        if not module:
            print("❌ Module take_a_way_loyalty non trouvé")
            return False
        
        print(f"✅ Module trouvé: {module.name} (état: {module.state})")
        
        # Forcer la mise à jour
        if module.state == 'installed':
            print("🔄 Mise à jour du module...")
            module.button_immediate_upgrade()
        elif module.state == 'uninstalled':
            print("📦 Installation du module...")
            module.button_immediate_install()
        else:
            print(f"ℹ️ Module dans l'état: {module.state}")
        
        # Vérifier que les modèles sont créés
        models_to_check = [
            'add.participant.wizard',
            'parrainage.wizard',
            'heure.prevue.wizard'
        ]
        
        for model_name in models_to_check:
            model = env['ir.model'].search([('model', '=', model_name)], limit=1)
            if model:
                print(f"✅ Modèle {model_name} créé")
            else:
                print(f"❌ Modèle {model_name} non trouvé")
        
        # Vérifier les permissions
        access_records = env['ir.model.access'].search([
            ('name', 'in', ['add.participant.wizard', 'parrainage.wizard', 'heure.prevue.wizard'])
        ])
        
        print(f"✅ {len(access_records)} enregistrements de permissions trouvés")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de la mise à jour: {str(e)}")
        return False

if __name__ == "__main__":
    print("=== Force Update du module take_a_way_loyalty ===")
    
    success = force_update_module()
    
    if success:
        print("✅ Mise à jour forcée terminée!")
        print("📋 Redémarrez Odoo pour appliquer les changements")
    else:
        print("❌ Échec de la mise à jour forcée") 