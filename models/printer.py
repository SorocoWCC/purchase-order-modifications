# -*- coding: utf-8 -*-

from odoo import models, fields, api
from openerp.exceptions import ValidationError
from odoo.exceptions import UserError
from openerp.exceptions import Warning

class impresora(models.Model):
    _name = 'impresora'
    name = fields.Char(string= 'Impresora')
    state = fields.Selection ([('on', 'ON'), ('off','OFF') ], string='Estado', default='off')