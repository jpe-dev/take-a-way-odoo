# -*- coding: utf-8 -*-
"""
Script pour vérifier les actions dans la base de données
"""

from odoo import api, fields, models
import logging

_logger = logging.getLogger(__name__)

def check_actions():
    """Vérifie les actions dans la base de données"""
    
    try:
        # Récupérer l'environnement Odoo
        env = api.Environment(cr, uid, {})
        
        print("=== Vérification des actions heure prévue ===")
        print("")
        
        # 1. Vérifier les actions serveur
        print("1. Actions serveur trouvées:")
        actions = env['ir.actions.server'].search([
            ('name', 'like', '%heure%')
        ])
        
        print(f"   Nombre d'actions: {len(actions)}")
        for action in actions:
            print(f"   - {action.name} (ID: {action.id})")
            print(f"     Modèle: {action.model_id.name}")
            print(f"     Binding: {action.binding_model_id.name if action.binding_model_id else 'Aucun'}")
            print(f"     View types: {action.binding_view_types}")
            print(f"     Actif: {action.active}")
            print("")
        
        # 2. Vérifier spécifiquement les actions pour pos.order
        print("2. Actions pour pos.order:")
        pos_actions = env['ir.actions.server'].search([
            ('model_id.model', '=', 'pos.order'),
            ('binding_model_id.model', '=', 'pos.order')
        ])
        
        print(f"   Nombre d'actions pos.order: {len(pos_actions)}")
        for action in pos_actions:
            print(f"   - {action.name} (ID: {action.id})")
            print(f"     Binding view types: {action.binding_view_types}")
            print(f"     Actif: {action.active}")
            print("")
        
        # 3. Vérifier le modèle pos.order
        print("3. Modèle pos.order:")
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
        
        if hasattr(pos_order_model, 'action_clear_heure_prevue'):
            print("   ✅ Action action_clear_heure_prevue existe")
        else:
            print("   ❌ Action action_clear_heure_prevue n'existe pas")
        
        print("")
        
        # 4. Suggestions
        print("4. Suggestions:")
        if len(actions) == 0:
            print("   ❌ Aucune action trouvée. Le fichier XML n'a pas été chargé correctement.")
        elif len(pos_actions) == 0:
            print("   ❌ Aucune action pour pos.order trouvée.")
        else:
            print("   ✅ Actions trouvées. Vérifiez que:")
            print("      - Vous êtes dans la bonne vue (form)")
            print("      - Vous avez les bonnes permissions")
            print("      - Le cache du navigateur est vidé")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de la vérification: {str(e)}")
        return False

if __name__ == "__main__":
    success = check_actions()
    
    if success:
        print("✅ Vérification terminée!")
    else:
        print("❌ Vérification échouée!") 