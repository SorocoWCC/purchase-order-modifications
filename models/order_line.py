# -*- coding: utf-8 -*-

from odoo import models, fields, api


class order_line(models.Model):
    _name = 'purchase.order.line'
    _inherit = 'purchase.order.line'
    imagen_lleno = fields.Binary (string="Imagen Lleno")
    imagen_vacio = fields.Binary (string="Imagen Vacio")
    peso_lleno = fields.Float (string="Peso Lleno")
    peso_vacio = fields.Float (string="Peso Vacio" )
    basura = fields.Float (string="Basura" )
    calcular = fields.Boolean (string="Calcular" )