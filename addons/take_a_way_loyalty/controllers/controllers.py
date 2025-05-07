# -*- coding: utf-8 -*-
# from odoo import http


# class TakeAWayLoyalty(http.Controller):
#     @http.route('/take_a_way_loyalty/take_a_way_loyalty', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/take_a_way_loyalty/take_a_way_loyalty/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('take_a_way_loyalty.listing', {
#             'root': '/take_a_way_loyalty/take_a_way_loyalty',
#             'objects': http.request.env['take_a_way_loyalty.take_a_way_loyalty'].search([]),
#         })

#     @http.route('/take_a_way_loyalty/take_a_way_loyalty/objects/<model("take_a_way_loyalty.take_a_way_loyalty"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('take_a_way_loyalty.object', {
#             'object': obj
#         })

