# -*- coding: utf-8 -*-
"""
Test pour vérifier que le wizard d'heure prévue fonctionne
"""

from odoo import api, fields, models
from datetime import datetime, timedelta
import logging

_logger = logging.getLogger(__name__)

def test_wizard_heure_prevue():
    """Test du wizard d'heure prévue"""
    
    try:
        # Récupérer l'environnement Odoo
        env = api.Environment(cr, uid, {})
        
        # Vérifier que le modèle wizard existe
        if not env['ir.model'].search([('model', '=', 'heure.prevue.wizard')]):
            print("❌ Le modèle heure.prevue.wizard n'existe pas")
            return False
        
        print("✅ Le modèle heure.prevue.wizard existe")
        
        # Créer une commande PoS de test
        pos_order = env['pos.order'].create({
            'name': 'Test Wizard Heure Prévue',
            'date_order': fields.Datetime.now(),
            'amount_total': 25.00,
            'state': 'draft'
        })
        
        print(f"✅ Commande PoS créée: {pos_order.name}")
        
        # Créer un wizard d'heure prévue
        wizard = env['heure.prevue.wizard'].create({
            'pos_order_id': pos_order.id,
            'heure_prevue': fields.Datetime.now() + timedelta(hours=1)
        })
        
        print(f"✅ Wizard créé avec heure prévue: {wizard.heure_prevue}")
        
        # Tester l'action de confirmation
        result = wizard.action_confirm()
        print("✅ Action de confirmation testée")
        
        # Vérifier que l'heure prévue a été mise à jour
        pos_order.refresh()
        if pos_order.heure_prevue:
            print(f"✅ Heure prévue mise à jour: {pos_order.heure_prevue}")
        else:
            print("❌ Heure prévue non mise à jour")
            return False
        
        # Tester l'action rapide
        result_rapide = pos_order.action_set_heure_prevue_rapide()
        print("✅ Action rapide testée")
        
        # Vérifier que l'heure prévue a été mise à jour
        pos_order.refresh()
        print(f"✅ Heure prévue après action rapide: {pos_order.heure_prevue}")
        
        # Nettoyer
        pos_order.unlink()
        print("✅ Commande de test supprimée")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors du test: {str(e)}")
        return False

if __name__ == "__main__":
    print("=== Test du wizard d'heure prévue ===")
    
    success = test_wizard_heure_prevue()
    
    if success:
        print("✅ Test réussi! Le wizard d'heure prévue fonctionne correctement.")
        print("📋 Instructions pour utiliser:")
        print("1. Allez dans Point de Vente > Commandes")
        print("2. Sélectionnez une commande")
        print("3. Dans le menu Actions, vous devriez voir:")
        print("   - 'Définir heure prévue' (ouvre le wizard)")
        print("   - 'Heure prévue +1h' (définit rapidement)")
    else:
        print("❌ Test échoué. Vérifiez les logs pour plus de détails.") 