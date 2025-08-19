# -*- coding: utf-8 -*-from
{
    'name': "Pos Rating",
    'sequence': 4,
    'depends': ['base', 'product', 'point_of_sale'],
    'data': [
        'security/ir.model.access.csv',
        'views/product_view.xml',
        'views/res_config_settings.xml'
    ],
    'assets': {
        'point_of_sale._assets_pos': [
            'pos_rating/static/src/js/pos_receipt.js',
            'pos_rating/static/src/js/session_discount_limit.js',
            'pos_rating/static/src/xml/pos_screen.xml',
            'pos_rating/static/src/xml/pos_receipt.xml',
        ],
    },
    'application': True,
    'installable': True,

}
