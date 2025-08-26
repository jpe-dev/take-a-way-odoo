# -*- coding: utf-8 -*-

from . import controllers
from . import models
from . import wizards

# Hook de migration pour générer les codes de parrainage
def post_init_hook(env):
    """Hook appelé après l'installation/mise à jour du module"""
    import random
    
    # Vérifier si le champ code_parrainage existe
    try:
        # Vérifier si le champ existe dans le modèle
        if 'code_parrainage' not in env['res.partner']._fields:
            print("Le champ code_parrainage n'existe pas encore, skip de la génération")
            return
            
        # Rechercher tous les contacts sans code de parrainage
        contacts_sans_code = env['res.partner'].search([
            ('is_company', '=', False),
            ('type', '=', 'contact'),
            ('code_parrainage', '=', False)
        ])
        
        print(f"Génération de codes de parrainage pour {len(contacts_sans_code)} contacts")
        
        def generate_parrainage_code():
            """Génère un code de parrainage unique de 6 chiffres"""
            while True:
                code = ''.join([str(random.randint(0, 9)) for _ in range(6)])
                # Vérifier que le code n'existe pas déjà
                existing = env['res.partner'].search([('code_parrainage', '=', code)], limit=1)
                if not existing:
                    return code
        
        for contact in contacts_sans_code:
            try:
                # Générer un code unique
                code = generate_parrainage_code()
                contact.code_parrainage = code
                print(f"Code généré pour {contact.name}: {code}")
            except Exception as e:
                print(f"Erreur lors de la génération du code pour {contact.name}: {str(e)}")
        
        print("Migration des codes de parrainage terminée")
    except Exception as e:
        print(f"Erreur lors de l'exécution du post_init_hook: {str(e)}")
        # Ne pas faire échouer l'installation si le hook échoue
        pass

# Hook supprimé car cause des erreurs
