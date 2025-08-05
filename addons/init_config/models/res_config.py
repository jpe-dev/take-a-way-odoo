from odoo import api, models

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    @api.model
    def get_values(self):
        res = super().get_values()
        # S'assurer que CHF est activé
        self.env['res.currency'].search([('name', '=', 'CHF')]).write({'active': True})
        return res

    @api.model
    def set_values(self):
        super().set_values()
        # Forcer la configuration suisse lors de la sauvegarde des paramètres
        company = self.env.company
        company.write({
            'country_id': self.env.ref('base.ch').id,
            'currency_id': self.env.ref('base.CHF').id,
        })
