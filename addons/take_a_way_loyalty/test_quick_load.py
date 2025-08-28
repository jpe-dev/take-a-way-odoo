# -*- coding: utf-8 -*-
"""
Test rapide pour vérifier que le module se charge correctement
"""

from odoo import api, fields, models
import logging

_logger = logging.getLogger(__name__)

def test_module_load():
    """Test rapide pour vérifier que le module se charge"""
    
    try:
        # Récupérer l'environnement Odoo
        env = api.Environment(cr, uid, {})
        
        # Vérifier que les modèles existent
        models_to_check = [
            'heure.prevue.wizard',
            'add.participant.wizard',
            'parrainage.wizard'
        ]
        
        for model_name in models_to_check:
            model = env['ir.model'].search([('model', '=', model_name)], limit=1)
            if model:
                print(f"✅ Modèle {model_name} créé")
            else:
                print(f"❌ Modèle {model_name} non trouvé")
        
        # Vérifier que le champ heure_prevue existe dans pos.order
        pos_order_model = env['pos.order']
        if hasattr(pos_order_model, 'heure_prevue'):
            print("✅ Champ heure_prevue existe dans pos.order")
        else:
            print("❌ Champ heure_prevue n'existe pas dans pos.order")
        
        # Vérifier les actions serveur
        actions = env['ir.actions.server'].search([
            ('name', 'in', ['Heure prévue +1h', 'Définir heure prévue'])
        ])
        
        print(f"✅ {len(actions)} actions serveur trouvées")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors du test: {str(e)}")
        return False

if __name__ == "__main__":
    print("=== Test rapide du module take_a_way_loyalty ===")
    
    success = test_module_load()
    
    if success:
        print("✅ Module chargé avec succès!")
    else:
        print("❌ Échec du chargement du module") 