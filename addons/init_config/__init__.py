from odoo import api, SUPERUSER_ID
from . import models

def post_init_hook(cr, registry):
    with api.Environment.manage():
        env = api.Environment(cr, SUPERUSER_ID, {})

        # Définir la langue par défaut sur fr_CH
        lang = env['res.lang'].search([('code', '=', 'fr_CH')], limit=1)
        if lang:
            env['res.users'].browse(SUPERUSER_ID).write({'lang': lang.code})

        # Configurer la société principale pour forcer la localisation fiscale suisse
        company = env['res.company'].browse(1)
        company.write({
            'country_id': env.ref('base.ch').id,  # Suisse
            'currency_id': env.ref('base.CHF').id,  # Franc suisse
        })

        # Forcer l'installation du plan comptable suisse via la localisation
        # Odoo va automatiquement installer le bon plan comptable, taxes, etc.
        # quand le pays est défini sur la Suisse
        if env['ir.module.module'].search([('name', '=', 'account')]).state == 'installed':
            # Déclencher la configuration automatique de la localisation
            # en forçant la mise à jour des paramètres de la société
            company._onchange_country_id()