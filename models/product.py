# -*- coding: utf-8 -*-

from odoo import models, fields, api

class product(models.Model):
    _name = 'product.template'
    _inherit = 'product.template'
    sumar_validacion = fields.Boolean (string='NO sumar en validación:')
    tomar_foto = fields.Boolean (string='NO Fotos')
    calcular = fields.Boolean (string='Calcular peso en ordenes de compra:', default=True) 
    factor_conversion = fields.Float(string='Factor Conversión:') 
	