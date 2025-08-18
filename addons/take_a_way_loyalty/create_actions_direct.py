#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script pour créer directement les actions heure prévue
"""

import sys
import os

# Ajouter le chemin d'Odoo
sys.path.append('/usr/lib/python3/dist-packages')

from odoo import api, SUPERUSER_ID
import odoo

def create_actions():
    """Crée les actions pour l'heure prévue"""
    
    try:
        # Initialiser Odoo
        odoo.cli.main()
        
        # Créer l'environnement
        registry = odoo.registry('db-odoo-ta')
        cr = registry.cursor()
        env = api.Environment(cr, SUPERUSER_ID, {})
        
        print("=== Création des actions heure prévue ===")
        
        # Supprimer les anciennes actions si elles existent
        old_actions = env['ir.actions.server'].search([
            ('name', 'like', '%heure%'),
            ('model_id.model', '=', 'pos.order')
        ])
        if old_actions:
            old_actions.unlink()
            print("✅ Anciennes actions supprimées")
        
        # Créer les nouvelles actions
        pos_order_model = env['ir.model'].search([('model', '=', 'pos.order')], limit=1)
        
        if not pos_order_model:
            print("❌ Modèle pos.order non trouvé")
            return False
        
        # Action 1: Définir heure prévue
        action1 = env['ir.actions.server'].create({
            'name': 'Définir heure prévue',
            'model_id': pos_order_model.id,
            'state': 'code',
            'code': 'if records:\n    records.action_set_heure_prevue()',
            'binding_model_id': pos_order_model.id,
            'binding_view_types': 'form',
        })
        print("✅ Action 'Définir heure prévue' créée (ID: {})".format(action1.id))
        
        # Action 2: Heure prévue +1h
        action2 = env['ir.actions.server'].create({
            'name': 'Heure prévue +1h',
            'model_id': pos_order_model.id,
            'state': 'code',
            'code': 'if records:\n    records.action_set_heure_prevue_rapide()',
            'binding_model_id': pos_order_model.id,
            'binding_view_types': 'form',
        })
        print("✅ Action 'Heure prévue +1h' créée (ID: {})".format(action2.id))
        
        # Action 3: Effacer heure prévue
        action3 = env['ir.actions.server'].create({
            'name': 'Effacer heure prévue',
            'model_id': pos_order_model.id,
            'state': 'code',
            'code': 'if records:\n    records.action_clear_heure_prevue()',
            'binding_model_id': pos_order_model.id,
            'binding_view_types': 'form',
        })
        print("✅ Action 'Effacer heure prévue' créée (ID: {})".format(action3.id))
        
        # Valider les changements
        cr.commit()
        
        print("")
        print("🎉 Toutes les actions ont été créées avec succès!")
        print("")
        print("📋 Instructions:")
        print("1. Allez dans Point de Vente > Commandes")
        print("2. Sélectionnez une commande")
        print("3. Cliquez sur Actions dans la barre d'outils")
        print("4. Vous devriez voir les 3 actions heure prévue")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de la création des actions: {str(e)}")
        return False
    finally:
        if 'cr' in locals():
            cr.close()

if __name__ == "__main__":
    success = create_actions()
    
    if success:
        print("✅ Script terminé avec succès!")
    else:
        print("❌ Script échoué!")
        sys.exit(1) 