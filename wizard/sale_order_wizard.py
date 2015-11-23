# -*- coding: utf-8 -*-

from openerp import models, fields, api


class sale_order_add_product(models.TransientModel):
    _name = 'sale.order.add.product'
    _description = 'Agregar productos a la lineas'

    product_category_id = fields.Many2one('product.category', string="Categoria", required=True)
    product_id = fields.Many2one('product.product', string='Producto', domain=[('sale_ok', '=', True)], required=True)
    supplier_id = fields.Many2one('res.partner', string="Proveedor")
    public_price = fields.Float('Precio de venta', default='0.0', required=True)
    supplier_price = fields.Float('Precio de proveedor', default='0.0', required=True)
    supplier_price2 = fields.Float('Precio de proveedor', default='0.0', required=True)
    quantity = fields.Float('Cantidad', default='1.0', required=True)


    def onchange_get_supplier(self, cr, uid, ids, product_id):
		# Mostrar ids de los supplier_id segun el product_id seleccionado
		res = {}
		#PRODUCT TEMPLATE ID
		product_rd_tmpl = []
		#SUPPLIER
		suppliers_ids = []
		#LIST_PRICE
		price_ids = 0.0
		
		product_obj = self.pool.get('product.product')
		product_template_obj = self.pool.get('product.template')
		supp_info_obj = self.pool.get('product.supplierinfo')
		res_partner_obj = self.pool.get('res.partner')
		
		product_info_ids = product_obj.search(cr, uid, [('id', '=', product_id)])
		product_rd = product_obj.read(cr, uid, product_info_ids, ['product_tmpl_id'])
		for a in product_rd:
			product_rd_tmpl.append(a['product_tmpl_id'][0])
			
		# Para mostrar precio de la ficha del producto
		product_template_rd = product_template_obj.read(cr, uid, product_rd_tmpl, ['list_price'])
		for b in product_template_rd:
			price_ids = b['list_price']
		res['public_price'] = price_ids
		
		# Para obtener los proveedores de un producto
		product_supp_src = supp_info_obj.search(cr, uid, [('product_tmpl_id', 'in', product_rd_tmpl)])
		product_supp_rd = supp_info_obj.read(cr, uid, product_supp_src, ['name'])
		for c in product_supp_rd:
			suppliers_ids.append(c['name'][0])
		partner_ids = res_partner_obj.search(cr, uid, [('id', 'in', suppliers_ids)])
		
		return {'domain':{'supplier_id':[('id','in', partner_ids)]}, 'value': res}


    def onchange_get_cost(self, cr, uid, ids, product_id, supplier_id):
		res = {}
		product_rd_tmpl = []
		price_supplier = 0.0
		product_obj = self.pool.get('product.product')
		supp_info_obj = self.pool.get('product.supplierinfo')
		prclst_info_obj = self.pool.get('pricelist.partnerinfo')
		
		product_info_ids = product_obj.search(cr, uid, [('id', '=', product_id)])
		supp_info_ids = supp_info_obj.search(cr, uid, [('name', '=', supplier_id)])
		prclts_info_src = prclst_info_obj.search(cr, uid, [('suppinfo_id', 'in', supp_info_ids)])
		prclts_info_rd = prclst_info_obj.read(cr, uid, prclts_info_src, ['price'])
		for a in prclts_info_rd:
			price_supplier = a['price']
		res['supplier_price'] = price_supplier
		res['supplier_price2'] = price_supplier
		
		# Para sobreescribir la secuencia a 1 segun el supplier seleccionado
		product_rd = product_obj.read(cr, uid, product_info_ids, ['product_tmpl_id'])
		for b in product_rd:
			product_rd_tmpl.append(b['product_tmpl_id'][0])
		product_supp_src2 = supp_info_obj.search(cr, uid, [('name', '=', supplier_id), ('product_tmpl_id', 'in', product_rd_tmpl)])
		supp_info_obj.write(cr, uid, product_supp_src2, {'sequence': 1})
	
		# Para sobreescribir la secuencia a los demas suppliers siendo mayor a 1
		product_supp_src3 = supp_info_obj.search(cr, uid, [('name', '!=', supplier_id), ('product_tmpl_id', 'in', product_rd_tmpl)])
		seq = 1
		for c in product_supp_src3:
			seq = seq +1 
			supp_info_obj.write(cr, uid, c, {'sequence': seq})
		
		return {'value' : res}
    

    @api.one
    def add_product(self):
        active_id = self._context['active_id']
        sale = self.env['sale.order'].browse(active_id)
        
        product_id = self.product_id

        product = self.env['sale.order.line'].product_id_change(
            sale.pricelist_id.id,
            product_id.id,
            qty=self.quantity,
            uom=product_id.uom_id.id,
            partner_id=sale.partner_id.id)
        val = {
            'name': product['value'].get('name'),
            'product_uom_qty': self.quantity,
            'order_id': sale.id,
            'product_id': product_id.id or False,
			'supplier_id': self.supplier_id.id,
			'partner_id':sale.partner_id.id,
            'product_uom': product_id.uom_id.id,
            'price_unit': product['value'].get('price_unit'),
        }
	res = self.env['sale.order.line'].create(val)
	
	#Calculo de porcentaje de la diferencia
	#Formula - ( (valor nuevo - Valor antiguo) / Valor antiguo ) * 100
	por3 = None
	por1 = product['value'].get('price_unit') - self.supplier_price2
	if self.supplier_price2 == 0:
		por3 = 100
	else:
		por2 = por1 / self.supplier_price2
		por3 = por2 * 100
	
	#Traer la descripcion del producto
	product_desc_final = ''
	product_desc = self.env['product.product'].search_read([('id', '=', product_id.id )], ['product_tmpl_id'])
	for i in product_desc:
		pr_tmpl_id = i['product_tmpl_id'][0]
		product_tmpl = self.env['product.template'].search_read([('id', '=', pr_tmpl_id )], ['name', 'description', 'default_code'])
		
		for x in product_tmpl:
			product_desc_final = '[' + str(x['default_code']) + ']' + ' ' + str(x['name'])
	
	#Se crea un registro en el modelo sale.order.line y sale.order.line.margin
	val_margen = {
		'order_id': sale.id,
		'order_line_id': res.id,
		'product_desc': product_desc_final,
		'supplier_id': self.supplier_id.id,
		'supplier_price': self.supplier_price2,
		'porcentaje': por3,
		'margen': product['value'].get('price_unit') - self.supplier_price2,
		}
	
	res2 = self.env['sale.order.line.margin'].create(val_margen)
	
	#Actualizamos el campo sale_order_line_margin en sale.order.line
	sale_order_line = self.env['sale.order.line'].browse((res).id)
	sale_order_line.write({'sale_order_line_margin': (res2).id})
	
	#Calcular margen bruto de la venta
	margen_sum = []
	sale_margen = self.env['sale.order.line.margin'].search_read([('order_id', '=', active_id)], ['margen'])
	for d in sale_margen:
		margen_sum.append(d['margen'])
	sale.write({'margen_bruto': sum(margen_sum)})
