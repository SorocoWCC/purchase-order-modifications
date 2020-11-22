# -*- coding: utf-8 -*-

from odoo import models, fields, api

class product(models.Model):
    _name = 'res.partner'
    _inherit = 'res.partner'
    control_estadistico = fields.Boolean (string='Control Estadístico:')
	