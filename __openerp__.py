# -*- coding: utf-8 -*-

{
    'name': 'Modulo/Wizard para agregar productos segun el precio del proveedor.',
    'version': '8.0.1.0.0',
    'category': 'Sales & Purchases Management',
    'sequence': 14,
    'summary': '',
    'description': """
        Modulo/Wizard que permite agregar lineas tomando en cuenta el precio
        segun el proveedor.
        Se selecciona categoria, producto, proveedor y precios de costo.
    """,
    'author': "Angel A. Guadarrama B.",
    'website': "https://ve.linkedin.com/in/aguadarrama",
    'depends': ['base', 'web', 'product', 'sale', 'purchase'],
    'data': [
	'view/AddCustomCSS.xml',
        'wizard/sale_add_product.xml',
        'view/sale_view.xml',
	'security/ir.model.access.csv',
	
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
