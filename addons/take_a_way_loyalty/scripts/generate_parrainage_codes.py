#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script pour générer des codes de parrainage pour les contacts existants
"""

import logging
from odoo import api, SUPERUSER_ID

_logger = logging.getLogger(__name__)

def generate_parrainage_codes(env):
    """Génère des codes de parrainage pour tous les contacts qui n'en ont pas"""
    
    # Rechercher tous les contacts sans code de parrainage
    contacts_sans_code = env['res.partner'].search([
        ('is_company', '=', False),
        ('type', '=', 'contact'),
        ('code_parrainage', '=', False)
    ])
    
    _logger.info(f"Génération de codes de parrainage pour {len(contacts_sans_code)} contacts")
    
    for contact in contacts_sans_code:
        try:
            # Générer un code unique
            code = contact._generate_parrainage_code()
            contact.code_parrainage = code
            _logger.info(f"Code généré pour {contact.name}: {code}")
        except Exception as e:
            _logger.error(f"Erreur lors de la génération du code pour {contact.name}: {str(e)}")
    
    _logger.info("Génération des codes de parrainage terminée")

def main():
    """Fonction principale"""
    env = api.Environment(cr, SUPERUSER_ID, {})
    generate_parrainage_codes(env)

if __name__ == "__main__":
    main() 