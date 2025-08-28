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

        # Activer les promotions/cartes-cadeaux/programmes de fidélité sur les PdV
        try:
            pos_configs = env['pos.config'].search([])
            for config in pos_configs:
                # Selon versions, le champ de programme peut être 'loyalty_id'. L'important ici
                # est d'activer la fonctionnalité Pricing > Loyalty côté PoS si un champ existe.
                values = {}
                # Activer les promotions/récompenses si disponible
                # Plusieurs installations utilisent un booléen 'module_pos_coupon' ou 'module_coupon'.
                for bool_field in ['module_pos_loyalty', 'module_pos_coupon', 'module_coupon']:
                    if bool_field in config._fields:
                        values[bool_field] = True
                if values:
                    config.write(values)
            print("Paramètre promotions/fidélité PoS activé sur les configurations existantes")
        except Exception as e:
            print(f"Erreur lors de l'activation des promotions PoS: {str(e)}")

        # Créer automatiquement un programme de fidélité PoS s'il n'en existe aucun
        try:
            program_model = env['loyalty.program']
            # Chercher un programme applicable au PoS
            domain = []
            if 'applies_on' in program_model._fields:
                domain = [('applies_on', 'in', ['pos', 'both'])]
            program = program_model.search(domain or [], limit=1)
            if not program:
                vals = {
                    'name': 'TAW - Fidélité PoS',
                }
                # Renseigner dynamiquement les champs selon la version
                if 'program_type' in program_model._fields:
                    pt_field = program_model._fields['program_type']
                    try:
                        sel = pt_field.selection(env) if callable(pt_field.selection) else pt_field.selection
                        keys = [k for k, _ in (sel or [])]
                    except Exception:
                        keys = []
                    desired = 'loyalty'
                    vals['program_type'] = desired if desired in keys or not keys else keys[0]
                if 'applies_on' in program_model._fields:
                    ao_field = program_model._fields['applies_on']
                    try:
                        sel = ao_field.selection(env) if callable(ao_field.selection) else ao_field.selection
                        keys = [k for k, _ in (sel or [])]
                    except Exception:
                        keys = []
                    preferred = None
                    for opt in ['pos', 'both', 'orders', 'all', 'any']:
                        if opt in keys:
                            preferred = opt
                            break
                    if preferred:
                        vals['applies_on'] = preferred
                if 'company_id' in program_model._fields:
                    vals['company_id'] = env.company.id
                if 'active' in program_model._fields:
                    vals['active'] = True

                try:
                    program = program_model.create(vals)
                    print(f"Programme de fidélité PoS créé: {program.name} (ID: {program.id})")
                except Exception as e2:
                    print(f"Impossible de créer le programme de fidélité PoS: {str(e2)}")
                    program = program_model.search(domain or [], limit=1)

            # Associer le programme aux PdV si le champ existe
            if program:
                pos_configs = env['pos.config'].search([])
                for config in pos_configs:
                    if 'loyalty_id' in config._fields and not config.loyalty_id:
                        try:
                            config.write({'loyalty_id': program.id})
                        except Exception as e3:
                            print(f"Association du programme au PdV {config.display_name} impossible: {str(e3)}")
        except Exception as e:
            print(f"Erreur lors de la création/association du programme de fidélité PoS: {str(e)}")
    except Exception as e:
        print(f"Erreur lors de l'exécution du post_init_hook: {str(e)}")
        # Ne pas faire échouer l'installation si le hook échoue
        pass

# Hook supprimé car cause des erreurs
