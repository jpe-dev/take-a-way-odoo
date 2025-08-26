# -*- coding: utf-8 -*-
"""
Test simple pour vérifier que le champ heure_prevue fonctionne
"""

from odoo import api, fields, models
from datetime import datetime, timedelta
import logging

_logger = logging.getLogger(__name__)

def test_simple_heure_prevue():
    """Test simple pour vérifier que le champ heure_prevue fonctionne"""

    try:
        # Récupérer l'environnement Odoo
        env = api.Environment(cr, uid, {})

        # Vérifier que le champ existe dans le modèle
        pos_order_model = env['pos.order']

        if hasattr(pos_order_model, 'heure_prevue'):
            print("✅ Le champ heure_prevue existe dans le modèle pos.order")
        else:
            print("❌ Le champ heure_prevue n'existe pas dans le modèle pos.order")
            return False

        # Créer une commande PoS de test
        pos_order = env['pos.order'].create({
            'name': 'Test Heure Prévue Simple',
            'date_order': fields.Datetime.now(),
            'heure_prevue': fields.Datetime.now() + timedelta(hours=1),
            'amount_total': 25.00,
            'state': 'draft'
        })

        print("✅ Commande PoS créée avec succès")
        print(f"  - ID: {pos_order.id}")
        print(f"  - Nom: {pos_order.name}")
        print(f"  - Heure prévue: {pos_order.heure_prevue}")

        # Vérifier que le champ peut être modifié
        pos_order.write({
            'heure_prevue': fields.Datetime.now() + timedelta(hours=2)
        })

        print("✅ Le champ heure_prevue peut être modifié")
        print(f"  - Nouvelle heure prévue: {pos_order.heure_prevue}")

        # Vérifier les actions
        if hasattr(pos_order, 'action_set_heure_prevue_rapide'):
            print("✅ Action rapide disponible")
        else:
            print("❌ Action rapide non disponible")

        if hasattr(pos_order, 'action_set_heure_prevue'):
            print("✅ Action wizard disponible")
        else:
            print("❌ Action wizard non disponible")

        # Nettoyer - supprimer la commande de test
        pos_order.unlink()
        print("✅ Commande de test supprimée")

        return True

    except Exception as e:
        print(f"❌ Erreur lors du test: {str(e)}")
        return False

if __name__ == "__main__":
    print("=== Test simple du champ heure_prevue ===")

    success = test_simple_heure_prevue()

    if success:
        print("✅ Test réussi! Le champ heure_prevue fonctionne correctement.")
        print("📋 Instructions:")
        print("1. Allez dans Point de Vente > Commandes")
        print("2. Sélectionnez une commande")
        print("3. Dans le menu Actions, vous devriez voir:")
        print("   - 'Définir heure prévue' (ouvre le wizard)")
        print("   - 'Heure prévue +1h' (action rapide)")
        print("   - 'Effacer heure prévue' (efface le champ)")
    else:
        print("❌ Test échoué. Vérifiez les logs pour plus de détails.") 