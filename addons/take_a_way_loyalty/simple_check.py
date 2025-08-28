# -*- coding: utf-8 -*-
"""
Script simple pour vérifier et créer les actions
À exécuter dans le shell Odoo
"""

# Vérifier les actions existantes
print("=== Vérification des actions existantes ===")
actions = env['ir.actions.server'].search([
    ('name', 'like', '%heure%')
])
print(f"Actions trouvées: {len(actions)}")
for action in actions:
    print(f"- {action.name} (ID: {action.id})")

# Supprimer les anciennes actions
if actions:
    actions.unlink()
    print("✅ Anciennes actions supprimées")

# Créer les nouvelles actions
print("\n=== Création des nouvelles actions ===")
pos_order_model = env['ir.model'].search([('model', '=', 'pos.order')], limit=1)

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

print("\n🎉 Actions créées avec succès!")
print("\n📋 Instructions:")
print("1. Allez dans Point de Vente > Commandes")
print("2. Sélectionnez une commande")
print("3. Cliquez sur Actions dans la barre d'outils")
print("4. Vous devriez voir les 3 actions heure prévue") 