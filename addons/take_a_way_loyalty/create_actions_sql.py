# -*- coding: utf-8 -*-
"""
Script pour créer les actions via SQL direct
"""

from odoo import api, fields, models
import logging

_logger = logging.getLogger(__name__)

def create_actions_sql():
    """Crée les actions via SQL direct"""
    
    try:
        # Récupérer l'environnement Odoo
        env = api.Environment(cr, uid, {})
        
        print("=== Création des actions via SQL ===")
        
        # Récupérer le modèle pos.order
        pos_order_model = env['ir.model'].search([('model', '=', 'pos.order')], limit=1)
        
        if not pos_order_model:
            print("❌ Modèle pos.order non trouvé")
            return False
        
        print(f"✅ Modèle pos.order trouvé (ID: {pos_order_model.id})")
        
        # Supprimer les anciennes actions
        old_actions = env['ir.actions.server'].search([
            ('name', 'like', '%heure%'),
            ('model_id.model', '=', 'pos.order')
        ])
        if old_actions:
            old_actions.unlink()
            print("✅ Anciennes actions supprimées")
        
        # Créer les nouvelles actions
        actions_data = [
            {
                'name': 'Définir heure prévue',
                'code': 'if records:\n    records.action_set_heure_prevue()'
            },
            {
                'name': 'Heure prévue +1h',
                'code': 'if records:\n    records.action_set_heure_prevue_rapide()'
            },
            {
                'name': 'Effacer heure prévue',
                'code': 'if records:\n    records.action_clear_heure_prevue()'
            }
        ]
        
        for action_data in actions_data:
            action = env['ir.actions.server'].create({
                'name': action_data['name'],
                'model_id': pos_order_model.id,
                'state': 'code',
                'code': action_data['code'],
                'binding_model_id': pos_order_model.id,
                'binding_view_types': 'form',
                'active': True,
            })
            print(f"✅ Action '{action_data['name']}' créée (ID: {action.id})")
        
        # Valider les changements
        env.cr.commit()
        
        print("")
        print("🎉 Toutes les actions ont été créées avec succès!")
        print("")
        print("📋 Instructions:")
        print("1. Allez dans Point de Vente > Commandes")
        print("2. Sélectionnez une commande")
        print("3. Cliquez sur Actions dans la barre d'outils")
        print("4. Vous devriez voir les 3 actions heure prévue")
        print("")
        print("💡 Si les actions ne sont toujours pas visibles:")
        print("   - Videz le cache du navigateur (Ctrl+F5)")
        print("   - Redémarrez Odoo")
        print("   - Vérifiez que vous êtes dans la vue 'form'")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de la création des actions: {str(e)}")
        return False

if __name__ == "__main__":
    success = create_actions_sql()
    
    if success:
        print("✅ Script terminé avec succès!")
    else:
        print("❌ Script échoué!") 