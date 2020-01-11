# -*- coding: utf-8 -*-

from odoo import models, fields, api
from openerp.exceptions import ValidationError
from odoo.exceptions import UserError
from openerp.exceptions import Warning

class camara(models.Model):
    _name = 'camara'
    ip = fields.Char(string= 'Dirección IP')
    tipo= fields.Selection ([('romana', 'Romana'), ('indicador','Indicador'), ('caja','Caja') ], string='Tipo')
    usuario = fields.Char(string= 'Usuario')
    contrasena = fields.Char(string= 'Contrasena')