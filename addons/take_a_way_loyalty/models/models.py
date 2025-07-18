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
        if not mission_user.mission_id.condition_ids:
            _logger.warning("La mission %s n'a pas de conditions", mission_user.mission_id.name)
            return

        conditions_remplies = True
        for condition in mission_user.mission_id.condition_ids:
            if condition.type_condition.code == 'ACHAT_PRODUIT':
                progression_produit = self.env['take_a_way_loyalty.progression_produit'].search([
                    ('mission_user_id', '=', mission_user.id),
                    ('produit_id', '=', condition.produit_id.id)
                ], limit=1)
                if not progression_produit or progression_produit.quantite_actuelle < progression_produit.quantite_requise:
                    conditions_remplies = False
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

        if conditions_remplies and mission_user.etat == 'en_cours':
            mission_user.etat = 'termine'
            points_record = self.env['take_a_way_loyalty.points_utilisateur'].search([
                ('utilisateur_id', '=', mission_user.utilisateur_id.id)
            ], limit=1)
            if not points_record:
                points_record = self.env['take_a_way_loyalty.points_utilisateur'].create({
                    'utilisateur_id': mission_user.utilisateur_id.id,
                    'points_total': 0
                })
            points_record.points_total += mission_user.mission_id.point_recompense

    def _set_default_values(self, vals):
        """Définit les valeurs par défaut pour la création."""
        if 'date_debut' not in vals:
            vals['date_debut'] = fields.Date.today()
        if 'progression' not in vals:
            vals['progression'] = 0
        return vals

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
    produit_id = fields.Many2one('product.product', string='Produit')
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
                elif record.type_condition.code != 'ACHAT_PRODUIT':
                    record.produit_id = False
                elif record.type_condition.code != 'TOTAL_COMMANDE':
                    record.montant_minimum = 0.0
                elif record.type_condition.code != 'NOMBRE_COMMANDE':
                    record.nombre_commandes = 0

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

    def _check_missions_manual(self):
        """Méthode manuelle pour déclencher la vérification des missions"""
        for order in self:
            _logger.warning("[FIDELITE][DEBUG] _check_missions_manual appelée pour la commande %s", order.id)
        self._check_missions()

    def write(self, vals):
        result = super(PosOrder, self).write(vals)
        
        # Vérifier différents statuts possibles pour les commandes POS payées
        if vals.get('state') in ['paid', 'done', 'invoiced']:
            for order in self:
                _logger.warning("[FIDELITE][DEBUG] Commande POS %s passée au statut '%s', appel de _check_missions", order.id, vals.get('state'))
            _logger.warning("[FIDELITE][DEBUG] Valeurs de write: %s", vals)
            self._check_missions()
        else:
            for order in self:
                _logger.warning("[FIDELITE][DEBUG] Commande POS %s - statut: %s (pas un statut de paiement)", order.id, vals.get('state'))
        return result

    def action_pos_order_paid(self):
        """Méthode appelée quand une commande POS est payée"""
        for order in self:
            _logger.warning("[FIDELITE][DEBUG] action_pos_order_paid appelée pour la commande %s", order.id)
        result = super(PosOrder, self).action_pos_order_paid()
        self._check_missions()
        return result

    def action_pos_order_invoice(self):
        """Méthode appelée quand une facture est créée pour une commande POS"""
        for order in self:
            _logger.warning("[FIDELITE][DEBUG] action_pos_order_invoice appelée pour la commande %s", order.id)
        result = super(PosOrder, self).action_pos_order_invoice()
        self._check_missions()
        return result

    @api.model_create_multi
    def create(self, vals_list):
        """Surcharge de la méthode create pour vérifier les commandes POS créées"""
        orders = super(PosOrder, self).create(vals_list)
        for order in orders:
            _logger.warning("[FIDELITE][DEBUG] Commande POS créée: %s avec statut: %s", order.id, order.state)
            if order.state in ['paid', 'done', 'invoiced']:
                _logger.warning("[FIDELITE][DEBUG] Commande POS %s créée avec statut de paiement, appel de _check_missions", order.id)
                order._check_missions()
        return orders

    def _check_missions(self):
        for order in self:
            _logger.warning("[FIDELITE][DEBUG] _check_missions appelée pour order %s", order.id)
            _logger.warning("[FIDELITE][DEBUG] Partner de la commande: %s (ID: %s)", order.partner_id.name, order.partner_id.id)
            
            # Vérifier toutes les missions existantes
            all_missions = self.env['take_a_way_loyalty.mission'].search([])
            _logger.warning("[FIDELITE][DEBUG] Toutes les missions existantes: %s", len(all_missions))
            for mission in all_missions:
                _logger.warning("[FIDELITE][DEBUG] Mission: %s (début: %s, fin: %s)", mission.name, mission.debut, mission.fin)
            
            missions = self.env['take_a_way_loyalty.mission'].search([
                ('debut', '<=', fields.Date.today()),
                ('fin', '>=', fields.Date.today()),
            ])
            
            _logger.warning("[FIDELITE][DEBUG] Missions trouvées dans la période: %s", len(missions))

            for mission in missions:
                _logger.warning("[FIDELITE][DEBUG] Vérification de la mission: %s", mission.name)
                
                # Vérifier si la commande a un partenaire
                if not order.partner_id:
                    _logger.warning("[FIDELITE][DEBUG] Commande %s n'a pas de partenaire, impossible de vérifier les missions", order.id)
                    continue
                
                mission_user = self.env['take_a_way_loyalty.mission_user'].search([
                    ('mission_id', '=', mission.id),
                    ('utilisateur_id', '=', order.partner_id.id),
                    ('etat', '=', 'en_cours')
                ], limit=1)

                if not mission_user:
                    _logger.warning("[FIDELITE][DEBUG] Aucun mission_user trouvé pour la mission %s et l'utilisateur %s (ID: %s)", 
                                   mission.name, order.partner_id.name, order.partner_id.id)
                    
                    # Vérifier tous les mission_users pour cette mission
                    all_mission_users = self.env['take_a_way_loyalty.mission_user'].search([
                        ('mission_id', '=', mission.id)
                    ])
                    _logger.warning("[FIDELITE][DEBUG] Tous les mission_users pour cette mission: %s", len(all_mission_users))
                    for mu in all_mission_users:
                        _logger.warning("[FIDELITE][DEBUG] Mission_user: %s (utilisateur: %s, état: %s)", 
                                       mu.id, mu.utilisateur_id.name, mu.etat)
                    continue

                _logger.warning("[FIDELITE][DEBUG] Mission_user trouvé: %s, progression actuelle: %s", 
                               mission_user.id, mission_user.progression)

                for condition in mission.condition_ids:
                    _logger.warning("[FIDELITE][DEBUG] Vérification de la condition: %s", condition.type_condition.code)
                    if condition.type_condition.code == 'ACHAT_PRODUIT':
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

    def _check_product_condition(self, order, condition, mission_user):
        if condition.produit_id:
            progression_produit = self.env['take_a_way_loyalty.progression_produit'].search([
                ('mission_user_id', '=', mission_user.id),
                ('produit_id', '=', condition.produit_id.id)
            ], limit=1)

            if not progression_produit:
                progression_produit = self.env['take_a_way_loyalty.progression_produit'].create({
                    'mission_user_id': mission_user.id,
                    'produit_id': condition.produit_id.id,
                    'quantite_requise': condition.quantite,
                    'quantite_actuelle': 0
                })

            quantite_achetee = sum(line.qty for line in order.lines if line.product_id.id == condition.produit_id.id)
            
            if quantite_achetee > 0:
                progression_produit.write({
                    'quantite_actuelle': progression_produit.quantite_actuelle + quantite_achetee
                })
                
                self.env['take_a_way_loyalty.mission_user']._check_mission_completion(mission_user)

    def _check_total_condition(self, order, condition, mission_user):
        if order.amount_total >= condition.montant_minimum:
            mission_user.progression += 1
            self.env['take_a_way_loyalty.mission_user']._check_mission_completion(mission_user)

    def _check_order_count_condition(self, order, condition, mission_user):
        # Utiliser le statut 'paid' pour les commandes POS en Odoo 18
        order_count = self.env['pos.order'].search_count([
            ('partner_id', '=', order.partner_id.id),
            ('state', '=', 'paid'),  # statut correct pour Odoo 18
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
                # La mission est complétée
                mission_user.etat = 'termine'
                # Ajouter les points de récompense
                points_record = self.env['take_a_way_loyalty.points_utilisateur'].search([
                    ('utilisateur_id', '=', mission_user.utilisateur_id.id)
                ], limit=1)
                if points_record:
                    points_record.points_total += mission_user.mission_id.point_recompense

    def _check_achats_jour_condition(self, order, condition, mission_user):
        """Vérifie si l'utilisateur a fait 2 achats dans la même journée."""
        # On récupère la date de la commande (sans l'heure)
        date_order = fields.Date.from_string(order.date_order)
        # On compte les commandes 'paid' du jour pour ce user
        order_count = self.env['pos.order'].search_count([
            ('partner_id', '=', order.partner_id.id),
            ('state', '=', 'paid'),
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
                ('state', '=', 'paid'),
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

# from odoo import models, fields, api


# class take_a_way_loyalty(models.Model):
#     _name = 'take_a_way_loyalty.take_a_way_loyalty'
#     _description = 'take_a_way_loyalty.take_a_way_loyalty'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100

