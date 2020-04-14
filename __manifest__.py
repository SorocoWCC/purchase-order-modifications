# -*- coding: utf-8 -*-
{
    'name': "San Miguel - Purchase Order Modifications",

    'summary': """
        Purchase Order Modifications""",

    'description': """
        Long description of module's purpose
    """,

    'author': "Recicladora San Miguel",
    'website': "https://www.recicladorasanmiguel.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.2',

    # any module necessary for this one to work correctly
    'depends': ['base','purchase'],

    # always loaded
    'data': [
        'purchase_order_modifications_report.xml',
        'data/configuration.xml',
        'views/templates.xml',
        'views/purchase_order.xml',
        'views/product.xml',
        'views/printer.xml',
        'views/camera.xml',
        'views/movement_conf.xml',
        'views/report_tiquete_compra.xml',
        'views/report_factura_de_compra_fotos.xml',
        'views/report_certificado_co2.xml'

    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}