# -*- coding: utf-8 -*-#

from openerp import models, fields, api


class SaleOrderLineMargin(models.Model):
    _name = 'sale.order.line.margin'

    order_id = fields.Many2one('sale.order', string="Orden de venta", ondelete='cascade')
    order_line_id = fields.Many2one('sale.order.line', string='Linea de orden de venta', ondelete='cascade')
    product_desc = fields.Char(string="Descripción")
    supplier_id = fields.Many2one('res.partner', string="Proveedor")
    supplier_price = fields.Float('Costo', default='0.0')
    porcentaje = fields.Float('%', default='0.0')
    margen = fields.Float('Márgen', default='0.0')
    

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    supplier_id = fields.Many2one('res.partner', string="Proveedor")
    sale_order_line_margin = fields.Many2one('sale.order.line.margin', 'Order Lines Margin', ondelete='cascade')
    

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    sale_order_line_margin = fields.One2many('sale.order.line.margin', 'order_id', 'Order Lines', ondelete='cascade')
    margen_bruto = fields.Float('Márgen bruto sobre la venta', default='0.0')
