# -*- coding: utf-8 -*-

from odoo import models, fields, api
from openerp.exceptions import ValidationError
from odoo.exceptions import UserError
from openerp.exceptions import Warning
from openerp import models, fields, api
from datetime import datetime
from pytz import timezone 
from datetime import timedelta  
import subprocess
import time
import base64
from openerp.http import request
from odoo_pictures import IM

class purchase_order(models.Model):
    _name = 'purchase.order'
    _inherit = 'purchase.order'
    state = fields.Selection(selection_add=[('quotation_paid', "Pagado")])
    #cajero_id = fields.Char(string="Cajero", readonly=True, copy=False)
    cliente = fields.Char(string="Cliente")
    cantidad = fields.Integer(string="Cantidad (KG)", default=1)
    material_procesado = fields.Char(string="Material Procesado", default="Desechos Reciclables")
    co2 = fields.Char(store=True, string="CO2")
    periodo = fields.Char(string="Periodo")
    peso_lleno = fields.Float(string="Peso Lleno")
    peso_vacio = fields.Float(string="Peso Vacio")
    peso_neto = fields.Float( string="Peso Neto")
    ficha = fields.Char (string="Ficha")
    placa_vehiculo= fields.Char (string="Placa")
    informacion = fields.Char (string="Avisos")
    partner_info = fields.Char(compute='_action_partner_info' )
    #mantenimiento_info = fields.Char(compute='_action_allowance', store=True, string="Avisos")
	#purchase_info_validation = fields.Char(compute='_action_purchase_creation', store=True, string="validacion")
   

    @api.multi
    def button_confirm(self):
        super(purchase_order, self).button_confirm()

        order_line = self.order_line
        if not order_line:
            raise Warning ("Error: La orden de compra no contiene productos.")
        
        self.user_id = self.env.user
        mensaje = "<p>Factura aprobada por: " + str(self.env.user.name) + " - " +datetime.now(timezone('America/Costa_Rica')).strftime("%Y-%m-%d %H:%M:%S") + "</p>"
        self.message_post(body=mensaje, content_subtype='html')

# Calcular la cantidad del producto a facturar
    @api.one
   # @api.onchange('peso_lleno', 'peso_vacio')
    def action_calcular_peso(self):
        
        # Validaciones peso lleno y vacio
        if self.peso_lleno < 1 or self.peso_vacio < 1 :
            raise Warning ("Error: Ingrese los pesos lleno y vacio.")
        if self.peso_vacio > self.peso_lleno:
            raise Warning ("Error: El peso vacio no puede ser mayor al lleno")

        # Validar que solamente 1 producto tenga el check de calcular / Validar los productos sobre los cuales no se puede realizar calculo
        productos_marcados = 0
        for i in self.order_line :
            if i.product_id.calcular == False and i.calcular == True :
                raise Warning ("Error: Este producto no es valido para realizar el cálculo")
            if i.calcular == True:
                productos_marcados += 1
        if productos_marcados > 1 :
            raise Warning ("Error: Solamente 1 producto puede ser calculado")
        if productos_marcados == 0 :
            raise Warning ("Error: Seleccione 1 producto para calcular")

        # Calculo de la cantidad de producto a facturar
        descontar = 0
        cantidad_facturable = self.peso_lleno - self.peso_vacio
        for i in self.order_line:
            # Productos que no se deben descontar: Mantenimiento, rebajo, prestamo
            if i.product_id.name != "Mantenimiento" and i.product_id.name != "Rebajo" and i.product_id.name != "Prestamo" and i.calcular == False:
                descontar += i.product_qty

        # Asigna la cantidad de material a facturar en la linea de compra
        for i in self.order_line:
            if i.calcular == True :
                i.product_qty = cantidad_facturable - descontar

# Calcular el peso neto
    @api.onchange('peso_lleno', 'peso_vacio')
    def _action_peso_neto(self):

      if self.peso_lleno > 0 and self.peso_vacio > 0:
        self.peso_neto = self.peso_lleno - self.peso_vacio
    
      # Nombre de la impresora 
      impresora = self.env['impresora'].search([('state', '=', 'on')])
      
      if len(impresora) > 0 and self.peso_lleno > 0:
          if impresora[0].state == "on" :
            subprocess.call('echo' + ' \"' + '------------------------ \n '+ '$(TZ=GMT+6 date +%T%p_%D)' + '\n \n' + 
            str(self.partner_id.name) + '\n' + str(self.placa_vehiculo) + '\n \n' +
            'Ingreso: ' + str(self.peso_lleno) + ' kg \n' + 'Salida: ' + str(self.peso_vacio) + ' kg \n' + 'NETO: ' + str(self.peso_neto) + ' kg \n' 
+ '------------------------ \n'+ '\"' + '| lp -d ' + str(impresora[0].name), shell=True)

    # Tomar Fotos   
    @api.one
    def action_take_picture(self):
        # Solo incluye las lineas de pedido si la factura esta vacia
        if len(self.order_line) == 0:
            # Incluye linea de Chatarra
            res= self.env['product.template'].search([['name', '=', 'Chatarra'], ['default_code', '=', 'CH']])
            self.order_line.create({'product_id': str(res.id), 'price_unit':str(res.list_price), 'order_id' : self.id, 'name': '[CH] Chatarra','calcular': True, 'date_planned': str(fields.Date.today()), 'product_qty': 1, 'product_uom': str(res.uom_po_id.id)})

            # Incluye Linea de basura
            #res_basura= self.env['product.template'].search([('name', '=', 'Basura Chatarra')])
            #self.order_line.create({'product_id': str(res_basura.id), 'price_unit':str(res_basura.list_price), 'order_id' : self.id, 'name': '[BC] Basura Chatarra', 'date_planned': str(fields.Date.today())})

        for line in self.order_line:
            camara_romana = self.env['camara'].search([['tipo', '=', 'romana']])
            camara_indicador = self.env['camara'].search([['tipo', '=', 'indicador']])
            imagen_vivo = IM({"ip": camara_romana[0].ip, "user": camara_romana[0].usuario, "passwd": camara_romana[0].contrasena}, {"ip": camara_indicador[0].ip, "user": camara_indicador[0].usuario, "passwd": camara_indicador[0].contrasena})
            
            # No se adjuntan fotos a los productos especiales
            if line.product_id.name != 'Basura Chatarra' and line.product_id.name != 'Prestamo' and line.product_id.name != 'Rebajo' :

                res = imagen_vivo.get_image()
               
                try:
                    if not line.imagen_lleno :
                        line.imagen_lleno = res["image"]
                        break
                    elif not line.imagen_vacio :
                        line.imagen_vacio = res["image"]
                        break
                except:
                    self.env.user.notify_danger(message='Error al obtener las imagenes.')

# Captura la informacion relevante del cliente : Prestamos, Mantenimiento y notas  
    @api.onchange('partner_id')
    def _action_partner_info(self):
        self.notes = self.partner_id.comment
