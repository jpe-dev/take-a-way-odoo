#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script simple pour tester la configuration du module init_config
"""

import sys
import os

# Ajouter le chemin d'Odoo au PYTHONPATH
sys.path.insert(0, '/usr/lib/python3/dist-packages')

from odoo import api, SUPERUSER_ID

def test_config():
    """Teste la configuration actuelle"""
    with api.Environment.manage():
        env = api.Environment(api.Environment.manage().cr, SUPERUSER_ID, {})
        
        print("=== Test de configuration ===")
        
        # Test 1: Vérifier la société
        company = env['res.company'].browse(1)
        print(f"Société: {company.name}")
        print(f"Pays: {company.country_id.name if company.country_id else 'Non défini'}")
        print(f"Devise: {company.currency_id.name if company.currency_id else 'Non définie'}")
        
        # Test 2: Vérifier la langue de l'admin
        user = env['res.users'].browse(SUPERUSER_ID)
        print(f"Langue admin: {user.lang}")
        
        # Test 3: Vérifier les paramètres
        config_param = env['ir.config_parameter'].search([
            ('key', '=', 'account.chart_template_id')
        ], limit=1)
        if config_param:
            print(f"Paramètre chart_template_id: {config_param.value}")
        else:
            print("Paramètre chart_template_id non défini")
        
        print("=== Fin du test ===")

if __name__ == "__main__":
    test_config() 