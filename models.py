# -*- coding: utf-8 -*-
 
from openerp import models, fields, api
import subprocess
import time
import datetime
from openerp.exceptions import Warning
import base64
from openerp.http import request


class impresora(models.Model):
    _name = 'impresora'
    name = fields.Char(string= 'Impresora')
    state = fields.Selection ([('on', 'ON'), ('off','OFF') ], string='Estado', default='off')

# ----------------------------  CLASE HEREDADA - PRODUCTO ------------------------------------
class product(models.Model):
    _name = 'product.template'
    _inherit = 'product.template'
    sumar_validacion = fields.Boolean (string='NO sumar en validación:')
    precio_venta_informe = fields.Float (string = 'Precio de Venta Informe:')
    calcular = fields.Boolean (string='Calcular peso en ordenes de compra:', default=True) 
    tiquetes = fields.Boolean (string='Mostrar en sistema de tiquetes:', default=False)   

# ----------------------------  CLASE HEREDADA - PROVEEDOR ------------------------------------
class product(models.Model):
    _name = 'res.partner'
    _inherit = 'res.partner'
    rebajar_mantenimiento = fields.Boolean (string='Rebajar Mantenimiento')
# ----------------------------  FIN HEREDADA - PRODUCTO ------------------------------------


# ----------------------------  CLASE HEREDADA - USERS ------------------------------------
class user_purchase(models.Model):
    _name = 'res.users'
    _inherit = 'res.users'
    purchase_type_user = fields.Selection ([('tablero', 'Tablero'), ('limitado','Limitado'), ('administrativo','Administrativo'), ('super', 'Super Usuario')], string='Tipo de Usuario para Compras', required=True)

# ----------------------------  FIN HEREDADA - USERS ------------------------------------

# ---------------------------- CLASE HEREDADA - ORDER LINE ------------------------------------
class order_line(models.Model):
    _name = 'purchase.order.line'
    _inherit = 'purchase.order.line'
    imagen_lleno = fields.Binary (string="Imagen Lleno")
    imagen_vacio = fields.Binary (string="Imagen Vacio")
    peso_lleno = fields.Float (string="Peso Lleno")
    peso_vacio = fields.Float (string="Peso Vacio" )
    basura = fields.Float (string="Basura" )
    calcular = fields.Boolean (string="Calcular" )
    order_line_user = fields.Char (compute='_action_order_line_user', store=True, string="Usuario", readonly=True)

# Nombre del cajero
    @api.one
    @api.depends('product_id.name', 'peso_vacio')
    def _action_order_line_user(self):
        self.order_line_user = str(self.env.user.name)

# ---------------------------- FIN CLASE HEREDADA - ORDER LINE ------------------------------------

# ---------------------------- CLASE HEREDADA - PURCHASE ORDER ------------------------------------
class purchase_order(models.Model):
    _name = 'purchase.order'
    _inherit = 'purchase.order'
    state = fields.Selection(selection_add=[('quotation_paid', "Pagado")])
    imagen_pago = fields.Binary(string="Información de pago")
    fecha_pago = fields.Datetime(string="Fecha Pago", readonly=True, copy=False)
    cajero_id = fields.Char(string="Cajero", readonly=True, copy=False)
    cliente = fields.Char(string="Cliente")
    cantidad = fields.Integer(string="Cantidad (KG)", default=1)
    material_procesado = fields.Char(string="Material Procesado", default="Desechos Reciclables")
    co2 = fields.Char(compute='_update_co2', store=True, string="CO2")
    periodo = fields.Char(string="Periodo")
    peso_lleno = fields.Float(string="Peso Lleno")
    peso_vacio = fields.Float(string="Peso Vacio")
    peso_neto = fields.Float( string="Peso Neto")
    placa = fields.Char (string="Ficha")
    placa_vehiculo = fields.Char (string="Placa")
    pago = fields.Selection ([('regular','Regular'), ('muy','***MUY PAGA***'), ('caja_chica','Caja Chica')], string='Metodo de Pago', required=True)
    pago_caja = fields.Selection ([('pendiente','Pendiente'),('pagado','Pagado')], string='Pago', default="pendiente", readonly=True, copy=False)
    informacion = fields.Char(compute='_update_info', store=True, string="Avisos")
    prestamo_info = fields.Char(compute='_action_allowance', store=True, default=0, string="Prestamo" )
    mantenimiento_info = fields.Char(compute='_action_allowance', store=True, string="Avisos")
    purchase_info_validation = fields.Char(compute='_action_purchase_creation', store=True, string="validacion")
    _defaults = { 
    }
# ---------------------------- FIN CLASE HEREDADA - PURCHASE ORDER ------------------------------------


# Actualizar el campo informacion con el tipo de pago
    @api.one
    @api.depends('pago')
    def _update_info(self):
        if str(self.pago) == "muy" :
            self.informacion = "***MUY PAGA***"
        elif str(self.pago) == "caja_chica":
            self.informacion = "Caja Chica"
        else:
            self.informacion = "Regular"

# Calcular CO2
    @api.one
    @api.depends('cantidad')
    def _update_co2(self):
        self.co2 = float(self.cantidad) / 1000

    @api.multi
    def wkf_confirm_order(self):
        super(purchase_order, self).wkf_confirm_order()
        # Validacion de la cantidad de material facturado
        cantidad_facturable = 0
               
        if self.peso_neto > 0 :       
            for i in self.order_line :
                if i.product_id.calcular == True:
                    cantidad_facturable += i.product_qty

        if cantidad_facturable > self.peso_neto:
            raise Warning ("Error: La cantidad de material facturado es mayor que el peso neto.")

        # Valida que el abono al prestamo se pueda realizar
        res= self.env['cliente.allowance'].search([('name', '=', str(self.partner_id.name)), ('state', '=', 'new')])

        for line in self.order_line:
            if line.product_id.name == "Prestamo" and len(res) > 0:
                if -(line.price_subtotal) > res[0].saldo:
                    raise Warning ("Error: El monto del abono es mayor al saldo del prestamo.")

        peso = float(self.peso_vacio) 
        # Valida si las lineas de factura de los usuarios no limitados tiene fotos adjuntas 
        for order_line in self.order_line:
            res_user = self.env['res.users'].search([('name', '=', str(order_line.order_line_user))])

            if order_line.product_id.sumar_validacion == False:
                peso += float(order_line.product_qty)

            if str(res_user.purchase_type_user) != "limitado" and order_line.product_id.sumar_validacion == False:
                if str(order_line.imagen_lleno) == "None" or str(order_line.imagen_vacio) == "None": 
                    #raise Warning ("Por favor adjunte una imagen en la linea del producto: " + str(order_line.name))
                    print "Validacion Imagenes" 

            if  str(res_user.purchase_type_user) != "limitado":
                if peso > float(self.peso_lleno) or float(self.peso_lleno) == 0 or float(self.peso_vacio) == 0 :
                    #raise Warning ("Error en los pesos (Productos - Peso lleno - Peso Vacio)") 
                    print "Validacion Pesos"        

    # Marcar la factura como pagada y la asocia con los cierres de caja
    @api.one
    def action_quotation_paid(self):

        # Valida si la factura fue cancelada antes de pagarla
        if str(self.state) == "cancel" :
            raise Warning ("Error: La factura fue cancelada")
        #Cajeros    
        cajero_cierre_regular = self.env['cierre'].search([('cajero', '=', str(self.env.user.name)), ('state', '=', 'new'), ('tipo', '=', 'regular')])
        cajero_cierre_caja_chica = self.env['cierre'].search([('cajero', '=', str(self.env.user.name)), ('state', '=', 'new'), ('tipo', '=', 'caja_chica')])
        # Cierres
        cierre_regular = self.env['cierre'].search([('state', '=', 'new'), ('tipo', '=', 'regular')])
        cierre_caja_chica = self.env['cierre'].search([('state', '=', 'new'), ('tipo', '=', 'caja_chica')])

        # El usuario administrador puede pagar todas las facturas
        if str(self.env.user.name) == "Administrator" :
            self.cajero_id = str(self.env.user.name)
            self.fecha_pago = fields.Datetime.now()
            self.pago_caja = 'pagado'
            self.cierre_id = cajero_cierre_regular.id
            self.cierre_id_caja_chica = cajero_cierre_caja_chica.id
        else:
            # Valida si el usuario que creo la orden de compra es igual al cajero
            if str(self.env.user.name) == str(self.validator.name) :
                raise Warning ("Error: El usuario que valida el pedido de compra es igual al cajero")

            # Valida si hay cierres de caja disponibles para asociarlos
            if cierre_regular.id == False :
                raise Warning ("Error: Proceda a crear un cierre de caja tipo Regular.")
            if str(self.pago) == "caja_chica":
                if cierre_caja_chica.id == False:
                    raise Warning ("Error: Proceda a crear un cierre de caja tipo Caja Chica.")     
            #===============================================
            # Valida facturas tipo Caja Chica
            if str(self.pago) == "caja_chica" :

                if str(cajero_cierre_caja_chica.cajero) == str(self.env.user.name) :
                    self.cajero_id = str(self.env.user.name)
                    self.fecha_pago = fields.Datetime.now()
                    self.pago_caja = 'pagado'
                    self.cierre_id = cajero_cierre_regular.id
                    self.cierre_id_caja_chica = cajero_cierre_caja_chica.id
                else:
                    raise Warning ("Usuario no autorizado para pagar facturas") 
            #===============================================
            # Valida facturas tipo Regular
            elif str(self.pago) == "regular" :

                # Valida si el usuario que creo la orden de compra es igual al cajero
                if str(self.env.user.name) == str(self.validator.name) :
                    raise Warning ("Error: El usuario que valida el pedido de compra es igual al cajero")
                
                # verifica que se adjunte la imagen
                if str(self.imagen_pago) == "None":
                    raise Warning ("Por Favor adjunte la imagen de pago.")

                if str(cajero_cierre_regular.cajero) == str(self.env.user.name) :
                    self.cajero_id = str(self.env.user.name)
                    self.fecha_pago = fields.Datetime.now()
                    self.pago_caja = 'pagado'
                    self.cierre_id = cajero_cierre_regular.id
                    self.cierre_id_caja_regular = cajero_cierre_regular.id
                else:
                    raise Warning ("Usuario no autorizado para pagar facturas")
            #===============================================
            # Valida las facturas tipo Muy Paga
            elif str(self.pago) == "muy" :
                self.cajero_id = str(self.env.user.name)
                self.fecha_pago = fields.Datetime.now()
                self.pago_caja = 'pagado'
                # Asocia el Nombre del cajera
                self.cierre_id = cajero_cierre_regular.id
                # Asocia el cierre de caja
                self.cierre_id_caja_regular = cajero_cierre_regular.id
            
            else:
                raise Warning ("Usuario no autorizado para pagar facturas") 
                    
            if str(self.informacion) == "Listo Para Revisar | ***MUY PAGA***":
                self.informacion = "***MUY PAGA***"

            # Crear directament un Abono al prestamo
            res= self.env['cliente.allowance'].search([('name', '=', str(self.partner_id.name)), ('state', '=', 'new')])
            print str(res)
            for line in self.order_line:
                if line.product_id.name == "Prestamo" and len(res) > 0:
                    res[0].abono_ids.create({'name':str(res[0].name),'libro_id':res[0].id, 'monto':-(line.price_subtotal), 'notas': str(self.name)})

# Transferir la factura
    @api.one
    def action_quotation_transfer(self):
        if str(self.state) == 'draft':
                self.state = 'sent'
        else:
            self.state = 'draft'
            if str(self.pago) == "muy" :
                self.informacion = 'Listo Para Revisar | ***MUY PAGA***'
            else:
                self.informacion = 'Listo Para Revisar'

# Tomar Fotos   
    @api.one
    def action_take_picture(self):
        # Solo incluye las lineas de pedido si la factura esta vacia
        if len(self.order_line) == 0:
            # Incluye linea de Chatarra
            res= self.env['product.template'].search([['name', '=', 'Chatarra'], ['default_code', '=', 'CH']])
            self.order_line.create({'product_id': str(res.id), 'price_unit':str(res.list_price), 'order_id' : self.id, 'name': '[CH] Chatarra','calcular': True, 'date_planned': str(fields.Date.today())})

            # Incluye Linea de basura
            res_basura= self.env['product.template'].search([('name', '=', 'Basura Chatarra')])
            self.order_line.create({'product_id': str(res_basura.id), 'price_unit':str(res_basura.list_price), 'order_id' : self.id, 'name': '[BC] Basura Chatarra', 'date_planned': str(fields.Date.today())})

        foto_nombre=str(datetime.datetime.now().strftime("%d-%m-%Y_%H:%M:%S")) + "-" + str(self.name)
        tomar_foto="pictures.sh " + foto_nombre
        subprocess.call(str(tomar_foto), shell=True)

        for line in self.order_line:
            # No se adjuntan fotos a los productos especiales
            if line.product_id.name != 'Basura Chatarra' and line.product_id.name != 'Prestamo' and line.product_id.name != 'Rebajo' :

                if not line.imagen_lleno :
                    file = open("/Documentos_Compartidos/Fotos/ODOO_Fotos/" + foto_nombre +".jpg", "rb")
                    out = file.read()
                    file.close()
                    line.imagen_lleno = base64.b64encode(out)
                    break
                else:
                    file = open("/Documentos_Compartidos/Fotos/ODOO_Fotos/" + foto_nombre +".jpg", "rb")
                    out = file.read()
                    file.close()
                    line.imagen_vacio = base64.b64encode(out)
                    break
                    #IP de donde viene el request
                    #print "------> 1" + str(request.httprequest.environ['REMOTE_ADDR'])


# Captura la informacion relevante del cliente : Prestamos, Mantenimiento y notas  
    @api.one
    @api.depends('partner_id')
    def _action_allowance(self):
        # Asigna las notas del proveedor y las trae a la order de compra
        self.notes = self.partner_id.comment
        # Verifica si se debe realizar un abono al prestamo
        res= self.env['cliente.allowance'].search([('name', '=', str(self.partner_id.name)), ('state', '=', 'new')])
        if len(res) > 0:
            self.prestamo_info = res[0].saldo
        else:
            self.prestamo_info = 0
        # Verifica si se debe rebajar Mantenimiento    
        if self.partner_id.rebajar_mantenimiento == True:
            self.mantenimiento_info = "Mantenimiento" 

#  Validar si el usuario puede crear facturas  
    @api.one
    @api.depends('partner_id')
    def _action_purchase_creation(self):
        cajero_cierre_regular = self.env['cierre'].search([('cajero', '=', str(self.env.user.name)), ('state', '=', 'new'), ('tipo', '=', 'regular')])
        cajero_cierre_caja_chica = self.env['cierre'].search([('cajero', '=', str(self.env.user.name)), ('state', '=', 'new'), ('tipo', '=', 'caja_chica')])
        print str(cajero_cierre_regular.cajero) + str(cajero_cierre_caja_chica.cajero)
        if str(self.pago) == "regular" :
            if str(cajero_cierre_regular.cajero) == str(self.env.user.name) :
                raise Warning ("Usuario no autorizado para crear facturas") 
        if str(self.pago) == "caja_chica" :
            if str(cajero_cierre_caja_chica.cajero) == str(self.env.user.name) :
                raise Warning ("Usuario no autorizado para crear facturas")


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
            +  '------------------------ \n'+ '\"' + '| lp -d ' + str(impresora[0].name), shell=True)


# ----------------------------AGREGAR LINEAS DE PRODUCTO ------------------------------------
# Agregar linea Pedido Aluminio
    @api.one
    def action_aluminio(self):
        res= self.env['product.template'].search([('name', '=', 'Aluminio')])
        if len(res) > 0 :
            self.order_line.create({'product_id': str(res.id), 'price_unit':str(res.list_price), 'order_id' : self.id, 'name': str(res.name), 
    'date_planned': str(fields.Date.today())})
        else:
            raise Warning ("El producto no existe")

# Agregar linea Pedido Cobre
    @api.one
    def action_cobre(self):
        res= self.env['product.template'].search([('name', '=', 'Cobre')])
        if len(res) > 0 :
            self.order_line.create({'product_id': str(res.id), 'price_unit':str(res.list_price), 'order_id' : self.id, 'name': str(res.name), 
    'date_planned': str(fields.Date.today())})
        else:
            raise Warning ("El producto no existe")

# Agregar linea Pedido Bronce
    @api.one
    def action_bronce(self):
        res= self.env['product.template'].search([('name', '=', 'Bronce')])
        if len(res) > 0 :
            self.order_line.create({'product_id': str(res.id), 'price_unit':str(res.list_price), 'order_id' : self.id, 'name': str(res.name), 
    'date_planned': str(fields.Date.today())})
        else:
            raise Warning ("El producto no existe")
# Agregar linea Pedido Chatarra
    @api.one
    def action_chatarra(self):
        res= self.env['product.template'].search([('name', '=', 'Chatarra')])
        if len(res) > 0 :
            self.order_line.create({'product_id': str(res.id), 'price_unit':str(res.list_price), 'order_id' : self.id, 'name': str(res.name), 
    'date_planned': str(fields.Date.today())})
        else:
            raise Warning ("El producto no existe")
# Agregar linea Pedido Papel Primera
    @api.one
    def action_papel_primera(self):
        res= self.env['product.template'].search([('name', '=', 'Papel Primera')])
        if len(res) > 0 :
            self.order_line.create({'product_id': str(res.id), 'price_unit':str(res.list_price), 'order_id' : self.id, 'name': str(res.name), 
    'date_planned': str(fields.Date.today())})
        else:
            raise Warning ("El producto no existe")

# Agregar linea Pedido Papel Segunda
    @api.one
    def action_papel_segunda(self):
        res= self.env['product.template'].search([('name', '=', 'Papel Segunda')])
        if len(res) > 0 :
            self.order_line.create({'product_id': str(res.id), 'price_unit':str(res.list_price), 'order_id' : self.id, 'name': str(res.name), 
    'date_planned': str(fields.Date.today())})
        else:
            raise Warning ("El producto no existe")

# Agregar linea Pedido Papel Primera
    @api.one
    def action_papel_periodico(self):
        res= self.env['product.template'].search([('name', '=', 'Papel Periodico')])
        if len(res) > 0 :
            self.order_line.create({'product_id': str(res.id), 'price_unit':str(res.list_price), 'order_id' : self.id, 'name': str(res.name), 
    'date_planned': str(fields.Date.today())})
        else:
            raise Warning ("El producto no existe")

# Agregar linea Pedido Carton
    @api.one
    def action_carton(self):
        res= self.env['product.template'].search([('name', '=', 'Carton')])
        if len(res) > 0 :
            self.order_line.create({'product_id': str(res.id), 'price_unit':str(res.list_price), 'order_id' : self.id, 'name': str(res.name), 
    'date_planned': str(fields.Date.today())})
        else:
            raise Warning ("El producto no existe")

# Agregar linea Pedido Bateria
    @api.one
    def action_bateria(self):
        res= self.env['product.template'].search([('name', '=', 'Bateria')])
        if len(res) > 0 :
            self.order_line.create({'product_id': str(res.id), 'price_unit':str(res.list_price), 'order_id' : self.id, 'name': str(res.name), 
    'date_planned': str(fields.Date.today())})
        else:
            raise Warning ("El producto no existe")

# Agregar linea Pedido Tarjeta Computadora
    @api.one
    def action_tar_comp(self):
        res= self.env['product.template'].search([('name', '=', 'Tar_Comp')])
        if len(res) > 0 :
            self.order_line.create({'product_id': str(res.id), 'price_unit':str(res.list_price), 'order_id' : self.id, 'name': str(res.name), 
    'date_planned': str(fields.Date.today())})
        else:
            raise Warning ("El producto no existe")

# Agregar linea Pedido Plastico Pet
    @api.one
    def action_plastico_pet(self):
        res= self.env['product.template'].search([('name', '=', 'Plastico Pet')])
        if len(res) > 0 :
            self.order_line.create({'product_id': str(res.id), 'price_unit':str(res.list_price), 'order_id' : self.id, 'name': str(res.name), 
    'date_planned': str(fields.Date.today())})
        else:
            raise Warning ("El producto no existe")

# Agregar linea Pedido Microondas
    @api.one
    def action_microondas(self):
        res= self.env['product.template'].search([('name', '=', 'Microondas')])
        if len(res) > 0 :
            self.order_line.create({'product_id': str(res.id), 'price_unit':str(res.list_price), 'order_id' : self.id, 'name': str(res.name), 
    'date_planned': str(fields.Date.today())})
        else:
            raise Warning ("El producto no existe")

# Agregar linea Radiador (Cobre/Aluminio)
    @api.one
    def action_radiador_ca(self):
        res= self.env['product.template'].search([('name', '=', 'Radiador (Cobre/Aluminio)')])
        if len(res) > 0 :
            self.order_line.create({'product_id': str(res.id), 'price_unit':str(res.list_price), 'order_id' : self.id, 'name': str(res.name), 
    'date_planned': str(fields.Date.today())})
        else:
            raise Warning ("El producto no existe")

# Agregar linea Radiador (Cobre/Bronce)
    @api.one
    def action_radiador_cb(self):
        res= self.env['product.template'].search([('name', '=', 'Radiador (Cobre/Bronce)')])
        if len(res) > 0 :
            self.order_line.create({'product_id': str(res.id), 'price_unit':str(res.list_price), 'order_id' : self.id, 'name': str(res.name), 
    'date_planned': str(fields.Date.today())})
        else:
            raise Warning ("El producto no existe")

# Agregar linea Catalizador Generico
    @api.one
    def action_catalizador_generico(self):
        res= self.env['product.template'].search([('name', '=', 'Catalizador Generico')])
        if len(res) > 0 :
            self.order_line.create({'product_id': str(res.id), 'price_unit':str(res.list_price), 'order_id' : self.id, 'name': str(res.name), 
    'date_planned': str(fields.Date.today())})
        else:
            raise Warning ("El producto no existe")

# Agregar linea Catalizador Original
    @api.one
    def action_catalizador_original(self):
        res= self.env['product.template'].search([('name', '=', 'Catalizador Original')])
        if len(res) > 0 :
            self.order_line.create({'product_id': str(res.id), 'price_unit':str(res.list_price), 'order_id' : self.id, 'name': str(res.name), 
    'date_planned': str(fields.Date.today())})
        else:
            raise Warning ("El producto no existe")

# Agregar linea  Vidrio
    @api.one
    def action_vidrio(self):
        res= self.env['product.template'].search([('name', '=', 'Vidrio')])
        if len(res) > 0 :
            self.order_line.create({'product_id': str(res.id), 'price_unit':str(res.list_price), 'order_id' : self.id, 'name': str(res.name), 
    'date_planned': str(fields.Date.today())})
        else:
            raise Warning ("El producto no existe")

# Agregar linea Plastico Lavadora
    @api.one
    def action_plastico_lavadora(self):
        res= self.env['product.template'].search([('name', '=', 'Plastico Lavadora')])
        if len(res) > 0 :
            self.order_line.create({'product_id': str(res.id), 'price_unit':str(res.list_price), 'order_id' : self.id, 'name': str(res.name), 
    'date_planned': str(fields.Date.today())})
        else:
            raise Warning ("El producto no existe")

# Agregar linea Caja Plastica
    @api.one
    def action_caja_plastica(self):
        res= self.env['product.template'].search([('name', '=', 'Caja Plastica')])
        if len(res) > 0 :
            self.order_line.create({'product_id': str(res.id), 'price_unit':str(res.list_price), 'order_id' : self.id, 'name': str(res.name), 
    'date_planned': str(fields.Date.today())})
        else:
            raise Warning ("El producto no existe")

# ----------------------------AGREGAR LINEAS DE PRODUCTO ------------------------------------
