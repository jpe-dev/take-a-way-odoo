from odoo import api, SUPERUSER_ID
from . import models

def post_init_hook(cr, registry):
    with api.Environment.manage():
        env = api.Environment(cr, SUPERUSER_ID, {})

        # Définir la langue par défaut sur fr_CH
        lang = env['res.lang'].search([('code', '=', 'fr_CH')], limit=1)
        if lang:
            env['res.users'].browse(SUPERUSER_ID).write({'lang': lang.code})

        # Définir la devise par défaut sur CHF
        currency = env['res.currency'].search([('name', '=', 'CHF')], limit=1)
        if currency:
            env['res.company'].browse(1).write({'currency_id': currency.id})