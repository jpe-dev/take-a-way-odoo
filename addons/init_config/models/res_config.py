from odoo import api, models

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    @api.model
    def get_values(self):
        res = super().get_values()
        # Activer CHF
        self.env['res.currency'].search([('name', '=', 'CHF')]).write({'active': True})
        # Configurer la société principale
        company = self.env.company
        chf_currency = self.env['res.currency'].search([('name', '=', 'CHF')], limit=1)
        if chf_currency:
            company.write({
                'currency_id': chf_currency.id,
                'country_id': self.env.ref('base.ch').id,
            })
        return res
