# -*- coding: utf-8 -*-
from odoo import http

# class Odoo12Test(http.Controller):
#     @http.route('/odoo12_test/odoo12_test/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/odoo12_test/odoo12_test/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('odoo12_test.listing', {
#             'root': '/odoo12_test/odoo12_test',
#             'objects': http.request.env['odoo12_test.odoo12_test'].search([]),
#         })

#     @http.route('/odoo12_test/odoo12_test/objects/<model("odoo12_test.odoo12_test"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('odoo12_test.object', {
#             'object': obj
#         })