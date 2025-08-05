from odoo import api, SUPERUSER_ID

def post_init_hook(env):
    """Hook post-installation pour configurer Odoo pour la Suisse"""
    try:
        # 1. Configurer la langue
        lang = env['res.lang'].search([('code', '=', 'fr_CH')], limit=1)
        if lang:
            env['res.users'].browse(SUPERUSER_ID).write({'lang': lang.code})
            print("Langue configurée sur fr_CH")
        
        # 2. Configurer la société
        company = env['res.company'].browse(1)
        swiss_country = env.ref('base.ch', raise_if_not_found=False)
        chf_currency = env.ref('base.CHF', raise_if_not_found=False)
        
        if swiss_country and chf_currency:
            company.write({
                'country_id': swiss_country.id,
                'currency_id': chf_currency.id,
            })
            print("Société configurée pour la Suisse")
        
        # 3. Configurer les paramètres pour le plan comptable
        env['ir.config_parameter'].set_param('account.chart_template_id', 'l10n_ch.chart_template_ch')
        print("Paramètres de configuration définis")
        
    except Exception as e:
        print(f"Erreur lors de la configuration: {str(e)}")