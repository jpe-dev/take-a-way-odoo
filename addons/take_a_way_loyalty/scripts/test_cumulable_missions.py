#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script de test pour vérifier le bon fonctionnement des missions cumulables
"""

import logging

_logger = logging.getLogger(__name__)

def test_cumulable_missions(env):
    """
    Teste le bon fonctionnement des missions cumulables
    """
    _logger.info("=== Test des missions cumulables ===")
    
    # 1. Vérifier les missions existantes
    missions = env['take_a_way_loyalty.mission'].search([])
    _logger.info(f"Nombre de missions trouvées: {len(missions)}")
    
    for mission in missions:
        _logger.info(f"Mission: {mission.name}")
        _logger.info(f"  - Cumulable: {mission.cumulable}")
        _logger.info(f"  - Points de récompense: {mission.point_recompense}")
        _logger.info(f"  - Participants: {len(mission.mission_user_ids)}")
        
        # Vérifier les participants
        for participant in mission.mission_user_ids:
            _logger.info(f"    Participant: {participant.utilisateur_id.name}")
            _logger.info(f"      - État: {participant.etat}")
            _logger.info(f"      - Progression: {participant.progression}")
    
    # 2. Créer une mission de test cumulable
    test_mission = env['take_a_way_loyalty.mission'].create({
        'name': 'Test Mission Cumulable',
        'description': 'Mission de test pour vérifier le fonctionnement cumulable',
        'point_recompense': 50,
        'debut': '2024-01-01',
        'fin': '2024-12-31',
        'cumulable': True,
    })
    
    _logger.info(f"Mission de test créée: {test_mission.name}")
    
    # 3. Ajouter un participant
    contacts = env['res.partner'].search([('is_company', '=', False)], limit=1)
    if contacts:
        participant = test_mission.action_ajouter_participant(contacts[0].id)
        if participant:
            _logger.info(f"Participant ajouté: {participant.utilisateur_id.name}")
            
            # 4. Simuler la completion de la mission
            _logger.info("Simulation de la completion de la mission...")
            participant.progression = 100  # Simuler une progression complète
            participant._check_mission_completion(participant)
            
            _logger.info(f"État après completion: {participant.etat}")
            _logger.info(f"Progression après completion: {participant.progression}")
            
            # 5. Vérifier que la mission peut être répétée
            if participant.mission_id.cumulable and participant.etat == 'en_cours':
                _logger.info("✅ Mission cumulable fonctionne correctement")
            else:
                _logger.error("❌ Mission cumulable ne fonctionne pas correctement")
    
    return True

def main():
    """
    Fonction principale pour exécuter les tests
    """
    _logger.info("Démarrage des tests des missions cumulables")
    
    # Cette fonction serait appelée depuis Odoo
    # env = self.env
    # test_cumulable_missions(env)
    
    _logger.info("Tests terminés")

if __name__ == "__main__":
    main() 