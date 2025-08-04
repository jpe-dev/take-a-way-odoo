from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class ParrainageWizard(models.TransientModel):
    _name = 'parrainage.wizard'
    _description = 'Assistant pour saisir un code de parrainage'

    partner_id = fields.Many2one('res.partner', string='Contact', required=True)
    code_parrainage = fields.Char(string='Code de parrainage', required=True, help='Saisissez le code de parrainage de votre parrain')

    def action_utiliser_code_parrainage(self):
        """Utilise le code de parrainage saisi"""
        self.ensure_one()
        
        if not self.code_parrainage:
            raise ValidationError(_('Veuillez saisir un code de parrainage.'))
        
        # Rechercher le parrain par son code
        parrain = self.env['res.partner'].search([('code_parrainage', '=', self.code_parrainage)], limit=1)
        
        if not parrain:
            raise ValidationError(_('Le code de parrainage saisi n\'existe pas.'))
        
        if parrain.id == self.partner_id.id:
            raise ValidationError(_('Vous ne pouvez pas vous parrainer vous-même.'))
        
        # Définir le parrain
        self.partner_id.parrain_id = parrain.id
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Parrainage effectué',
                'message': f'Vous avez été parrainé par {parrain.name}.',
                'type': 'success',
            }
        } 