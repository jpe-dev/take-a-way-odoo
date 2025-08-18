# -*- coding: utf-8 -*-
"""
Script pour forcer la création des actions heure prévue
"""

from odoo import api, fields, models
import logging

_logger = logging.getLogger(__name__)

def force_create_actions():
    """Force la création des actions heure prévue"""
    
    try:
        # Récupérer l'environnement Odoo
        env = api.Environment(cr, uid, {})
        
        print("=== Création forcée des actions heure prévue ===")
        print("")
        
        # Créer les actions
        result = env['pos.order']._create_heure_prevue_actions()
        
        if result:
            print("✅ Actions créées avec succès!")
        else:
            print("❌ Erreur lors de la création des actions")
            return False
        
        # Vérifier que les actions ont été créées
        actions = env['ir.actions.server'].search([
            ('name', 'like', '%heure%'),
            ('model_id.model', '=', 'pos.order')
        ])
        
        print(f"✅ {len(actions)} actions trouvées:")
        for action in actions:
            print(f"   - {action.name} (ID: {action.id})")
            print(f"     Binding: {action.binding_model_id.name if action.binding_model_id else 'Aucun'}")
            print(f"     View types: {action.binding_view_types}")
        
        print("")
        print("📋 Instructions:")
        print("1. Allez dans Point de Vente > Commandes")
        print("2. Sélectionnez une commande")
        print("3. Cliquez sur Actions dans la barre d'outils")
        print("4. Vous devriez voir les actions heure prévue")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de la création des actions: {str(e)}")
        return False

if __name__ == "__main__":
    success = force_create_actions()
    
    if success:
        print("✅ Actions créées avec succès!")
    else:
        print("❌ Échec de la création des actions") 