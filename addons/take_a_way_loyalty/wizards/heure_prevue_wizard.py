# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime, timedelta

class HeurePrevueWizard(models.TransientModel):
    _name = 'heure.prevue.wizard'
    _description = 'Wizard pour définir l\'heure prévue'

    pos_order_id = fields.Many2one('pos.order', string='Commande PoS', required=True)
    heure_prevue = fields.Datetime(string='Heure prévue', required=True, default=fields.Datetime.now)
    
    # Options rapides
    option_1h = fields.Boolean(string='Dans 1 heure', default=False)
    option_2h = fields.Boolean(string='Dans 2 heures', default=False)
    option_30min = fields.Boolean(string='Dans 30 minutes', default=False)
    option_custom = fields.Boolean(string='Heure personnalisée', default=True)

    @api.onchange('option_1h', 'option_2h', 'option_30min', 'option_custom')
    def _onchange_options(self):
        """Met à jour l'heure prévue selon l'option sélectionnée"""
        for record in self:
            if record.option_1h:
                record.heure_prevue = fields.Datetime.now() + timedelta(hours=1)
                record.option_2h = False
                record.option_30min = False
                record.option_custom = False
            elif record.option_2h:
                record.heure_prevue = fields.Datetime.now() + timedelta(hours=2)
                record.option_1h = False
                record.option_30min = False
                record.option_custom = False
            elif record.option_30min:
                record.heure_prevue = fields.Datetime.now() + timedelta(minutes=30)
                record.option_1h = False
                record.option_2h = False
                record.option_custom = False
            elif record.option_custom:
                record.option_1h = False
                record.option_2h = False
                record.option_30min = False

    @api.onchange('heure_prevue')
    def _onchange_heure_prevue(self):
        """Met à jour les options quand l'heure est modifiée manuellement"""
        for record in self:
            if record.heure_prevue:
                # Désélectionner toutes les options rapides
                record.option_1h = False
                record.option_2h = False
                record.option_30min = False
                record.option_custom = True

    def action_confirm(self):
        """Confirme l'heure prévue"""
        self.ensure_one()
        
        # Mettre à jour la commande PoS
        self.pos_order_id.write({
            'heure_prevue': self.heure_prevue
        })
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Heure prévue définie',
                'message': f'Heure prévue définie à {self.heure_prevue.strftime("%d/%m/%Y %H:%M")}',
                'type': 'success',
            }
        }

    def action_clear(self):
        """Efface l'heure prévue"""
        self.ensure_one()
        
        # Effacer l'heure prévue
        self.pos_order_id.write({
            'heure_prevue': False
        })
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Heure prévue effacée',
                'message': 'L\'heure prévue a été effacée',
                'type': 'info',
            }
        } 