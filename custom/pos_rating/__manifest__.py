# -*- coding: utf-8 -*-
{
    'name': "Pos Rating",
    'sequence': 4,
    'depends': ['base', 'product', 'point_of_sale'],
    'data': [
        'views/pos_product.xml',
        'views/pos_config.xml',
    ],
    'assets': {
        'point_of_sale._assets_pos': [
            'pos_rating/static/src/js/product_receipt.js',
            'pos_rating/static/src/js/discount_limit.js',
            'pos_rating/static/src/xml/pos_screen.xml',
            'pos_rating/static/src/xml/product_receipt.xml',
        ],
    },
    'application': True,
    'installable': True,
}
