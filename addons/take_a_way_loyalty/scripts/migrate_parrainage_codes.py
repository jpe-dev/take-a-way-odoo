#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script de migration pour générer des codes de parrainage pour les contacts existants
"""

def migrate_parrainage_codes(env):
    """Migration pour générer des codes de parrainage pour les contacts existants"""
    
    # Rechercher tous les contacts sans code de parrainage
    contacts_sans_code = env['res.partner'].search([
        ('is_company', '=', False),
        ('type', '=', 'contact'),
        ('code_parrainage', '=', False)
    ])
    
    print(f"Génération de codes de parrainage pour {len(contacts_sans_code)} contacts")
    
    for contact in contacts_sans_code:
        try:
            # Générer un code unique
            code = contact._generate_parrainage_code()
            contact.code_parrainage = code
            print(f"Code généré pour {contact.name}: {code}")
        except Exception as e:
            print(f"Erreur lors de la génération du code pour {contact.name}: {str(e)}")
    
    print("Migration des codes de parrainage terminée")

# Cette fonction sera appelée lors de la mise à jour du module
def post_init_hook(cr, registry):
    """Hook appelé après l'installation/mise à jour du module"""
    env = api.Environment(cr, SUPERUSER_ID, {})
    migrate_parrainage_codes(env) 