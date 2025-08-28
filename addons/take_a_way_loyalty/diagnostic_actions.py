# -*- coding: utf-8 -*-
"""
Script de diagnostic pour vérifier les actions créées
"""

from odoo import api, fields, models
import logging

_logger = logging.getLogger(__name__)

def diagnostic_actions():
    """Diagnostic des actions créées"""
    
    try:
        # Récupérer l'environnement Odoo
        env = api.Environment(cr, uid, {})
        
        print("=== Diagnostic des actions heure prévue ===")
        print("")
        
        # 1. Vérifier les actions serveur
        print("1. Vérification des actions serveur...")
        actions = env['ir.actions.server'].search([
            ('name', 'like', '%heure%')
        ])
        
        print(f"   Actions trouvées: {len(actions)}")
        for action in actions:
            print(f"   - {action.name} (ID: {action.id})")
            print(f"     Modèle: {action.model_id.name}")
            print(f"     Binding: {action.binding_model_id.name if action.binding_model_id else 'Aucun'}")
            print(f"     View types: {action.binding_view_types}")
            print("")
        
        # 2. Vérifier les actions window
        print("2. Vérification des actions window...")
        window_actions = env['ir.actions.act_window'].search([
            ('name', 'like', '%heure%')
        ])
        
        print(f"   Actions window trouvées: {len(window_actions)}")
        for action in window_actions:
            print(f"   - {action.name} (ID: {action.id})")
            print(f"     Modèle: {action.res_model}")
            print("")
        
        # 3. Vérifier le modèle pos.order
        print("3. Vérification du modèle pos.order...")
        pos_order_model = env['pos.order']
        
        if hasattr(pos_order_model, 'heure_prevue'):
            print("   ✅ Champ heure_prevue existe")
        else:
            print("   ❌ Champ heure_prevue n'existe pas")
        
        if hasattr(pos_order_model, 'action_set_heure_prevue'):
            print("   ✅ Action action_set_heure_prevue existe")
        else:
            print("   ❌ Action action_set_heure_prevue n'existe pas")
        
        if hasattr(pos_order_model, 'action_set_heure_prevue_rapide'):
            print("   ✅ Action action_set_heure_prevue_rapide existe")
        else:
            print("   ❌ Action action_set_heure_prevue_rapide n'existe pas")
        
        print("")
        
        # 4. Vérifier le wizard
        print("4. Vérification du wizard...")
        wizard_model = env['ir.model'].search([('model', '=', 'heure.prevue.wizard')], limit=1)
        if wizard_model:
            print("   ✅ Modèle heure.prevue.wizard existe")
        else:
            print("   ❌ Modèle heure.prevue.wizard n'existe pas")
        
        # 5. Vérifier les permissions
        print("5. Vérification des permissions...")
        access_records = env['ir.model.access'].search([
            ('name', 'like', '%heure%')
        ])
        
        print(f"   Permissions trouvées: {len(access_records)}")
        for access in access_records:
            print(f"   - {access.name} pour {access.model_id.name}")
        
        print("")
        
        # 6. Suggestions
        print("6. Suggestions...")
        if len(actions) == 0:
            print("   ❌ Aucune action trouvée. Vérifiez que le fichier pos_actions_data.xml a été chargé.")
        else:
            print("   ✅ Actions trouvées. Vérifiez que:")
            print("      - Les actions ont le bon binding_model_id")
            print("      - Les actions ont le bon binding_view_types")
            print("      - Le module a été mis à jour")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors du diagnostic: {str(e)}")
        return False

if __name__ == "__main__":
    success = diagnostic_actions()
    
    if success:
        print("✅ Diagnostic terminé!")
    else:
        print("❌ Diagnostic échoué!") 