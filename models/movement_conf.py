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

class movement_conf(models.Model):
    _name = 'movement_conf'

    name = fields.Char(string="Configuracion de Albaranes: ", readonly=True)
    configuracion = fields.Selection([('activo','Procesar Albaranes'), ('pasivo','Detener Albaranes')], string="Estado:")

    # Crear Configuracion Inicial
    @api.model
    def action_create_conf(self):
        if not self.env['movement_conf'].search([('name', '=', 'Configuracion')]):
            self.env['movement_conf'].create({'name':'Configuracion', 'configuracion': 'activo' })

    # Crear Configuracion Inicial
    @api.multi
    def action_cambiar(self):
        if self.configuracion == "activo":
            self.configuracion = "pasivo"
        else:
            self.configuracion = "activo"
            stock_picking = self.env['stock.picking'].search([('state', '=', 'assigned')])
            if stock_picking:
                for stock_move in stock_picking:

                    for move in stock_move.move_ids_without_package:
                        move.quantity_done = move.product_uom_qty

                    stock_move.button_validate()
