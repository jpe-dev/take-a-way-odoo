# -*- coding: utf-8 -*-
"""
Script de test pour vérifier le champ heure_prevue dans les commandes PoS
"""

from odoo import api, fields, models
from datetime import datetime, timedelta

def test_heure_prevue():
    """Test simple pour vérifier que le champ heure_prevue fonctionne"""
    
    # Récupérer l'environnement Odoo
    env = api.Environment(cr, uid, {})
    
    # Créer une commande PoS de test
    pos_order = env['pos.order'].create({
        'name': 'Test Heure Prévue',
        'date_order': fields.Datetime.now(),
        'heure_prevue': fields.Datetime.now() + timedelta(hours=1),  # Heure prévue dans 1 heure
        'amount_total': 25.00,
        'state': 'draft'
    })
    
    print(f"Commande PoS créée avec succès:")
    print(f"  - ID: {pos_order.id}")
    print(f"  - Nom: {pos_order.name}")
    print(f"  - Date commande: {pos_order.date_order}")
    print(f"  - Heure prévue: {pos_order.heure_prevue}")
    print(f"  - Montant total: {pos_order.amount_total}")
    
    # Vérifier que le champ existe et fonctionne
    if hasattr(pos_order, 'heure_prevue'):
        print("✅ Le champ heure_prevue existe et fonctionne correctement")
    else:
        print("❌ Le champ heure_prevue n'existe pas")
    
    return pos_order

if __name__ == "__main__":
    test_heure_prevue() 