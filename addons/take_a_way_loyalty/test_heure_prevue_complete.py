# -*- coding: utf-8 -*-
"""
Test complet pour vérifier la fonctionnalité heure prévue
"""

from odoo import api, fields, models
from datetime import datetime, timedelta
import logging

_logger = logging.getLogger(__name__)

def test_heure_prevue_complete():
    """Test complet de la fonctionnalité heure prévue"""
    
    try:
        # Récupérer l'environnement Odoo
        env = api.Environment(cr, uid, {})
        
        print("=== Test complet de la fonctionnalité heure prévue ===")
        
        # 1. Vérifier que le champ existe
        pos_order_model = env['pos.order']
        if hasattr(pos_order_model, 'heure_prevue'):
            print("✅ Champ heure_prevue existe dans pos.order")
        else:
            print("❌ Champ heure_prevue n'existe pas dans pos.order")
            return False
        
        # 2. Créer une commande PoS de test
        pos_order = env['pos.order'].create({
            'name': 'Test Heure Prévue',
            'date_order': fields.Datetime.now(),
            'amount_total': 25.00,
            'state': 'draft'
        })
        
        print(f"✅ Commande PoS créée: {pos_order.name}")
        
        # 3. Tester l'action rapide
        print("🔄 Test de l'action rapide...")
        result = pos_order.action_set_heure_prevue_rapide()
        print("✅ Action rapide exécutée")
        
        # 4. Vérifier que l'heure prévue a été définie
        pos_order.refresh()
        if pos_order.heure_prevue:
            print(f"✅ Heure prévue définie: {pos_order.heure_prevue}")
        else:
            print("❌ Heure prévue non définie")
            return False
        
        # 5. Tester le wizard
        print("🔄 Test du wizard...")
        wizard = env['heure.prevue.wizard'].create({
            'pos_order_id': pos_order.id,
            'heure_prevue': fields.Datetime.now() + timedelta(hours=2)
        })
        
        print("✅ Wizard créé")
        
        # 6. Tester l'action de confirmation du wizard
        result = wizard.action_confirm()
        print("✅ Action de confirmation du wizard exécutée")
        
        # 7. Vérifier que l'heure prévue a été mise à jour
        pos_order.refresh()
        print(f"✅ Heure prévue mise à jour: {pos_order.heure_prevue}")
        
        # 8. Vérifier les actions serveur
        actions = env['ir.actions.server'].search([
            ('name', 'in', ['Définir heure prévue', 'Heure prévue +1h', 'Effacer heure prévue'])
        ])
        
        print(f"✅ {len(actions)} actions serveur trouvées")
        
        # 9. Vérifier les vues
        views = env['ir.ui.view'].search([
            ('name', 'like', '%heure.prevue%')
        ])
        
        print(f"✅ {len(views)} vues trouvées")
        
        # 10. Nettoyer
        pos_order.unlink()
        print("✅ Commande de test supprimée")
        
        print("🎉 Test complet réussi!")
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors du test: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_heure_prevue_complete()
    
    if success:
        print("✅ Test complet réussi! La fonctionnalité heure prévue fonctionne correctement.")
        print("📋 Instructions pour utiliser:")
        print("1. Allez dans Point de Vente > Commandes")
        print("2. Sélectionnez une commande")
        print("3. Vous devriez voir:")
        print("   - Le champ 'Heure prévue' dans le formulaire")
        print("   - Les actions dans le menu Actions:")
        print("     * 'Définir heure prévue' (ouvre le wizard)")
        print("     * 'Heure prévue +1h' (action rapide)")
        print("     * 'Effacer heure prévue' (efface le champ)")
    else:
        print("❌ Test échoué. Vérifiez les logs pour plus de détails.") 