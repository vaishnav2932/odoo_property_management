# -*- coding: utf-8 -*-
{
    'name': "Property Management",
    'summary': '''property management''',
    'description': '''this is for manging property''',
    'sequence': 3,
    'category': "Property",
    'version': "18.0.1.1",
    'licence': "LGPL-3",
    'application': True,
    'auto_install': False,
    'installable': True,
    'author': "Raseena kv",
    'website': "www.cybrosys.com",
    'maintainer': "raseena  kv <raseenakv21@gmail.com>",
    'depends': [
        'base',
        'mail',
        'account',
        'contacts',
    ],
    'data': [
        "security/property_groups.xml",
        "security/company_record_rule.xml",
        "security/ir.model.access.csv",


        "views/account_move_views.xml",
        "views/res_partner_views.xml",
        "views/property_facility.xml",
        "views/property_property_views.xml",
        "views/property_management_views.xml",
        "views/property_property_line_views.xml",
        "views/property_menus.xml",

        "wizard/property_wizard_view.xml",

        "report/property_rent_reports.xml",
        "report/property_rent_template.xml",

        "data/property_property_demo.xml",
        "data/ir_sequence_data.xml",
        "data/ir_cron_data.xml",
        "data/mail_template_data.xml",
    ],

}
