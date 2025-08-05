#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script pour corriger l'attribution des points de fidélité
"""

import logging

_logger = logging.getLogger(__name__)

def correct_points_attribution(env):
    """
    Corrige l'attribution des points de fidélité
    """
    _logger.info("=== Correction de l'attribution des points ===")
    
    # 1. Analyser les points actuels
    points_records = env['take_a_way_loyalty.points_utilisateur'].search([])
    _logger.info(f"Nombre d'utilisateurs avec des points: {len(points_records)}")
    
    corrections = []
    
    for points_record in points_records:
        _logger.info(f"Utilisateur: {points_record.utilisateur_id.name}")
        _logger.info(f"  - Points actuels: {points_record.points_total}")
        
        # 2. Calculer les points corrects basés sur les missions complétées
        missions_completed = env['take_a_way_loyalty.mission_user'].search([
            ('utilisateur_id', '=', points_record.utilisateur_id.id),
            ('etat', '=', 'termine')
        ])
        
        points_corrects = 0
        for mission_user in missions_completed:
            points_corrects += mission_user.mission_id.point_recompense
            _logger.info(f"    Mission terminée: {mission_user.mission_id.name} (+{mission_user.mission_id.point_recompense} points)")
        
        # 3. Vérifier s'il y a une différence
        if points_record.points_total != points_corrects:
            difference = points_corrects - points_record.points_total
            _logger.warning(f"  - Différence détectée: {difference} points")
            _logger.warning(f"  - Points actuels: {points_record.points_total}")
            _logger.warning(f"  - Points corrects: {points_corrects}")
            
            corrections.append({
                'utilisateur': points_record.utilisateur_id.name,
                'points_actuels': points_record.points_total,
                'points_corrects': points_corrects,
                'difference': difference
            })
            
            # 4. Corriger les points
            points_record.points_total = points_corrects
            _logger.info(f"  - Points corrigés: {points_record.points_total}")
        else:
            _logger.info(f"  - Points corrects: {points_record.points_total}")
    
    # 5. Résumé des corrections
    if corrections:
        _logger.info("=== Résumé des corrections ===")
        for correction in corrections:
            _logger.info(f"Utilisateur: {correction['utilisateur']}")
            _logger.info(f"  - Ancien total: {correction['points_actuels']}")
            _logger.info(f"  - Nouveau total: {correction['points_corrects']}")
            _logger.info(f"  - Différence: {correction['difference']}")
    else:
        _logger.info("Aucune correction nécessaire")
    
    return {
        'corrections': corrections,
        'total_corrections': len(corrections)
    }

def reset_all_points(env):
    """
    Remet à zéro tous les points de fidélité
    """
    _logger.info("=== Remise à zéro de tous les points ===")
    
    points_records = env['take_a_way_loyalty.points_utilisateur'].search([])
    for points_record in points_records:
        _logger.info(f"Remise à zéro pour {points_record.utilisateur_id.name}")
        points_record.points_total = 0
    
    _logger.info(f"Points remis à zéro pour {len(points_records)} utilisateurs")
    return True

def main():
    """
    Fonction principale
    """
    _logger.info("Démarrage de la correction des points")
    
    # Cette fonction serait appelée depuis Odoo
    # env = self.env
    # result = correct_points_attribution(env)
    # _logger.info(f"Corrections effectuées: {result['total_corrections']}")
    
    _logger.info("Correction terminée")

if __name__ == "__main__":
    main() 