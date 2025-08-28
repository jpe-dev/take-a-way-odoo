# -*- coding: utf-8 -*-
"""
Script simple pour créer les actions heure prévue
À exécuter dans le shell Odoo
"""

# Supprimer les anciennes actions
old_actions = env['ir.actions.server'].search([
    ('name', 'like', '%heure%'),
    ('model_id.model', '=', 'pos.order')
])
if old_actions:
    old_actions.unlink()
    print("✅ Anciennes actions supprimées")

# Créer les nouvelles actions
pos_order_model = env['ir.model'].search([('model', '=', 'pos.order')], limit=1)

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

print("🎉 Toutes les actions ont été créées avec succès!") 