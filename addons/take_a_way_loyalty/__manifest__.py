# -*- coding: utf-8 -*-
{
    'name': "Take A Way Loyalty",
    'summary': """
        Système de fidélité avec missions""",
    'description': """
        Module de gestion de la fidélité avec système de missions
    """,
    'author': "Take A Way",
    'website': "https://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Sales',
    'version': '1.0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'point_of_sale', 'product'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'data/type_mission_data.xml',
        'views/add_participant_wizard_views.xml',
        'views/parrainage_wizard_views.xml',
        'views/views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'data/demo_parrainage_mission.xml',
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
    'post_init_hook': 'post_init_hook',
}

