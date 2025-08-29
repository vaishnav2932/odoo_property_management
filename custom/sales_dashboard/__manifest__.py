# -*- coding: utf-8 -*-
{
    'name': "Sales Dashboard",
    'version': "18.0.1.1",
    'depends': ['base', 'sale'],
    'data': [
        'views/action_views.xml'
    ],
    'assets': {
        'web.assets_backend': [
            'https://cdn.jsdelivr.net/npm/chart.js',
            'sales_dashboard/static/src/js/dashboard.js',
            'sales_dashboard/static/src/xml/dashboard.xml',
            'sales_dashboard/static/src/css/dashboard.css'
        ],
    },
    'insatllable': True,
    'license': "LGPL-3",
}
