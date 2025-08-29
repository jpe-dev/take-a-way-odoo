# -*- coding: utf-8 -*-

from odoo import models, fields, api  # type: ignore
import logging
from datetime import datetime, timedelta

_logger = logging.getLogger(__name__)

# Log au chargement du module
_logger.warning("[FIDELITE][DEBUG] Module take_a_way_loyalty chargé avec succès")

class PointsUtilisateur(models.Model):
    _name = 'take_a_way_loyalty.points_utilisateur'
    _description = 'Points de fidélité des utilisateurs'

    utilisateur_id = fields.Many2one('res.partner', string='Utilisateur', required=True)
    points_total = fields.Integer(string='Points totaux', default=0)

    _sql_constraints = [
        ('unique_utilisateur', 'UNIQUE(utilisateur_id)', 
         'Un utilisateur ne peut avoir qu\'un seul compteur de points!')
    ]

class Mission(models.Model):
    _name = 'take_a_way_loyalty.mission'
    _description = 'Mission de fidélité'

    name = fields.Char(string='Nom', required=True)
    description = fields.Text(string='Description')
    point_recompense = fields.Integer(string='Points de récompense')
    debut = fields.Date(string='Date de début')
    fin = fields.Date(string='Date de fin')
    cumulable = fields.Boolean(string='Cumulable', default=False)
    pos_config_id = fields.Many2one('pos.config', string='Point de Vente')

    # Relations
    mission_user_ids = fields.One2many('take_a_way_loyalty.mission_user', 'mission_id', string='Participants')
    condition_ids = fields.One2many('take_a_way_loyalty.condition_mission', 'mission_id', string='Conditions')

    @api.onchange('pos_config_id')
    def _onchange_pos_config_id(self):
        for mission in self:
            categories = mission.pos_config_id.iface_available_categ_ids
            _logger.info("Catégories PdV pour %s : %s", mission.pos_config_id.name, categories.mapped('name'))
            for condition in mission.condition_ids:
                if condition.type_condition and condition.type_condition.code == 'ACHAT_TOUTES_CATEGORIES':
                    condition.categories_ids = [(6, 0, categories.ids)]

    def ajouter_participant(self):
        """Ouvre le wizard d'ajout de participant à la mission"""
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'add.participant.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_mission_id': self.id,
            }
        }

    def ajouter_tous_contacts(self):
        """Ajoute tous les contacts comme participants à la mission"""
        # Récupérer tous les contacts (partenaires non-entreprises)
        contacts = self.env['res.partner'].search([
            ('is_company', '=', False),
            ('type', '=', 'contact')
        ])
        
        # Créer les enregistrements mission_user pour chaque contact
        for contact in contacts:
            try:
                # Vérifier si le contact est déjà participant
                existing = self.env['take_a_way_loyalty.mission_user'].search([
                    ('mission_id', '=', self.id),
                    ('utilisateur_id', '=', contact.id)
                ], limit=1)
                
                if not existing:
                    self.env['take_a_way_loyalty.mission_user'].create({
                        'mission_id': self.id,
                        'utilisateur_id': contact.id,
                        'date_debut': fields.Date.today(),
                        'progression': 0,
                        'etat': 'en_cours'
                    })
            except Exception as e:
                _logger.error("Erreur lors de l'ajout du contact %s à la mission %s: %s",
                            contact.name, self.name, str(e))
        
        return True

    def clear_missions_cache(self):
        """Nettoie le cache des missions vérifiées"""
        if hasattr(self.env, '_missions_cache'):
            cache_size = len(self.env._missions_cache)
            self.env._missions_cache.clear()
            _logger.info("[FIDELITE] Cache des missions nettoyé (%s entrées supprimées)", cache_size)
        return True

    def test_missions_manual(self):
        """Test manuel des missions pour déboguer"""
        _logger.warning("[FIDELITE][DEBUG] Test manuel des missions appelé")
        
        # Vérifier toutes les commandes POS récentes
        recent_orders = self.env['pos.order'].search([
            ('state', 'in', ['paid', 'done', 'invoiced']),
            ('create_date', '>=', fields.Date.today())
        ], limit=10)
        
        _logger.warning("[FIDELITE][DEBUG] Commandes POS récentes trouvées: %s", len(recent_orders))
        
        for order in recent_orders:
            _logger.warning("[FIDELITE][DEBUG] Commande: %s - Partenaire: %s - Statut: %s", 
                           order.id, order.partner_id.name if order.partner_id else "Aucun", order.state)
            order._check_missions()
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Test des missions',
                'message': f'Test terminé. Vérifiez les logs pour plus de détails.',
                'type': 'info',
            }
        }

    def test_cumulable_missions(self):
        """Test spécifique pour les missions cumulables"""
        _logger.info("=== Test des missions cumulables ===")
        
        # Vérifier les missions existantes
        missions = self.env['take_a_way_loyalty.mission'].search([])
        _logger.info(f"Nombre de missions trouvées: {len(missions)}")
        
        cumulable_missions = []
        non_cumulable_missions = []
        
        for mission in missions:
            if mission.cumulable:
                cumulable_missions.append(mission)
            else:
                non_cumulable_missions.append(mission)
            
            _logger.info(f"Mission: {mission.name}")
            _logger.info(f"  - Cumulable: {mission.cumulable}")
            _logger.info(f"  - Points de récompense: {mission.point_recompense}")
            _logger.info(f"  - Participants: {len(mission.mission_user_ids)}")
        
        message = f"""
        Résumé des missions:
        - Missions cumulables: {len(cumulable_missions)}
        - Missions non-cumulables: {len(non_cumulable_missions)}
        - Total: {len(missions)}
        
        Missions cumulables: {[m.name for m in cumulable_missions]}
        Missions non-cumulables: {[m.name for m in non_cumulable_missions]}
        """
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Test des missions cumulables',
                'message': message,
                'type': 'info',
            }
        }

    def test_points_attribution(self):
        """Test spécifique pour vérifier l'attribution des points"""
        _logger.info("=== Test de l'attribution des points ===")
        
        # Vérifier tous les utilisateurs et leurs points
        points_records = self.env['take_a_way_loyalty.points_utilisateur'].search([])
        _logger.info(f"Nombre d'utilisateurs avec des points: {len(points_records)}")
        
        total_points = 0
        details = []
        
        for points_record in points_records:
            _logger.info(f"Utilisateur: {points_record.utilisateur_id.name}")
            _logger.info(f"  - Points totaux: {points_record.points_total}")
            total_points += points_record.points_total
            details.append(f"{points_record.utilisateur_id.name}: {points_record.points_total} points")
        
        # Vérifier les missions et leurs points de récompense
        missions = self.env['take_a_way_loyalty.mission'].search([])
        _logger.info(f"Nombre de missions: {len(missions)}")
        
        mission_details = []
        for mission in missions:
            _logger.info(f"Mission: {mission.name}")
            _logger.info(f"  - Points de récompense: {mission.point_recompense}")
            _logger.info(f"  - Cumulable: {mission.cumulable}")
            _logger.info(f"  - Participants: {len(mission.mission_user_ids)}")
            mission_details.append(f"{mission.name}: {mission.point_recompense} points (cumulable: {mission.cumulable})")
        
        message = f"""
        Résumé des points:
        - Total des points attribués: {total_points}
        - Nombre d'utilisateurs: {len(points_records)}
        
        Détails par utilisateur:
        {chr(10).join(details)}
        
        Détails des missions:
        {chr(10).join(mission_details)}
        """
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Test de l\'attribution des points',
                'message': message,
                'type': 'info',
            }
        }

    def correct_points_attribution(self):
        """Corrige l'attribution des points de fidélité"""
        _logger.info("=== Correction de l'attribution des points ===")
        
        # 1. Analyser les points actuels
        points_records = self.env['take_a_way_loyalty.points_utilisateur'].search([])
        _logger.info(f"Nombre d'utilisateurs avec des points: {len(points_records)}")
        
        corrections = []
        
        for points_record in points_records:
            _logger.info(f"Utilisateur: {points_record.utilisateur_id.name}")
            _logger.info(f"  - Points actuels: {points_record.points_total}")
            
            # 2. Calculer les points corrects basés sur les missions complétées
            missions_completed = self.env['take_a_way_loyalty.mission_user'].search([
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
        
        message = f"""
        Correction des points terminée:
        - Utilisateurs vérifiés: {len(points_records)}
        - Corrections effectuées: {len(corrections)}
        
        Détails des corrections:
        {chr(10).join([f"- {c['utilisateur']}: {c['points_actuels']} → {c['points_corrects']} ({c['difference']:+d})" for c in corrections]) if corrections else "Aucune correction nécessaire"}
        """
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Correction des points',
                'message': message,
                'type': 'info',
            }
        }

    def test_mission_completion_safety(self):
        """Test de sécurité pour vérifier que _check_mission_completion fonctionne sans erreur"""
        _logger.info("=== Test de sécurité pour _check_mission_completion ===")
        
        # Récupérer toutes les missions en cours
        missions_users = self.env['take_a_way_loyalty.mission_user'].search([
            ('etat', '=', 'en_cours')
        ])
        
        _logger.info(f"Nombre de missions en cours: {len(missions_users)}")
        
        test_results = []
        
        for mission_user in missions_users:
            try:
                _logger.info(f"Test de la mission: {mission_user.mission_id.name}")
                _logger.info(f"  - Utilisateur: {mission_user.utilisateur_id.name}")
                _logger.info(f"  - État actuel: {mission_user.etat}")
                _logger.info(f"  - Progression: {mission_user.progression}")
                
                # Appeler _check_mission_completion pour tester
                mission_user._check_mission_completion(mission_user)
                
                _logger.info(f"  - État après test: {mission_user.etat}")
                _logger.info(f"  - Test réussi ✅")
                
                test_results.append({
                    'mission': mission_user.mission_id.name,
                    'utilisateur': mission_user.utilisateur_id.name,
                    'etat_avant': 'en_cours',
                    'etat_apres': mission_user.etat,
                    'success': True
                })
                
            except Exception as e:
                _logger.error(f"  - Erreur lors du test: {str(e)}")
                test_results.append({
                    'mission': mission_user.mission_id.name,
                    'utilisateur': mission_user.utilisateur_id.name,
                    'etat_avant': 'en_cours',
                    'etat_apres': 'erreur',
                    'success': False,
                    'error': str(e)
                })
        
        # Résumé des tests
        successful_tests = [r for r in test_results if r['success']]
        failed_tests = [r for r in test_results if not r['success']]
        
        message = f"""
        Test de sécurité terminé:
        - Tests réussis: {len(successful_tests)}/{len(test_results)}
        - Tests échoués: {len(failed_tests)}
        
        Détails des tests réussis:
        {chr(10).join([f"- {r['mission']} ({r['utilisateur']}): {r['etat_avant']} → {r['etat_apres']}" for r in successful_tests]) if successful_tests else "Aucun test réussi"}
        
        Détails des erreurs:
        {chr(10).join([f"- {r['mission']} ({r['utilisateur']}): {r.get('error', 'Erreur inconnue')}" for r in failed_tests]) if failed_tests else "Aucune erreur"}
        """
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Test de sécurité des missions',
                'message': message,
                'type': 'info' if not failed_tests else 'warning',
            }
        }

    def test_multiple_calls_protection(self):
        """Test de protection contre les appels multiples"""
        _logger.info("=== Test de protection contre les appels multiples ===")
        
        # Récupérer les commandes POS récentes
        recent_orders = self.env['pos.order'].search([
            ('state', 'in', ['paid', 'done', 'invoiced']),
            ('create_date', '>=', fields.Date.today())
        ], limit=5)
        
        _logger.info(f"Nombre de commandes récentes trouvées: {len(recent_orders)}")
        
        test_results = []
        
        for order in recent_orders:
            try:
                _logger.info(f"Test de la commande: {order.name} (ID: {order.id})")
                _logger.info(f"  - Statut: {order.state}")
                _logger.info(f"  - Partenaire: {order.partner_id.name if order.partner_id else 'Aucun'}")
                
                # Premier appel
                _logger.info("  - Premier appel à _check_missions...")
                order._check_missions(order)
                
                # Deuxième appel (devrait être ignoré)
                _logger.info("  - Deuxième appel à _check_missions...")
                order._check_missions(order)
                
                # Troisième appel (devrait être ignoré)
                _logger.info("  - Troisième appel à _check_missions...")
                order._check_missions(order)
                
                _logger.info("  - Test réussi ✅")
                
                test_results.append({
                    'commande': order.name,
                    'id': order.id,
                    'statut': order.state,
                    'success': True
                })
                
            except Exception as e:
                _logger.error(f"  - Erreur lors du test: {str(e)}")
                test_results.append({
                    'commande': order.name,
                    'id': order.id,
                    'statut': order.state,
                    'success': False,
                    'error': str(e)
                })
        
        # Résumé des tests
        successful_tests = [r for r in test_results if r['success']]
        failed_tests = [r for r in test_results if not r['success']]
        
        message = f"""
        Test de protection terminé:
        - Tests réussis: {len(successful_tests)}/{len(test_results)}
        - Tests échoués: {len(failed_tests)}
        
        Détails des tests réussis:
        {chr(10).join([f"- {r['commande']} (ID: {r['id']}): {r['statut']}" for r in successful_tests]) if successful_tests else "Aucun test réussi"}
        
        Détails des erreurs:
        {chr(10).join([f"- {r['commande']} (ID: {r['id']}): {r.get('error', 'Erreur inconnue')}" for r in failed_tests]) if failed_tests else "Aucune erreur"}
        """
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Test de protection contre les appels multiples',
                'message': message,
                'type': 'info' if not failed_tests else 'warning',
            }
        }

    @api.model_create_multi
    def create(self, vals_list):
        missions = super(Mission, self).create(vals_list)
        for mission in missions:
            contacts = self.env['res.partner'].search([
                ('is_company', '=', False),
                ('type', '=', 'contact')
            ])
            for contact in contacts:
                try:
                    self.env['take_a_way_loyalty.mission_user'].create({
                        'mission_id': mission.id,
                        'utilisateur_id': contact.id,
                        'date_debut': fields.Date.today(),
                        'progression': 0,
                        'etat': 'en_cours'
                    })
                except Exception as e:
                    _logger.error("Erreur lors de l'ajout automatique du contact %s à la mission %s: %s",
                                contact.name, mission.name, str(e))
            # Ajout auto des catégories PdV pour la condition ACHAT_TOUTES_CATEGORIES
            if mission.pos_config_id:
                categories = mission.pos_config_id.iface_available_categ_ids
                for condition in mission.condition_ids:
                    if condition.type_condition and condition.type_condition.code == 'ACHAT_TOUTES_CATEGORIES':
                        if categories:
                            condition.categories_ids = [(6, 0, categories.ids)]
        return missions

class MissionUser(models.Model):
    _name = 'take_a_way_loyalty.mission_user'
    _description = 'Progression des missions par utilisateur'

    mission_id = fields.Many2one('take_a_way_loyalty.mission', string='Mission', required=True)
    utilisateur_id = fields.Many2one('res.partner', string='Utilisateur', required=True)
    date_debut = fields.Date(string='Date de début', default=fields.Date.today)
    date_heure_debut = fields.Datetime(string='Date et heure de début', default=fields.Datetime.now)
    progression = fields.Integer(string='Progression', default=0)
    progression_par_produit = fields.One2many('take_a_way_loyalty.progression_produit', 'mission_user_id', string='Progression par produit')
    etat = fields.Selection([
        ('en_cours', 'En cours'),
        ('termine', 'Terminé'),
        ('expire', 'Expiré'),
        ('abandonne', 'Abandonné')
    ], string='État', default='en_cours')
    progression_periode_ids = fields.One2many(
        'take_a_way_loyalty.progression_periode',
        'mission_user_id',
        string='Progression par période'
    )

    _sql_constraints = [
        ('unique_mission_user', 'UNIQUE(mission_id, utilisateur_id)', 
         'Un utilisateur ne peut participer qu\'une seule fois à une mission!')
    ]

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            # Créer l'enregistrement des points si nécessaire
            if vals.get('utilisateur_id'):
                points_record = self.env['take_a_way_loyalty.points_utilisateur'].sudo().search([
                    ('utilisateur_id', '=', vals['utilisateur_id'])
                ], limit=1)
                
                if not points_record:
                    try:
                        points_record = self.env['take_a_way_loyalty.points_utilisateur'].sudo().create({
                            'utilisateur_id': vals['utilisateur_id'],
                            'points_total': 0
                        })
                    except Exception as e:
                        _logger.error("Erreur lors de la création des points utilisateur: %s", str(e))
        
        return super(MissionUser, self).create(vals_list)

    @api.onchange('progression')
    def _onchange_progression(self):
        for record in self:
            self._check_mission_completion(record)

    def _check_mission_completion(self, mission_user):
        _logger.warning("[FIDELITE][DEBUG] _check_mission_completion appelée pour mission_user %s", mission_user.id)
        
        # Vérifier si la mission est déjà terminée pour éviter les appels multiples
        if mission_user.etat == 'termine':
            _logger.warning("[FIDELITE][DEBUG] Mission déjà terminée, ignorée")
            return
        
        # Vérifier si les conditions sont déjà remplies pour éviter les appels multiples
        # en recalculant rapidement si les conditions sont remplies
        conditions_remplies = True
        for condition in mission_user.mission_id.condition_ids:
            if condition.type_condition.code == 'ACHAT_PRODUIT':
                _logger.warning("[FIDELITE][DEBUG] Vérification condition ACHAT_PRODUIT")
                _logger.warning("[FIDELITE][DEBUG] Produits définis: %s", condition.produits_ids.mapped('name'))
                _logger.warning("[FIDELITE][DEBUG] Quantités définies: %s", len(condition.quantites_produits))
                
                # Gestion des produits multiples avec quantités définies
                if condition.produits_ids and condition.quantites_produits:
                    _logger.warning("[FIDELITE][DEBUG] Utilisation de la logique produits multiples avec quantités définies")
                    # Vérifier que tous les produits ont atteint leur quantité requise
                    for quantite_produit in condition.quantites_produits:
                        progression_produit = self.env['take_a_way_loyalty.progression_produit'].search([
                            ('mission_user_id', '=', mission_user.id),
                            ('produit_id', '=', quantite_produit.produit_id.id)
                        ], limit=1)
                        _logger.warning("[FIDELITE][DEBUG] Produit %s: progression=%s, requise=%s, actuelle=%s", 
                                       quantite_produit.produit_id.name, 
                                       progression_produit.id if progression_produit else "Aucune",
                                       quantite_produit.quantite_requise,
                                       progression_produit.quantite_actuelle if progression_produit else 0)
                        if not progression_produit or progression_produit.quantite_actuelle < quantite_produit.quantite_requise:
                            conditions_remplies = False
                            break
                    if not conditions_remplies:
                        break
                # Gestion des produits multiples sans quantités définies (quantité globale)
                elif condition.produits_ids and not condition.quantites_produits:
                    _logger.warning("[FIDELITE][DEBUG] Vérification produits multiples avec quantité globale")
                    # Vérifier que tous les produits ont atteint leur quantité requise
                    for produit in condition.produits_ids:
                        progression_produit = self.env['take_a_way_loyalty.progression_produit'].search([
                            ('mission_user_id', '=', mission_user.id),
                            ('produit_id', '=', produit.id)
                        ], limit=1)
                        _logger.warning("[FIDELITE][DEBUG] Produit %s: progression=%s, requise=%s, actuelle=%s", 
                                       produit.name, 
                                       progression_produit.id if progression_produit else "Aucune",
                                       condition.quantite or 1,
                                       progression_produit.quantite_actuelle if progression_produit else 0)
                        if not progression_produit or progression_produit.quantite_actuelle < (condition.quantite or 1):
                            conditions_remplies = False
                            break
                    if not conditions_remplies:
                        break
            elif condition.type_condition.code == 'CATEGORIE_PRODUIT':
                # Pour CATEGORIE_PRODUIT, on vérifie si la progression (quantité achetée) 
                # dans la catégorie spécifiée atteint la quantité requise
                if mission_user.progression < condition.quantite:
                    conditions_remplies = False
                    break
            elif condition.type_condition.code == 'ACHAT_TOUTES_CATEGORIES':
                categories = condition.categories_ids
                categories_achetees = set()
                commandes = self.env['pos.order'].search([
                    ('partner_id', '=', mission_user.utilisateur_id.id),
                    ('state', '=', 'paid'),
                    ('date_order', '>=', mission_user.date_heure_debut)
                ])
                _logger.info("[FIDELITE] ACHAT_TOUTES_CATEGORIES - Catégories attendues: %s", categories.mapped('name'))
                for commande in commandes:
                    for ligne in commande.lines:
                        if ligne.product_id.product_tmpl_id and ligne.product_id.product_tmpl_id.pos_categ_id and ligne.product_id.product_tmpl_id.pos_categ_id.id in categories.ids:
                            categories_achetees.add(ligne.product_id.product_tmpl_id.pos_categ_id.id)
                _logger.info("[FIDELITE] ACHAT_TOUTES_CATEGORIES - Catégories achetées: %s", list(categories_achetees))
                mission_user.progression = len(categories_achetees)
                _logger.info("[FIDELITE] ACHAT_TOUTES_CATEGORIES - Progression calculée: %s/%s", len(categories_achetees), len(categories))
                if len(categories_achetees) < len(categories):
                    conditions_remplies = False
                    break
            else:
                if mission_user.progression < condition.nombre_commandes:
                    conditions_remplies = False
                    break

        # Vérifier à nouveau l'état avant de procéder (protection contre les appels multiples)
        if not conditions_remplies or mission_user.etat != 'en_cours':
            _logger.warning("[FIDELITE][DEBUG] Conditions non remplies ou mission déjà traitée, ignorée")
            return

        if not mission_user.mission_id.condition_ids:
            _logger.warning("La mission %s n'a pas de conditions", mission_user.mission_id.name)
            return

        # Marquer temporairement comme terminé pour éviter les appels multiples
        mission_user.etat = 'termine'
        
        try:
            # Attribuer les points de récompense
            points_record = self.env['take_a_way_loyalty.points_utilisateur'].search([
                ('utilisateur_id', '=', mission_user.utilisateur_id.id)
            ], limit=1)
            if not points_record:
                points_record = self.env['take_a_way_loyalty.points_utilisateur'].create({
                    'utilisateur_id': mission_user.utilisateur_id.id,
                    'points_total': 0
                })
            
            # Log détaillé pour tracer l'attribution des points
            points_avant = points_record.points_total
            points_a_ajouter = mission_user.mission_id.point_recompense
            points_record.points_total += points_a_ajouter
            points_apres = points_record.points_total
            
            _logger.info("[FIDELITE] Attribution des points pour la mission '%s'", mission_user.mission_id.name)
            _logger.info("[FIDELITE] Utilisateur: %s", mission_user.utilisateur_id.name)
            _logger.info("[FIDELITE] Points avant: %s", points_avant)
            _logger.info("[FIDELITE] Points à ajouter: %s", points_a_ajouter)
            _logger.info("[FIDELITE] Points après: %s", points_apres)
            _logger.info("[FIDELITE] Mission cumulable: %s", mission_user.mission_id.cumulable)

            # Créditer aussi la carte de fidélité native Odoo si disponible
            try:
                self._credit_partner_loyalty_card(mission_user, points_a_ajouter)
            except Exception as e:
                _logger.warning("[FIDELITE] Échec du crédit de la carte de fidélité native: %s", str(e))
            
            # Gestion des missions cumulables vs non-cumulables
            if mission_user.mission_id.cumulable:
                _logger.info("[FIDELITE] Mission cumulable terminée - Réinitialisation pour permettre la répétition")
                # Pour les missions cumulables, réinitialiser la progression pour permettre la répétition
                mission_user._reset_mission_progression()
            else:
                _logger.info("[FIDELITE] Mission non-cumulable terminée - Passage à l'état terminé")
                # Pour les missions non-cumulables, l'état est déjà 'termine'
        except Exception as e:
            # En cas d'erreur, remettre l'état en cours
            mission_user.etat = 'en_cours'
            _logger.error("[FIDELITE] Erreur lors de l'attribution des points: %s", str(e))
            raise

    def _reset_mission_progression(self):
        """Réinitialise la progression d'une mission pour permettre sa répétition"""
        self.ensure_one()
        _logger.info("[FIDELITE] Réinitialisation de la progression pour la mission %s", self.mission_id.name)
        
        # Réinitialiser la progression générale
        self.progression = 0
        
        # Réinitialiser les progressions par produit
        for progression_produit in self.progression_par_produit:
            progression_produit.quantite_actuelle = 0
        
        # Réinitialiser les progressions par période (pour les missions consécutives)
        for progression_periode in self.progression_periode_ids:
            progression_periode.unlink()
        
        # Garder l'état en cours pour permettre la répétition
        self.etat = 'en_cours'
        
        _logger.info("[FIDELITE] Progression réinitialisée pour la mission %s", self.mission_id.name)

    def _set_default_values(self, vals):
        """Définit les valeurs par défaut pour la création."""
        if 'date_debut' not in vals:
            vals['date_debut'] = fields.Date.today()
        if 'progression' not in vals:
            vals['progression'] = 0
        return vals

    def _credit_partner_loyalty_card(self, mission_user, points_to_add):
        """Crédite la carte de fidélité native Odoo du partenaire si le module est présent.

        Cette méthode tente d'être résiliente aux différences de versions (Odoo 16/17/18)
        concernant les noms de champs et les modèles de fidélité.
        """
        partner = mission_user.utilisateur_id
        if not partner or not points_to_add:
            return False

        # Vérifier la présence des modèles loyalty.*
        try:
            card_model = self.env['loyalty.card']
            _logger.info("[FIDELITE] LOYALTY: Modèle loyalty.card disponible, tentative de crédit. Partenaire=%s, Points=%s", partner.name, points_to_add)
        except Exception:
            _logger.info("[FIDELITE] Module de fidélité natif absent (loyalty.card). Crédit ignoré.")
            return False

        # Tenter de récupérer un programme de fidélité pertinent depuis la config du PdV liée à la mission
        program = False
        try:
            program = getattr(mission_user.mission_id.pos_config_id, 'loyalty_id', False)
            if program:
                _logger.info("[FIDELITE] LOYALTY: Programme détecté via pos.config: %s (%s)", getattr(program, 'name', program.id), program.id)
        except Exception:
            program = False
        # Fallback: rechercher n'importe quel programme (idéalement pour le PoS)
        if not program:
            try:
                program_model = self.env['loyalty.program']
                # Essayer d'abord un programme configuré pour le PoS
                prog_domain = []
                if 'applies_on' in program_model._fields:
                    prog_domain = [('applies_on', 'in', ['pos', 'both'])]
                program = program_model.search(prog_domain or [], limit=1)
                _logger.info("[FIDELITE] LOYALTY: Programme fallback trouvé=%s", bool(program))
            except Exception:
                program = False

        # Si toujours aucun programme, tenter d'en créer un minimal à la volée
        if not program:
            try:
                program_model = self.env['loyalty.program']
                create_vals = {'name': 'TAW - Fidélité PoS Auto'}
                # program_type selection
                if 'program_type' in program_model._fields:
                    pt_field = program_model._fields['program_type']
                    try:
                        sel = pt_field.selection(self.env) if callable(pt_field.selection) else pt_field.selection
                        keys = [k for k, _ in (sel or [])]
                    except Exception:
                        keys = []
                    desired = 'loyalty'
                    create_vals['program_type'] = desired if desired in keys or not keys else keys[0]
                # applies_on selection
                if 'applies_on' in program_model._fields:
                    ao_field = program_model._fields['applies_on']
                    try:
                        sel = ao_field.selection(self.env) if callable(ao_field.selection) else ao_field.selection
                        keys = [k for k, _ in (sel or [])]
                    except Exception:
                        keys = []
                    preferred = None
                    for opt in ['pos', 'both', 'orders', 'all', 'any']:
                        if opt in keys:
                            preferred = opt
                            break
                    if preferred:
                        create_vals['applies_on'] = preferred
                if 'company_id' in program_model._fields:
                    create_vals['company_id'] = self.env.company.id
                if 'active' in program_model._fields:
                    create_vals['active'] = True
                program = program_model.create(create_vals)
                _logger.info("[FIDELITE] LOYALTY: Programme créé à la volée id=%s", program.id)
            except Exception as e:
                _logger.warning("[FIDELITE] LOYALTY: Impossible de créer un programme à la volée: %s", str(e))

        # Construire le domaine pour trouver la carte
        domain = [('partner_id', '=', partner.id)]
        program_field_name = None
        try:
            # Déterminer dynamiquement le champ du programme (souvent 'program_id')
            if 'program_id' in card_model._fields and program:
                program_field_name = 'program_id'
                domain.append((program_field_name, '=', program.id))
            elif 'program_id' in card_model._fields and not program and getattr(card_model._fields['program_id'], 'required', False):
                _logger.warning("[FIDELITE] LOYALTY: Aucun programme disponible alors que loyalty.card.program_id est requis. Configurez un programme de fidélité (PoS) pour activer la création des cartes.")
                return False
        except Exception:
            pass

        # Rechercher ou créer la carte
        _logger.info("[FIDELITE] LOYALTY: Recherche carte avec domaine=%s", domain)
        card = card_model.search(domain, limit=1)
        if not card:
            vals = {'partner_id': partner.id}
            if program and program_field_name:
                vals[program_field_name] = program.id
            try:
                _logger.info("[FIDELITE] LOYALTY: Création de la carte avec valeurs=%s", vals)
                card = card_model.create(vals)
                _logger.info("[FIDELITE] LOYALTY: Carte créée id=%s", card.id)
            except Exception as e:
                _logger.warning("[FIDELITE] Impossible de créer la carte de fidélité: %s", str(e))
                return False

        # Déterminer le champ des points sur la carte et incrémenter
        possible_point_fields = ['points', 'points_balance', 'points_total', 'points_available']
        point_field = next((f for f in possible_point_fields if f in card._fields), None)
        if not point_field:
            _logger.warning("[FIDELITE] Aucun champ de points reconnu sur loyalty.card: %s", list(card._fields.keys()))
            return False

        try:
            current = card[point_field] or 0
            new_val = current + points_to_add
            _logger.info("[FIDELITE] LOYALTY: Crédit carte id=%s champ=%s avant=%s +ajout=%s => après=%s", card.id, point_field, current, points_to_add, new_val)
            card.write({point_field: new_val})
            _logger.info("[FIDELITE] Carte de fidélité créditée (+%s) pour %s sur champ %s", points_to_add, partner.name, point_field)
            return True
        except Exception as e:
            _logger.warning("[FIDELITE] Échec de l'incrément des points sur loyalty.card: %s", str(e))
            return False

    @api.model
    def migrate_points_to_loyalty_cards(self):
        """Migre les points de la table personnalisée vers les cartes de fidélité natives.

        Pour chaque enregistrement `take_a_way_loyalty.points_utilisateur`, crée (si besoin)
        une `loyalty.card` pour le partenaire et affecte le total de points.
        """
        try:
            card_model = self.env['loyalty.card']
        except Exception:
            _logger.warning("[FIDELITE] Module loyalty non disponible, migration annulée")
            return False

        # Choisir un programme par défaut si possible
        program = False
        try:
            program_model = self.env['loyalty.program']
            prog_domain = []
            if 'applies_on' in program_model._fields:
                prog_domain = [('applies_on', 'in', ['pos', 'both'])]
            program = program_model.search(prog_domain or [], limit=1)
        except Exception:
            program = False

        # Déterminer champs
        program_field_name = 'program_id' if 'program_id' in card_model._fields else None
        possible_point_fields = ['points', 'points_balance', 'points_total', 'points_available']
        point_field = next((f for f in possible_point_fields if f in card_model._fields), None)
        if not point_field:
            _logger.warning("[FIDELITE] Aucun champ points utilisable sur loyalty.card, migration annulée")
            return False

        migrated = 0
        for rec in self.env['take_a_way_loyalty.points_utilisateur'].search([]):
            partner = rec.utilisateur_id
            if not partner:
                continue
            domain = [('partner_id', '=', partner.id)]
            if program and program_field_name:
                domain.append((program_field_name, '=', program.id))
            card = card_model.search(domain, limit=1)
            if not card:
                vals = {'partner_id': partner.id}
                if program and program_field_name:
                    vals[program_field_name] = program.id
                try:
                    card = card_model.create(vals)
                except Exception as e:
                    _logger.warning("[FIDELITE] Création carte échouée pour %s: %s", partner.name, str(e))
                    continue
            try:
                card.write({point_field: rec.points_total or 0})
                migrated += 1
            except Exception as e:
                _logger.warning("[FIDELITE] Écriture des points échouée pour %s: %s", partner.name, str(e))

        _logger.info("[FIDELITE] Migration vers loyalty.card terminée: %s cartes mises à jour", migrated)
        return True

    def action_ajouter_participant(self, partner_id):
        """Ajoute un participant à la mission."""
        if not partner_id:
            return False

        # Vérifier si le participant existe déjà
        existing_participant = self.env['take_a_way_loyalty.mission_user'].search([
            ('mission_id', '=', self.id),
            ('utilisateur_id', '=', partner_id)
        ], limit=1)

        if existing_participant:
            return existing_participant

        # Créer l'enregistrement des points si nécessaire
        points_record = self.env['take_a_way_loyalty.points_utilisateur'].search([
            ('utilisateur_id', '=', partner_id)
        ], limit=1)

        if not points_record:
            try:
                points_record = self.env['take_a_way_loyalty.points_utilisateur'].create({
                    'utilisateur_id': partner_id,
                    'points_total': 0
                })
            except Exception as e:
                _logger.error("Erreur lors de la création des points utilisateur: %s", str(e))
                # Si la création échoue, on continue quand même avec la création du participant

        # Créer le participant
        try:
            participant = self.env['take_a_way_loyalty.mission_user'].create({
                'mission_id': self.id,
                'utilisateur_id': partner_id,
                'date_debut': fields.Date.today(),
                'progression': 0,
                'etat': 'en_cours'
            })
            return participant
        except Exception as e:
            _logger.error("Erreur lors de la création du participant: %s", str(e))
            return False

    def action_reinitialiser_mission(self):
        """Action pour réinitialiser manuellement une mission cumulable"""
        self.ensure_one()
        if not self.mission_id.cumulable:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Mission non cumulable',
                    'message': 'Cette mission n\'est pas cumulable et ne peut pas être réinitialisée.',
                    'type': 'warning',
                }
            }
        
        self._reset_mission_progression()
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Mission réinitialisée',
                'message': f'La mission "{self.mission_id.name}" a été réinitialisée et peut être complétée à nouveau.',
                'type': 'success',
            }
        }

    def action_verifier_repetition(self):
        """Vérifie si une mission peut être répétée"""
        self.ensure_one()
        if self.mission_id.cumulable:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Mission cumulable',
                    'message': f'Cette mission peut être complétée plusieurs fois. État actuel: {self.etat}',
                    'type': 'info',
                }
            }
        else:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Mission non cumulable',
                    'message': f'Cette mission ne peut être complétée qu\'une seule fois. État actuel: {self.etat}',
                    'type': 'info',
                }
            }

class TypeMission(models.Model):
    _name = 'take_a_way_loyalty.type_mission'
    _description = 'Type de mission'
    _rec_name = 'libelle'  # Définir libelle comme champ d'affichage par défaut

    code = fields.Char(string='Code', required=True)
    libelle = fields.Char(string='Libellé', required=True)

    _sql_constraints = [
        ('code_unique', 'UNIQUE(code)', 'Le code du type de mission doit être unique!')
    ]

    def name_get(self):
        result = []
        for record in self:
            result.append((record.id, record.libelle))
        return result

class ConditionMission(models.Model):
    _name = 'take_a_way_loyalty.condition_mission'
    _description = 'Conditions des missions'

    mission_id = fields.Many2one('take_a_way_loyalty.mission', string='Mission', required=True)
    type_condition = fields.Many2one('take_a_way_loyalty.type_mission', string='Type de condition', required=True)
    categorieProduit_id = fields.Many2one('pos.category', string='Catégorie PoS')
    quantite = fields.Integer(string='Quantité')
    montant_minimum = fields.Float(string='Montant minimum')
    nombre_commandes = fields.Integer(string='Nombre de commandes')
    delai_jours = fields.Integer(string='Délai en jours')

    # Champs pour la mission consécutive
    type_periode = fields.Selection([
        ('quotidien', 'Quotidien'),
        ('hebdomadaire', 'Hebdomadaire'),
        ('mensuel', 'Mensuel')
    ], string='Type de période')
    
    nombre_periodes = fields.Integer(string='Nombre de périodes consécutives')
    
    commandes_par_periode = fields.Integer(string='Nombre de commandes par période')
    
    montant_par_periode = fields.Float(string='Montant minimum par période')
    
    type_objectif = fields.Selection([
        ('commandes', 'Nombre de commandes'),
        ('montant', 'Montant total')
    ], string='Type d\'objectif', default='commandes')

    categories_ids = fields.Many2many('pos.category', string='Catégories PoS')
    
    # Champs pour les produits multiples
    produits_ids = fields.Many2many('product.product', string='Produits')
    quantites_produits = fields.One2many('take_a_way_loyalty.quantite_produit', 'condition_id', string='Quantités par produit')

    @api.depends('type_condition.code')
    def _compute_type_condition_code(self):
        for record in self:
            record.type_condition_code = record.type_condition.code if record.type_condition else False

    type_condition_code = fields.Char(compute='_compute_type_condition_code', store=True)

    @api.onchange('type_condition', 'mission_id')
    def _onchange_type_condition(self):
        for record in self:
            if record.type_condition:
                if record.type_condition.code == 'CATEGORIE_PRODUIT':
                    # Pour CATEGORIE_PRODUIT, on peut laisser l'utilisateur choisir les catégories
                    # ou pré-remplir avec les catégories du POS
                    if record.mission_id.pos_config_id:
                        categories = record.mission_id.pos_config_id.iface_available_categ_ids
                        record.categories_ids = [(6, 0, categories.ids)]
                elif record.type_condition.code == 'ACHATS_JOUR':
                    # Pour ACHATS_JOUR, fixer la quantité à 2 (2 achats dans la même journée)
                    record.quantite = 2
                elif record.type_condition.code != 'TOTAL_COMMANDE':
                    record.montant_minimum = 0.0
                elif record.type_condition.code != 'NOMBRE_COMMANDE':
                    record.nombre_commandes = 0

    @api.onchange('produits_ids')
    def _onchange_produits_ids(self):
        """Met à jour automatiquement les quantités par produit quand les produits changent"""
        for record in self:
            if record.type_condition and record.type_condition.code == 'ACHAT_PRODUIT':
                # Supprimer les anciennes quantités
                record.quantites_produits = [(5, 0, 0)]
                
                # Créer de nouvelles quantités pour chaque produit sélectionné
                for produit in record.produits_ids:
                    record.quantites_produits = [(0, 0, {
                        'produit_id': produit.id,
                        'quantite_requise': 1
                    })]
                _logger.warning("[FIDELITE][DEBUG] Quantités créées automatiquement pour %s produits", len(record.produits_ids))

    def action_reinitialiser_categories(self):
        self.ensure_one()
        if self.type_condition.code == 'ACHAT_TOUTES_CATEGORIES':
            categories = self.mission_id.pos_config_id.iface_available_categ_ids
            self.categories_ids = [(6, 0, categories.ids)]
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Catégories réinitialisées',
                    'message': 'Les catégories PdV ont été réinitialisées.',
                    'type': 'info',
                }
            }
        return False

    @api.depends('quantites_produits')
    def _compute_resume_quantites(self):
        """Calcule un résumé des quantités définies pour l'affichage"""
        for record in self:
            if record.type_condition and record.type_condition.code == 'ACHAT_PRODUIT' and record.quantites_produits:
                resume = []
                for quantite_produit in record.quantites_produits:
                    resume.append(f"{quantite_produit.produit_id.name}: {quantite_produit.quantite_requise}")
                record.resume_quantites = ", ".join(resume)
            else:
                record.resume_quantites = ""

    resume_quantites = fields.Char(compute='_compute_resume_quantites', string='Résumé des quantités', store=False)

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        for record in records:
            if record.type_condition and record.mission_id.pos_config_id:
                categories = record.mission_id.pos_config_id.iface_available_categ_ids
                if (
                    record.type_condition.code == 'ACHAT_TOUTES_CATEGORIES'
                    and not record.categories_ids
                ):
                    record.categories_ids = [(6, 0, categories.ids)]
                elif (
                    record.type_condition.code == 'CATEGORIE_PRODUIT'
                    and not record.categories_ids
                ):
                    record.categories_ids = [(6, 0, categories.ids)]
        return records

class PosOrder(models.Model):
    _inherit = 'pos.order'

    # Heure prévue (modifiable après création depuis le backend)
    heure_prevue = fields.Datetime(string='Heure prévue', help='Heure prévue de préparation / retrait / livraison')

    def _check_missions_manual(self):
        """Méthode manuelle pour déclencher la vérification des missions"""
        for order in self:
            _logger.warning("[FIDELITE][DEBUG] _check_missions_manual appelée pour la commande %s", order.id)
        self._check_missions()

    def write(self, vals):
        """Override pour vérifier les missions quand une commande est payée"""
        orders = super(PosOrder, self).write(vals)
        
        # Vérifier si le statut a changé vers un statut de paiement
        if 'state' in vals and vals['state'] in ['paid', 'done', 'invoiced']:
            _logger.warning("[FIDELITE][DEBUG] Valeurs de write: %s", vals)
            for order in self:
                _logger.warning("[FIDELITE][DEBUG] _check_missions appelée pour order %s", order.id)
                order._check_missions(order)
        
        return orders

    def reset_missions_check_flag(self):
        """Réinitialise le flag de vérification des missions pour une commande"""
        for order in self:
            cache_key = f"missions_checked_{order.id}"
            if hasattr(self.env, '_missions_cache') and cache_key in self.env._missions_cache:
                del self.env._missions_cache[cache_key]
                _logger.info("[FIDELITE] Flag de vérification des missions réinitialisé pour la commande %s", order.id)
        return True

    def action_pos_order_paid(self):
        """Override pour vérifier les missions quand une commande est marquée comme payée"""
        _logger.warning("[FIDELITE][DEBUG] action_pos_order_paid appelée pour la commande %s", self.id)
        result = super(PosOrder, self).action_pos_order_paid()
        
        # Vérifier les missions après le paiement
        for order in self:
            _logger.warning("[FIDELITE][DEBUG] Commande POS %s passée au statut 'paid', appel de _check_missions", order.id)
            order._check_missions(order)
        
        return result

    def action_pos_order_invoice(self):
        """Override pour vérifier les missions quand une commande est facturée"""
        _logger.warning("[FIDELITE][DEBUG] action_pos_order_invoice appelée pour la commande %s", self.id)
        result = super(PosOrder, self).action_pos_order_invoice()
        
        # Vérifier les missions après la facturation
        for order in self:
            _logger.warning("[FIDELITE][DEBUG] Commande POS %s passée au statut 'invoiced', appel de _check_missions", order.id)
            order._check_missions(order)
        
        return result

    @api.model_create_multi
    def create(self, vals_list):
        """Override pour vérifier les missions à la création d'une commande POS"""
        orders = super(PosOrder, self).create(vals_list)
        
        for order in orders:
            _logger.warning("[FIDELITE][DEBUG] Commande POS créée: %s avec statut: %s", order.id, order.state)
            
            # Vérifier les missions seulement si la commande est déjà payée
            if order.state in ['paid', 'done', 'invoiced']:
                _logger.warning("[FIDELITE][DEBUG] Commande POS %s créée avec statut de paiement, appel de _check_missions", order.id)
                order._check_missions(order)
        
        return orders

    def _check_missions(self, order):
        """Vérifie les missions pour une commande POS"""
        _logger.warning("[FIDELITE][DEBUG] _check_missions appelée pour order %s", order.id)
        
        # Protection contre les appels multiples pour la même commande
        # Utiliser un cache global au lieu de modifier l'objet
        cache_key = f"missions_checked_{order.id}"
        if hasattr(self.env, '_missions_cache') and cache_key in self.env._missions_cache:
            _logger.warning("[FIDELITE][DEBUG] Missions déjà vérifiées pour cette commande, ignorée")
            return
        
        # Initialiser le cache si nécessaire
        if not hasattr(self.env, '_missions_cache'):
            self.env._missions_cache = {}
        
        # Marquer la commande comme vérifiée
        self.env._missions_cache[cache_key] = True
        
        if not order.partner_id:
            _logger.warning("[FIDELITE][DEBUG] Pas de partenaire associé à la commande")
            return

        _logger.warning("[FIDELITE][DEBUG] Partner de la commande: %s (ID: %s)", order.partner_id.name, order.partner_id.id)

        # Récupérer toutes les missions actives
        missions = self.env['take_a_way_loyalty.mission'].search([])
        _logger.warning("[FIDELITE][DEBUG] Toutes les missions existantes: %s", len(missions))

        # Filtrer les missions dans la période actuelle
        date_actuelle = fields.Date.today()
        missions_periode = []
        for mission in missions:
            _logger.warning("[FIDELITE][DEBUG] Mission: %s (début: %s, fin: %s)", 
                           mission.name, mission.debut, mission.fin)
            if (not mission.debut or mission.debut <= date_actuelle) and \
               (not mission.fin or mission.fin >= date_actuelle):
                missions_periode.append(mission)

        _logger.warning("[FIDELITE][DEBUG] Missions trouvées dans la période: %s", len(missions_periode))

        if not missions_periode:
            _logger.warning("[FIDELITE][DEBUG] Aucune mission active trouvée")
            return

        _logger.warning("[FIDELITE][DEBUG] Vérification des missions pour l'utilisateur: %s (ID: %s)", 
                       order.partner_id.name, order.partner_id.id)

        for mission in missions_periode:
            _logger.warning("[FIDELITE][DEBUG] Vérification de la mission: %s", mission.name)

            # Vérifier si l'utilisateur participe à cette mission
            mission_user = self.env['take_a_way_loyalty.mission_user'].search([
                ('mission_id', '=', mission.id),
                ('utilisateur_id', '=', order.partner_id.id)
            ], limit=1)

            if not mission_user:
                _logger.warning("[FIDELITE][DEBUG] L'utilisateur %s ne participe pas à la mission %s", 
                               order.partner_id.name, mission.name)
                continue

            _logger.warning("[FIDELITE][DEBUG] Mission_user trouvé: %s, progression actuelle: %s", 
                           mission_user.id, mission_user.progression)

            # Vérifier chaque condition de la mission
            for condition in mission.condition_ids:
                _logger.warning("[FIDELITE][DEBUG] Vérification de la condition: %s", condition.type_condition.code)

                if condition.type_condition.code == 'ACHAT_PRODUIT':
                    _logger.warning("[FIDELITE][DEBUG] _check_product_condition appelée")
                    self._check_product_condition(order, condition, mission_user)
                elif condition.type_condition.code == 'TOTAL_COMMANDE':
                    self._check_total_condition(order, condition, mission_user)
                elif condition.type_condition.code == 'NOMBRE_COMMANDE':
                    self._check_order_count_condition(order, condition, mission_user)
                elif condition.type_condition.code == 'CONSECUTIVE':
                    self._check_consecutive_condition(order, condition, mission_user)
                elif condition.type_condition.code == 'ACHATS_JOUR':
                    self._check_achats_jour_condition(order, condition, mission_user)
                elif condition.type_condition.code == 'CATEGORIE_PRODUIT':
                    self._check_categorie_produit_condition(order, condition, mission_user)
                elif condition.type_condition.code == 'ACHAT_TOUTES_CATEGORIES':
                    self._check_categorie_produit_condition(order, condition, mission_user)
                elif condition.type_condition.code == 'PARRAINAGE':
                    self._check_parrainage_condition(order, condition, mission_user)

    def _check_product_condition(self, order, condition, mission_user):
        _logger.warning("[FIDELITE][DEBUG] _check_product_condition appelée")
        _logger.warning("[FIDELITE][DEBUG] Produits définis: %s", condition.produits_ids.mapped('name'))
        _logger.warning("[FIDELITE][DEBUG] Quantités définies: %s", len(condition.quantites_produits))
        
        # Gestion des produits multiples avec quantités définies
        if condition.produits_ids and condition.quantites_produits:
            _logger.warning("[FIDELITE][DEBUG] Utilisation de la logique produits multiples avec quantités définies")
            for quantite_produit in condition.quantites_produits:
                progression_produit = self.env['take_a_way_loyalty.progression_produit'].search([
                    ('mission_user_id', '=', mission_user.id),
                    ('produit_id', '=', quantite_produit.produit_id.id)
                ], limit=1)

                if not progression_produit:
                    progression_produit = self.env['take_a_way_loyalty.progression_produit'].create({
                        'mission_user_id': mission_user.id,
                        'produit_id': quantite_produit.produit_id.id,
                        'quantite_requise': quantite_produit.quantite_requise,
                        'quantite_actuelle': 0
                    })

                # Cumul sur toutes les commandes POS 'paid', 'done', 'invoiced' du participant depuis le début de la mission
                commandes = self.env['pos.order'].search([
                    ('partner_id', '=', order.partner_id.id),
                    ('state', 'in', ['paid', 'done', 'invoiced']),
                    ('date_order', '>=', mission_user.date_debut)
                ])
                _logger.warning("[FIDELITE][DEBUG] Commandes trouvées pour %s: %s", order.partner_id.name, len(commandes))
                quantite_achetee = 0
                for commande in commandes:
                    _logger.warning("[FIDELITE][DEBUG] Commande %s contient:", commande.id)
                    for line in commande.lines:
                        _logger.warning("[FIDELITE][DEBUG]   - %s (qty: %s)", line.product_id.name, line.qty)
                        if line.product_id.id == quantite_produit.produit_id.id:
                            quantite_achetee += line.qty

                progression_produit.write({
                    'quantite_actuelle': quantite_achetee
                })
            # Vérifier si tous les produits ont atteint leur quantité requise
            self.env['take_a_way_loyalty.mission_user']._check_mission_completion(mission_user)
        # Gestion des produits multiples avec quantité globale
        elif condition.produits_ids and not condition.quantites_produits:
            _logger.warning("[FIDELITE][DEBUG] Utilisation de la logique produits multiples avec quantité globale")
            # Utiliser la quantité globale pour tous les produits
            for produit in condition.produits_ids:
                progression_produit = self.env['take_a_way_loyalty.progression_produit'].search([
                    ('mission_user_id', '=', mission_user.id),
                    ('produit_id', '=', produit.id)
                ], limit=1)

                if not progression_produit:
                    progression_produit = self.env['take_a_way_loyalty.progression_produit'].create({
                        'mission_user_id': mission_user.id,
                        'produit_id': produit.id,
                        'quantite_requise': condition.quantite or 1,
                        'quantite_actuelle': 0
                    })

                # Cumul sur toutes les commandes POS 'paid', 'done', 'invoiced' du participant depuis le début de la mission
                commandes = self.env['pos.order'].search([
                    ('partner_id', '=', order.partner_id.id),
                    ('state', 'in', ['paid', 'done', 'invoiced']),
                    ('date_order', '>=', mission_user.date_debut)
                ])
                quantite_achetee = 0
                for commande in commandes:
                    for line in commande.lines:
                        if line.product_id.id == produit.id:
                            quantite_achetee += line.qty

                progression_produit.write({
                    'quantite_actuelle': quantite_achetee
                })
            # Vérifier si tous les produits ont atteint leur quantité requise
            self.env['take_a_way_loyalty.mission_user']._check_mission_completion(mission_user)

    def _check_total_condition(self, order, condition, mission_user):
        if order.amount_total >= condition.montant_minimum:
            mission_user.progression += 1
            self.env['take_a_way_loyalty.mission_user']._check_mission_completion(mission_user)

    def _check_order_count_condition(self, order, condition, mission_user):
        # Utiliser les statuts 'paid', 'done', 'invoiced' pour les commandes POS en Odoo 18
        order_count = self.env['pos.order'].search_count([
            ('partner_id', '=', order.partner_id.id),
            ('state', 'in', ['paid', 'done', 'invoiced']),  # statut correct pour Odoo 18
            ('date_order', '>=', mission_user.date_debut)
        ])
        mission_user.progression = order_count
        self.env['take_a_way_loyalty.mission_user']._check_mission_completion(mission_user)

    def _check_consecutive_condition(self, order, condition, mission_user):
        """Vérifie les conditions de mission consécutive."""
        date_order = fields.Date.from_string(order.date_order)
        if condition.type_periode == 'quotidien':
            periode_debut = date_order
            periode_fin = date_order
        elif condition.type_periode == 'hebdomadaire':
            jour_semaine = date_order.weekday()
            periode_debut = date_order - timedelta(days=jour_semaine)
            periode_fin = periode_debut + timedelta(days=6)
        else:  # mensuel
            periode_debut = date_order.replace(day=1)
            if date_order.month == 12:
                periode_fin = date_order.replace(year=date_order.year + 1, month=1, day=1) - timedelta(days=1)
            else:
                periode_fin = date_order.replace(month=date_order.month + 1, day=1) - timedelta(days=1)

        # Vérifier si une progression existe déjà pour cette période
        progression_periode = self.env['take_a_way_loyalty.progression_periode'].search([
            ('mission_user_id', '=', mission_user.id),
            ('periode_debut', '=', periode_debut),
            ('periode_fin', '=', periode_fin)
        ], limit=1)

        if not progression_periode:
            # Créer une nouvelle progression pour cette période
            progression_periode = self.env['take_a_way_loyalty.progression_periode'].create({
                'mission_user_id': mission_user.id,
                'periode_debut': periode_debut,
                'periode_fin': periode_fin,
                'nombre_commandes': 0,
                'montant_total': 0.0
            })

        # Mettre à jour la progression
        progression_periode.nombre_commandes += 1
        progression_periode.montant_total += order.amount_total

        # Vérifier si l'objectif est atteint pour cette période
        objectif_atteint = False
        if condition.type_objectif == 'commandes':
            objectif_atteint = progression_periode.nombre_commandes >= condition.commandes_par_periode
        else:
            objectif_atteint = progression_periode.montant_total >= condition.montant_par_periode

        if objectif_atteint:
            # Vérifier les périodes précédentes
            limit = max(0, condition.nombre_periodes - 1)
            if limit > 0:
                periodes_precedentes = self.env['take_a_way_loyalty.progression_periode'].search([
                    ('mission_user_id', '=', mission_user.id),
                    ('periode_fin', '<', periode_debut)
                ], order='periode_fin desc', limit=limit)
            else:
                periodes_precedentes = self.env['take_a_way_loyalty.progression_periode'].browse([])

            # Vérifier si toutes les périodes précédentes ont atteint leur objectif
            toutes_periodes_atteintes = True
            for periode in periodes_precedentes:
                if condition.type_objectif == 'commandes':
                    if periode.nombre_commandes < condition.commandes_par_periode:
                        toutes_periodes_atteintes = False
                        break
                else:
                    if periode.montant_total < condition.montant_par_periode:
                        toutes_periodes_atteintes = False
                        break

            if toutes_periodes_atteintes and len(periodes_precedentes) == limit:
                # La mission est complétée - utiliser _check_mission_completion pour centraliser l'attribution des points
                _logger.info("[FIDELITE] CONSECUTIVE - Mission consécutive terminée pour l'utilisateur %s", mission_user.utilisateur_id.name)
                self.env['take_a_way_loyalty.mission_user']._check_mission_completion(mission_user)

    def _check_achats_jour_condition(self, order, condition, mission_user):
        """Vérifie si l'utilisateur a fait 2 achats dans la même journée."""
        # On récupère la date de la commande (sans l'heure)
        date_order = fields.Date.from_string(order.date_order)
        # On compte les commandes 'paid', 'done', 'invoiced' du jour pour ce user
        order_count = self.env['pos.order'].search_count([
            ('partner_id', '=', order.partner_id.id),
            ('state', 'in', ['paid', 'done', 'invoiced']),
            ('date_order', '>=', date_order.strftime('%Y-%m-%d') + " 00:00:00"),
            ('date_order', '<=', date_order.strftime('%Y-%m-%d') + " 23:59:59"),
        ])
        if order_count >= 2:
            mission_user.progression = order_count
            self.env['take_a_way_loyalty.mission_user']._check_mission_completion(mission_user)

    def _check_categorie_produit_condition(self, order, condition, mission_user):
        """Vérifie si l'utilisateur a acheté dans toutes les catégories PoS listées (au moins une fois dans chaque)."""
        if condition.categories_ids:
            # Récupérer toutes les commandes payées depuis le début de la mission
            commandes = self.env['pos.order'].search([
                ('partner_id', '=', order.partner_id.id),
                ('state', 'in', ['paid', 'done', 'invoiced']),
                ('date_order', '>=', mission_user.date_heure_debut)
            ])
            categories_achetees = set()
            for commande in commandes:
                for ligne in commande.lines:
                    tmpl = ligne.product_id.product_tmpl_id
                    # Ajoute toutes les catégories PoS du produit
                    if hasattr(tmpl, 'pos_categ_ids'):
                        categories_achetees.update(tmpl.pos_categ_ids.ids)
            # Log détaillé
            _logger.info("[FIDELITE] CATEGORIE_PRODUIT - Catégories attendues: %s", condition.categories_ids.mapped('name'))
            _logger.info("[FIDELITE] CATEGORIE_PRODUIT - Catégories achetées: %s", list(categories_achetees))
            # Progression = nombre de catégories différentes déjà achetées
            mission_user.progression = len(set(condition.categories_ids.ids) & categories_achetees)
            _logger.info("[FIDELITE] CATEGORIE_PRODUIT - Progression calculée: %s/%s", mission_user.progression, len(condition.categories_ids))
            # Si toutes les catégories sont cochées, mission terminée
            if mission_user.progression == len(condition.categories_ids):
                _logger.info("[FIDELITE] CATEGORIE_PRODUIT - Condition remplie pour l'utilisateur %s (toutes les catégories achetées)", mission_user.utilisateur_id.name)
                self.env['take_a_way_loyalty.mission_user']._check_mission_completion(mission_user)

    def _check_parrainage_condition(self, order, condition, mission_user):
        """Vérifie si l'utilisateur a parrainé le nombre requis de nouveaux clients."""
        # Compter le nombre de filleuls actifs (qui ont fait au moins une commande)
        filleuls_actifs = 0
        
        _logger.warning("[FIDELITE][DEBUG] PARRAINAGE - Vérification pour l'utilisateur %s (ID: %s)", 
                       mission_user.utilisateur_id.name, mission_user.utilisateur_id.id)
        _logger.warning("[FIDELITE][DEBUG] PARRAINAGE - Nombre total de filleuls: %s", 
                       len(mission_user.utilisateur_id.filleuls_ids))
        
        for filleul in mission_user.utilisateur_id.filleuls_ids:
            _logger.warning("[FIDELITE][DEBUG] PARRAINAGE - Vérification du filleul: %s (ID: %s)", 
                           filleul.name, filleul.id)
            
            # Vérifier si le filleul a fait au moins une commande depuis le début de la mission
            # Utiliser les statuts 'paid', 'done' et 'invoiced' pour Odoo 18
            commandes_filleul = self.env['pos.order'].search([
                ('partner_id', '=', filleul.id),
                ('state', 'in', ['paid', 'done', 'invoiced']),
                ('date_order', '>=', mission_user.date_heure_debut)
            ])
            
            _logger.warning("[FIDELITE][DEBUG] PARRAINAGE - Commandes trouvées pour le filleul %s: %s", 
                           filleul.name, len(commandes_filleul))
            
            if commandes_filleul:
                filleuls_actifs += 1
                _logger.warning("[FIDELITE][DEBUG] PARRAINAGE - Filleul %s est actif (a fait des commandes)", 
                               filleul.name)
            else:
                _logger.warning("[FIDELITE][DEBUG] PARRAINAGE - Filleul %s n'a pas fait de commandes depuis %s", 
                               filleul.name, mission_user.date_heure_debut)
        
        # Mettre à jour la progression
        mission_user.progression = filleuls_actifs
        
        _logger.info("[FIDELITE] PARRAINAGE - Utilisateur %s a %s filleuls actifs sur %s requis", 
                    mission_user.utilisateur_id.name, filleuls_actifs, condition.quantite or 1)
        
        # Vérifier si la condition est remplie
        if filleuls_actifs >= (condition.quantite or 1):
            _logger.info("[FIDELITE] PARRAINAGE - Condition remplie pour l'utilisateur %s", mission_user.utilisateur_id.name)
            self.env['take_a_way_loyalty.mission_user']._check_mission_completion(mission_user)

    def action_set_heure_prevue(self):
        """Action pour définir l'heure prévue de la commande"""
        self.ensure_one()
        
        # Créer un wizard pour définir l'heure prévue
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'heure.prevue.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_pos_order_id': self.id,
                'default_heure_prevue': self.heure_prevue or fields.Datetime.now(),
            }
        }

    def action_set_heure_prevue_rapide(self):
        """Action rapide pour définir l'heure prévue (dans 1 heure par défaut)"""
        self.ensure_one()
        
        # Définir l'heure prévue dans 1 heure par défaut
        heure_prevue = fields.Datetime.now() + timedelta(hours=1)
        self.write({'heure_prevue': heure_prevue})
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Heure prévue définie',
                'message': f'Heure prévue définie à {heure_prevue.strftime("%d/%m/%Y %H:%M")}',
                'type': 'success',
            }
        }

    def action_clear_heure_prevue(self):
        """Action pour effacer l'heure prévue"""
        self.ensure_one()
        
        self.write({'heure_prevue': False})
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Heure prévue effacée',
                'message': 'L\'heure prévue a été effacée',
                'type': 'info',
            }
        }

    @api.model
    def _create_heure_prevue_actions(self):
        """Crée automatiquement les actions pour l'heure prévue"""
        try:
            # Action pour définir l'heure prévue
            action_set = self.env['ir.actions.server'].search([
                ('name', '=', 'Définir heure prévue'),
                ('model_id.model', '=', 'pos.order')
            ], limit=1)
            
            if not action_set:
                action_set = self.env['ir.actions.server'].create({
                    'name': 'Définir heure prévue',
                    'model_id': self.env['ir.model'].search([('model', '=', 'pos.order')], limit=1).id,
                    'state': 'code',
                    'code': 'if records:\n    records.action_set_heure_prevue()',
                    'binding_model_id': self.env['ir.model'].search([('model', '=', 'pos.order')], limit=1).id,
                    'binding_view_types': 'form',
                })
                _logger.info("Action 'Définir heure prévue' créée")
            
            # Action rapide pour définir l'heure prévue dans 1 heure
            action_rapide = self.env['ir.actions.server'].search([
                ('name', '=', 'Heure prévue +1h'),
                ('model_id.model', '=', 'pos.order')
            ], limit=1)
            
            if not action_rapide:
                action_rapide = self.env['ir.actions.server'].create({
                    'name': 'Heure prévue +1h',
                    'model_id': self.env['ir.model'].search([('model', '=', 'pos.order')], limit=1).id,
                    'state': 'code',
                    'code': 'if records:\n    records.action_set_heure_prevue_rapide()',
                    'binding_model_id': self.env['ir.model'].search([('model', '=', 'pos.order')], limit=1).id,
                    'binding_view_types': 'form',
                })
                _logger.info("Action 'Heure prévue +1h' créée")
            
            # Action pour effacer l'heure prévue
            action_clear = self.env['ir.actions.server'].search([
                ('name', '=', 'Effacer heure prévue'),
                ('model_id.model', '=', 'pos.order')
            ], limit=1)
            
            if not action_clear:
                action_clear = self.env['ir.actions.server'].create({
                    'name': 'Effacer heure prévue',
                    'model_id': self.env['ir.model'].search([('model', '=', 'pos.order')], limit=1).id,
                    'state': 'code',
                    'code': 'if records:\n    records.action_clear_heure_prevue()',
                    'binding_model_id': self.env['ir.model'].search([('model', '=', 'pos.order')], limit=1).id,
                    'binding_view_types': 'form',
                })
                _logger.info("Action 'Effacer heure prévue' créée")
            
            return True
            
        except Exception as e:
            _logger.error(f"Erreur lors de la création des actions: {str(e)}")
            return False

class QuantiteProduit(models.Model):
    _name = 'take_a_way_loyalty.quantite_produit'
    _description = 'Quantité requise par produit pour une condition de mission'

    condition_id = fields.Many2one('take_a_way_loyalty.condition_mission', string='Condition', required=True)
    produit_id = fields.Many2one('product.product', string='Produit', required=True)
    quantite_requise = fields.Integer(string='Quantité requise', required=True, default=1)

    _sql_constraints = [
        ('unique_produit_condition', 'UNIQUE(condition_id, produit_id)', 
         'Un produit ne peut être défini qu\'une seule fois par condition!')
    ]

class ProgressionProduit(models.Model):
    _name = 'take_a_way_loyalty.progression_produit'
    _description = 'Progression par produit pour une mission'

    mission_user_id = fields.Many2one('take_a_way_loyalty.mission_user', string='Mission Utilisateur', required=True)
    produit_id = fields.Many2one('product.product', string='Produit', required=True)
    quantite_requise = fields.Integer(string='Quantité requise', required=True)
    quantite_actuelle = fields.Integer(string='Quantité actuelle', default=0)

    _sql_constraints = [
        ('unique_produit_mission', 'UNIQUE(mission_user_id, produit_id)', 
         'Un produit ne peut être suivi qu\'une seule fois par mission!')
    ]

class ResPartner(models.Model):
    _inherit = 'res.partner'

    mission_id = fields.Many2one('take_a_way_loyalty.mission', string='Mission', ondelete='cascade')
    
    # Champs pour le système de parrainage
    code_parrainage = fields.Char(string='Code de parrainage', readonly=True, copy=False, help='Code unique généré automatiquement pour le parrainage')
    parrain_id = fields.Many2one('res.partner', string='Parrain', domain=[('is_company', '=', False), ('type', '=', 'contact')], help='Contact qui a parrainé ce client')
    filleuls_ids = fields.One2many('res.partner', 'parrain_id', string='Filleuls', help='Clients parrainés par ce contact')
    nombre_filleuls = fields.Integer(string='Nombre de filleuls', compute='_compute_nombre_filleuls', store=True)
    
    _sql_constraints = [
        ('unique_code_parrainage', 'UNIQUE(code_parrainage)', 'Le code de parrainage doit être unique!')
    ]
    
    @api.depends('filleuls_ids')
    def _compute_nombre_filleuls(self):
        for partner in self:
            partner.nombre_filleuls = len(partner.filleuls_ids)
    
    def _generate_parrainage_code(self):
        """Génère un code de parrainage unique de 6 chiffres"""
        import random
        while True:
            code = ''.join([str(random.randint(0, 9)) for _ in range(6)])
            # Vérifier que le code n'existe pas déjà
            existing = self.search([('code_parrainage', '=', code)], limit=1)
            if not existing:
                return code
    
    def action_utiliser_code_parrainage(self, code_parrainage):
        """Utilise un code de parrainage pour définir le parrain"""
        if not code_parrainage:
            return False
        
        # Rechercher le parrain par son code
        parrain = self.search([('code_parrainage', '=', code_parrainage)], limit=1)
        
        if not parrain:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Code invalide',
                    'message': 'Le code de parrainage saisi n\'existe pas.',
                    'type': 'warning',
                }
            }
        
        if parrain.id == self.id:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Code invalide',
                    'message': 'Vous ne pouvez pas vous parrainer vous-même.',
                    'type': 'warning',
                }
            }
        
        # Définir le parrain
        self.parrain_id = parrain.id
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Parrainage effectué',
                'message': f'Vous avez été parrainé par {parrain.name}.',
                'type': 'success',
            }
        }
    
    @api.model_create_multi
    def create(self, vals_list):
        """Surcharge de la méthode create pour générer le code de parrainage et ajouter automatiquement les nouveaux contacts aux missions actives"""
        partners = super(ResPartner, self).create(vals_list)
        
        for partner in partners:
            # Générer un code de parrainage pour les nouveaux contacts
            if not partner.is_company and partner.type == 'contact' and not partner.code_parrainage:
                partner.code_parrainage = partner._generate_parrainage_code()
                
            # Vérifier si c'est un contact (pas une entreprise)
            if not partner.is_company and partner.type == 'contact':
                _logger.info("[FIDELITE] Nouveau contact créé: %s (ID: %s), ajout automatique aux missions actives", 
                           partner.name, partner.id)
                
                # Récupérer toutes les missions actives
                active_missions = self.env['take_a_way_loyalty.mission'].search([
                    ('debut', '<=', fields.Date.today()),
                    ('fin', '>=', fields.Date.today()),
                ])
                
                _logger.info("[FIDELITE] Missions actives trouvées: %s", len(active_missions))
                
                for mission in active_missions:
                    try:
                        # Vérifier si le contact est déjà participant à cette mission
                        existing_participant = self.env['take_a_way_loyalty.mission_user'].search([
                            ('mission_id', '=', mission.id),
                            ('utilisateur_id', '=', partner.id)
                        ], limit=1)
                        
                        if not existing_participant:
                            # Créer l'enregistrement des points si nécessaire
                            points_record = self.env['take_a_way_loyalty.points_utilisateur'].search([
                                ('utilisateur_id', '=', partner.id)
                            ], limit=1)
                            
                            if not points_record:
                                points_record = self.env['take_a_way_loyalty.points_utilisateur'].create({
                                    'utilisateur_id': partner.id,
                                    'points_total': 0
                                })
                            
                            # Ajouter le contact comme participant à la mission
                            mission_user = self.env['take_a_way_loyalty.mission_user'].create({
                                'mission_id': mission.id,
                                'utilisateur_id': partner.id,
                                'date_debut': fields.Date.today(),
                                'progression': 0,
                                'etat': 'en_cours'
                            })
                            
                            _logger.info("[FIDELITE] Contact %s ajouté automatiquement à la mission %s", 
                                       partner.name, mission.name)
                        else:
                            _logger.info("[FIDELITE] Contact %s déjà participant à la mission %s", 
                                       partner.name, mission.name)
                            
                    except Exception as e:
                        _logger.error("[FIDELITE] Erreur lors de l'ajout automatique du contact %s à la mission %s: %s",
                                    partner.name, mission.name, str(e))
        
        return partners

    def action_ajouter_participant(self):
        """Ajoute le client comme participant à la mission."""
        if not self.mission_id:
            return False
        return self.mission_id.action_ajouter_participant(self.id)

class ProgressionPeriode(models.Model):
    _name = 'take_a_way_loyalty.progression_periode'
    _description = 'Progression par période pour une mission consécutive'

    mission_user_id = fields.Many2one('take_a_way_loyalty.mission_user', string='Mission Utilisateur', required=True)
    periode_debut = fields.Date(string='Début de la période', required=True)
    periode_fin = fields.Date(string='Fin de la période', required=True)
    nombre_commandes = fields.Integer(string='Nombre de commandes', default=0)
    montant_total = fields.Float(string='Montant total', default=0.0)

    _sql_constraints = [
        ('unique_periode_mission', 'UNIQUE(mission_user_id, periode_debut, periode_fin)', 
         'Une période ne peut être suivie qu\'une seule fois par mission!')
    ]

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    disponibilite_inventaire = fields.Boolean(string='Disponible en inventaire', default=True)

    def _get_pos_products_domain(self):
        """Surcharge pour filtrer les produits disponibles dans le PoS"""
        _logger.info("[DISPO_POS] ProductTemplate._get_pos_products_domain appelée")
        
        domain = super(ProductTemplate, self)._get_pos_products_domain()
        
        _logger.info("[DISPO_POS] ProductTemplate domaine initial: %s", domain)
        
        # Ajouter le filtre de disponibilité
        domain += [('disponibilite_inventaire', '=', True)]
        
        _logger.info("[DISPO_POS] ProductTemplate domaine final: %s", domain)
        return domain

    @api.model
    def _get_pos_products(self, pos_config_id=None):
        """Surcharge pour retourner les produits disponibles pour le PoS"""
        _logger.info("[DISPO_POS] ProductTemplate._get_pos_products appelée avec pos_config_id: %s", pos_config_id)
        
        domain = self._get_pos_products_domain()
        
        _logger.info("[DISPO_POS] ProductTemplate domaine final: %s", domain)
        products = self.search(domain)
        _logger.info("[DISPO_POS] ProductTemplate nombre de produits retournés: %s", len(products))
        
        return products

    def write(self, vals):
        """Surcharge pour forcer le rechargement des sessions PoS quand la disponibilité change"""
        result = super(ProductTemplate, self).write(vals)
        
        # Si la disponibilité a changé, forcer le rechargement des sessions PoS actives
        if 'disponibilite_inventaire' in vals:
            _logger.info("[DISPO_POS] Disponibilité changée pour %s: %s", self.mapped('name'), vals['disponibilite_inventaire'])
            
            # Récupérer toutes les sessions PoS actives
            active_sessions = self.env['pos.session'].search([
                ('state', '=', 'opened')
            ])
            
            for session in active_sessions:
                try:
                    session.force_reload_products()
                except Exception as e:
                    _logger.error("[DISPO_POS] Erreur lors du rechargement de la session %s: %s", session.id, str(e))
        
        return result


class PosConfig(models.Model):
    _inherit = 'pos.config'

    def _get_available_products(self):
        """Surcharge pour filtrer les produits disponibles dans le PoS"""
        _logger.info("[DISPO_POS] PosConfig._get_available_products appelée pour la config %s", self.id)
        
        products = super(PosConfig, self)._get_available_products()
        
        _logger.info("[DISPO_POS] Nombre de produits avant filtrage: %s", len(products))
        
        # Filtrer les produits non disponibles
        available_products = products.filtered(lambda p: p.product_tmpl_id.disponibilite_inventaire)
        
        _logger.info("[DISPO_POS] Nombre de produits après filtrage: %s", len(available_products))
        
        return available_products

    def _get_products_domain(self):
        """Surcharge pour ajouter le filtre de disponibilité au domaine des produits"""
        _logger.info("[DISPO_POS] PosConfig._get_products_domain appelée pour la config %s", self.id)
        
        domain = super(PosConfig, self)._get_products_domain()
        
        _logger.info("[DISPO_POS] Domaine initial: %s", domain)
        
        # Ajouter le filtre de disponibilité
        domain += [('product_tmpl_id.disponibilite_inventaire', '=', True)]
        
        _logger.info("[DISPO_POS] Domaine final: %s", domain)
        return domain


class PosSession(models.Model):
    _inherit = 'pos.session'

    def _loader_params_product_product(self):
        """Surcharge pour filtrer les produits non disponibles lors du chargement de la session PoS"""
        _logger.info("[DISPO_POS] _loader_params_product_product appelée pour la session %s", self.id)
        
        params = super(PosSession, self)._loader_params_product_product()
        
        _logger.info("[DISPO_POS] Paramètres initiaux: %s", params)
        
        # Ajouter le filtre de disponibilité au domaine
        # Selon la version d'Odoo, les paramètres peuvent contenir directement
        # une clé 'domain' (liste) ou une clé imbriquée 'search_params' avec un 'domain'.
        try:
            if 'search_params' in params:
                search_params = params['search_params'] or {}
                existing_domain = search_params.get('domain') or []
                # S'assurer que le domaine est une liste
                if not isinstance(existing_domain, list):
                    _logger.warning("[DISPO_POS] Domaine inattendu (type %s) dans search_params, remplacement par liste",
                                    type(existing_domain))
                    existing_domain = []
                search_params['domain'] = existing_domain + [('product_tmpl_id.disponibilite_inventaire', '=', True)]
                params['search_params'] = search_params
            elif 'domain' in params:
                existing_domain = params.get('domain') or []
                if not isinstance(existing_domain, list):
                    _logger.warning("[DISPO_POS] Domaine inattendu (type %s) dans params, remplacement par liste",
                                    type(existing_domain))
                    existing_domain = []
                params['domain'] = existing_domain + [('product_tmpl_id.disponibilite_inventaire', '=', True)]
            else:
                params['domain'] = [('product_tmpl_id.disponibilite_inventaire', '=', True)]
        except Exception as e:
            _logger.error("[DISPO_POS] Erreur lors de l'ajout du filtre de disponibilité au domaine: %s", str(e))
        
        _logger.info("[DISPO_POS] Paramètres finaux: %s", params)
        return params

    def _get_pos_products_domain(self):
        """Surcharge pour ajouter le filtre de disponibilité au domaine des produits PoS"""
        _logger.info("[DISPO_POS] _get_pos_products_domain appelée pour la session %s", self.id)
        
        domain = super(PosSession, self)._get_pos_products_domain()
        
        _logger.info("[DISPO_POS] Domaine initial: %s", domain)
        
        # Ajouter le filtre de disponibilité
        domain += [('product_tmpl_id.disponibilite_inventaire', '=', True)]
        
        _logger.info("[DISPO_POS] Domaine final: %s", domain)
        return domain

    def force_reload_products(self):
        """Force le rechargement des produits dans la session PoS"""
        try:
            # Invalider le cache en modifiant un champ de la session
            self.write({'update_stock_at_closing': self.update_stock_at_closing})
            _logger.info("[DISPO_POS] Session PoS %s forcée pour rechargement", self.id)
            return True
        except Exception as e:
            _logger.error("[DISPO_POS] Erreur lors du rechargement forcé de la session %s: %s", self.id, str(e))
            return False

    def _load_model_data(self, model_name, domain=None, fields=None):
        """Surcharge pour filtrer les produits lors du chargement des données"""
        _logger.info("[DISPO_POS] _load_model_data appelée pour model_name: %s", model_name)
        
        if model_name == 'product.product':
            _logger.info("[DISPO_POS] _load_model_data appelée pour product.product")
            if domain is None:
                domain = []
            domain += [('product_tmpl_id.disponibilite_inventaire', '=', True)]
            _logger.info("[DISPO_POS] Domaine modifié pour product.product: %s", domain)
        
        result = super(PosSession, self)._load_model_data(model_name, domain, fields)
        _logger.info("[DISPO_POS] _load_model_data résultat pour %s: %s", model_name, len(result) if isinstance(result, list) else result)
        return result

    def load_data(self, models_to_load=None):
        """Surcharge pour ajouter des logs lors du chargement des données"""
        _logger.info("[DISPO_POS] load_data appelée pour la session %s", self.id)
        _logger.info("[DISPO_POS] models_to_load: %s", models_to_load)
        
        result = super(PosSession, self).load_data(models_to_load)
        
        # Analyser la structure des données retournées
        _logger.info("[DISPO_POS] Clés dans result: %s", list(result.keys()) if isinstance(result, dict) else "Non dict")
        
        # Filtrer les produits non disponibles dans le résultat
        if 'product.product' in result:
            _logger.info("[DISPO_POS] Filtrage des produits dans load_data")
            products = result['product.product']

            # Analyser le type et la structure
            _logger.info("[DISPO_POS] Type de products: %s", type(products))
            if isinstance(products, dict):
                _logger.info("[DISPO_POS] Clés dans products: %s", list(products.keys()))
                data_block = products.get('data')
                if isinstance(data_block, dict):
                    try:
                        product_ids = [int(pid) for pid in data_block.keys()]
                    except Exception:
                        product_ids = list(data_block.keys())

                    allowed_ids = set(
                        self.env['product.product']
                        .browse(product_ids)
                        .filtered(lambda p: p.product_tmpl_id.disponibilite_inventaire)
                        .ids
                    )
                    before = len(data_block)
                    filtered_dict = {
                        pid: vals for pid, vals in data_block.items() if (int(pid) if isinstance(pid, str) and pid.isdigit() else pid) in allowed_ids
                    }
                    result['product.product']['data'] = filtered_dict
                    _logger.info("[DISPO_POS] load_data dict filtré: %s -> %s (exclus: %s)", before, len(filtered_dict), list(set(product_ids) - allowed_ids))
                else:
                    # Cas Odoo 18: data est une liste de lignes alignées avec 'fields'
                    _logger.info("[DISPO_POS] products['data'] est une liste (%s), tentative de filtrage par fields", type(data_block))
                    fields_meta = products.get('fields')
                    if isinstance(fields_meta, list):
                        field_names = fields_meta
                    elif isinstance(fields_meta, dict):
                        field_names = list(fields_meta.keys())
                    else:
                        field_names = []

                    # Debug: tracer les champs et un échantillon de ligne
                    try:
                        sample_row = data_block[0] if isinstance(data_block, list) and data_block else None
                        _logger.info("[DISPO_POS] fields=%s", field_names)
                        _logger.info("[DISPO_POS] sample_row_type=%s len=%s", type(sample_row), (len(sample_row) if isinstance(sample_row, (list, tuple)) else None))
                        if isinstance(sample_row, (list, tuple)):
                            _logger.info("[DISPO_POS] sample_row_first_8=%s", sample_row[:8])
                    except Exception as e_dbg:
                        _logger.warning("[DISPO_POS] Debug fields/sample_row logging error: %s", str(e_dbg))

                    try:
                        idx_id = field_names.index('id') if 'id' in field_names else -1
                    except Exception:
                        idx_id = -1
                    try:
                        idx_tmpl = field_names.index('product_tmpl_id') if 'product_tmpl_id' in field_names else -1
                    except Exception:
                        idx_tmpl = -1

                    before = len(data_block) if isinstance(data_block, list) else 0

                    if isinstance(data_block, list) and before:
                        # Collecter les ids pertinents
                        product_ids = []
                        template_ids = []
                        for row in data_block:
                            if isinstance(row, dict):
                                pid = row.get('id')
                                if isinstance(pid, int):
                                    product_ids.append(pid)
                                v = row.get('product_tmpl_id')
                                if isinstance(v, (list, tuple)) and v:
                                    template_ids.append(v[0])
                                elif isinstance(v, int):
                                    template_ids.append(v)
                            elif isinstance(row, (list, tuple)):
                                if idx_id != -1 and idx_id < len(row):
                                    pid = row[idx_id]
                                    if isinstance(pid, int):
                                        product_ids.append(pid)
                                if idx_tmpl != -1 and idx_tmpl < len(row):
                                    val = row[idx_tmpl]
                                    if isinstance(val, (list, tuple)) and val:
                                        template_ids.append(val[0])
                                    elif isinstance(val, int):
                                        template_ids.append(val)

                        # Construire un set d'ids produits désactivés (plus robuste)
                        disabled_template_ids = set(
                            self.env['product.template']
                            .search([('disponibilite_inventaire', '=', False)])
                            .ids
                        )
                        disabled_product_ids = set()
                        if disabled_template_ids:
                            disabled_product_ids = set(
                                self.env['product.product']
                                .search([('product_tmpl_id', 'in', list(disabled_template_ids))])
                                .ids
                            )

                        filtered_rows = []
                        removed_count = 0
                        for row in data_block:
                            keep = True
                            if isinstance(row, dict):
                                pid = row.get('id') if isinstance(row.get('id'), int) else None
                                v = row.get('product_tmpl_id')
                                tmpl_id = v[0] if isinstance(v, (list, tuple)) and v else (v if isinstance(v, int) else None)
                                if pid is not None and pid in disabled_product_ids:
                                    keep = False
                                if tmpl_id is not None and tmpl_id in disabled_template_ids:
                                    keep = False
                            elif isinstance(row, (list, tuple)):
                                if idx_id != -1 and idx_id < len(row) and isinstance(row[idx_id], int) and row[idx_id] in disabled_product_ids:
                                    keep = False
                                if idx_tmpl != -1 and idx_tmpl < len(row):
                                    val = row[idx_tmpl]
                                    tmpl_id = val[0] if isinstance(val, (list, tuple)) and val else (val if isinstance(val, int) else None)
                                    if tmpl_id is not None and tmpl_id in disabled_template_ids:
                                        keep = False
                            if keep:
                                filtered_rows.append(row)
                            else:
                                removed_count += 1

                        result['product.product']['data'] = filtered_rows
                        _logger.info("[DISPO_POS] load_data list filtré: %s -> %s (supprimés: %s, désactivés: prod=%s, tmpl=%s)", before, len(filtered_rows), removed_count, len(disabled_product_ids), len(disabled_template_ids))
                    else:
                        _logger.info("[DISPO_POS] Impossible de filtrer: fields=%s, idx_id=%s, idx_tmpl=%s", type(fields_meta), idx_id, idx_tmpl)
            elif isinstance(products, list):
                _logger.info("[DISPO_POS] Nombre de produits dans la liste: %s", len(products))
                if products:
                    _logger.info("[DISPO_POS] Premier produit: %s", products[0])
                
                filtered_products = []
                for product in products:
                    if isinstance(product, dict):
                        if product.get('product_tmpl_id'):
                            template_id = product['product_tmpl_id'][0]
                            template = self.env['product.template'].browse(template_id)
                            
                            if template.disponibilite_inventaire:
                                filtered_products.append(product)
                                _logger.info("[DISPO_POS] Produit gardé: %s", product.get('name', 'Unknown'))
                            else:
                                _logger.info("[DISPO_POS] Produit filtré: %s", product.get('name', 'Unknown'))
                        else:
                            filtered_products.append(product)
                            _logger.info("[DISPO_POS] Produit sans template gardé: %s", product.get('name', 'Unknown'))
                    else:
                        filtered_products.append(product)
                        _logger.info("[DISPO_POS] Produit de type %s gardé: %s", type(product), product)
                
                result['product.product'] = filtered_products
                _logger.info("[DISPO_POS] Nombre de produits après filtrage: %s", len(filtered_products))
            else:
                _logger.info("[DISPO_POS] Format inattendu pour products: %s", type(products))
        else:
            _logger.info("[DISPO_POS] Pas de 'product.product' dans le résultat")
        
        _logger.info("[DISPO_POS] load_data terminée pour la session %s", self.id)
        return result

    def _loader_params(self, model_name):
        """Surcharge pour ajouter des logs lors du chargement des paramètres"""
        _logger.info("[DISPO_POS] _loader_params appelée pour model_name: %s", model_name)
        
        result = super(PosSession, self)._loader_params(model_name)
        
        if model_name == 'product.product':
            _logger.info("[DISPO_POS] _loader_params pour product.product: %s", result)
        
        return result


class ProductProduct(models.Model):
    _inherit = 'product.product'

    def _get_pos_products_domain(self):
        """Surcharge pour filtrer les produits disponibles dans le PoS"""
        _logger.info("[DISPO_POS] ProductProduct._get_pos_products_domain appelée")
        
        domain = super(ProductProduct, self)._get_pos_products_domain()
        
        _logger.info("[DISPO_POS] Domaine initial: %s", domain)
        
        # Ajouter le filtre de disponibilité
        domain += [('product_tmpl_id.disponibilite_inventaire', '=', True)]
        
        _logger.info("[DISPO_POS] Domaine final: %s", domain)
        return domain

    @api.model
    def _get_pos_products(self, pos_config_id=None):
        """Surcharge pour retourner les produits disponibles pour le PoS"""
        _logger.info("[DISPO_POS] ProductProduct._get_pos_products appelée avec pos_config_id: %s", pos_config_id)
        
        domain = self._get_pos_products_domain()
        
        # Ajouter les filtres standard du PoS si nécessaire
        if pos_config_id:
            pos_config = self.env['pos.config'].browse(pos_config_id)
            if pos_config.iface_available_categ_ids:
                domain += [('pos_categ_id', 'in', pos_config.iface_available_categ_ids.ids)]
        
        _logger.info("[DISPO_POS] Domaine final pour _get_pos_products: %s", domain)
        products = self.search(domain)
        _logger.info("[DISPO_POS] Nombre de produits retournés: %s", len(products))
        
        return products

    def _get_pos_products_domain_old(self):
        """Ancienne méthode pour compatibilité"""
        _logger.info("[DISPO_POS] ProductProduct._get_pos_products_domain_old appelée")
        return [('product_tmpl_id.disponibilite_inventaire', '=', True)]

    def search_read(self, domain=None, fields=None, offset=0, limit=None, order=None, **kwargs):
        """Surcharge pour filtrer les produits lors des recherches"""
        _logger.info("[DISPO_POS] ProductProduct.search_read appelée")
        _logger.info("[DISPO_POS] Domaine initial search_read: %s", domain)
        _logger.info("[DISPO_POS] Paramètres supplémentaires: %s", kwargs)
        
        if domain is None:
            domain = []
        
        # Ajouter le filtre de disponibilité si ce n'est pas déjà présent
        disponibilite_filter = ('product_tmpl_id.disponibilite_inventaire', '=', True)
        if disponibilite_filter not in domain:
            domain += [disponibilite_filter]
            _logger.info("[DISPO_POS] Filtre de disponibilité ajouté au domaine search_read")
        
        _logger.info("[DISPO_POS] Domaine final search_read: %s", domain)
        
        result = super(ProductProduct, self).search_read(domain, fields, offset, limit, order, **kwargs)
        _logger.info("[DISPO_POS] search_read retourne %s résultats", len(result))
        
        return result

    def _load_pos_data(self, data):
        """Surcharge Odoo 18: filtre les produits après chargement.

        L'API appelle désormais `_load_pos_data(response)` avec `response` (dict)
        en paramètre. On délègue au parent puis on filtre le résultat retourné
        (liste de records sérialisés) en fonction de la disponibilité.
        """
        _logger.info("[DISPO_POS] ProductProduct._load_pos_data appelée (type arg=%s)", type(data))

        # Appel parent avec la signature actuelle
        result = super(ProductProduct, self)._load_pos_data(data)

        # Filtrage défensif du résultat pour ne garder que les produits dont
        # le template est disponible en inventaire
        try:
            # Cas Odoo 18+: structure dict avec clés 'data', 'fields', 'relations'
            if isinstance(result, dict) and 'data' in result:
                data_block = result.get('data')
                # data peut être un dict {product_id: row} ou une liste de rows
                if isinstance(data_block, dict):
                    # Filtrer via les ids de produits (plus robuste, agnostique du format interne des rows)
                    try:
                        product_ids = [int(pid) for pid in data_block.keys()]
                    except Exception:
                        # Si les clés ne sont pas castables en int, on les prend telles quelles
                        product_ids = list(data_block.keys())

                    allowed_ids = set(
                        self.env['product.product']
                        .browse(product_ids)
                        .filtered(lambda p: p.product_tmpl_id.disponibilite_inventaire)
                        .ids
                    )
                    before = len(data_block)
                    result['data'] = {
                        pid: vals for pid, vals in data_block.items() if (int(pid) if isinstance(pid, str) and pid.isdigit() else pid) in allowed_ids
                    }
                    _logger.info("[DISPO_POS] _load_pos_data dict filtré: %s -> %s", before, len(result['data']))

                elif isinstance(data_block, list):
                    # Fallback si 'data' est une liste alignée sur 'fields'
                    fields = result.get('fields') or []
                    try:
                        tmpl_idx = fields.index('product_tmpl_id')
                    except ValueError:
                        tmpl_idx = -1
                    filtered_rows = []
                    before = len(data_block)
                    for row in data_block:
                        template_id = None
                        if isinstance(row, (list, tuple)) and 0 <= tmpl_idx < len(row):
                            val = row[tmpl_idx]
                            if isinstance(val, (list, tuple)) and val:
                                template_id = val[0]
                            elif isinstance(val, int):
                                template_id = val
                        if template_id:
                            if self.env['product.template'].browse(template_id).disponibilite_inventaire:
                                filtered_rows.append(row)
                        else:
                            # Si on ne sait pas déterminer le template, on ne filtre pas par prudence
                            filtered_rows.append(row)
                    result['data'] = filtered_rows
                    _logger.info("[DISPO_POS] _load_pos_data list filtré: %s -> %s", before, len(filtered_rows))

                # Toujours retourner la structure dict attendue par le client PoS
                return result

            if isinstance(result, list):
                # Format classique: liste de dicts sérialisés
                product_ids = []
                for product in result:
                    if isinstance(product, dict) and product.get('id'):
                        product_ids.append(product['id'])
                allowed_ids = set(
                    self.env['product.product']
                    .browse(product_ids)
                    .filtered(lambda p: p.product_tmpl_id.disponibilite_inventaire)
                    .ids
                )
                filtered = [p for p in result if not isinstance(p, dict) or not p.get('id') or p.get('id') in allowed_ids]
                _logger.info("[DISPO_POS] _load_pos_data list filtré par ids: %s -> %s (exclus: %s)",
                             len(result), len(filtered), list(set(product_ids) - allowed_ids))
                return filtered
        except Exception as e:
            _logger.error("[DISPO_POS] Erreur durant le filtrage _load_pos_data: %s", str(e))

        return result

