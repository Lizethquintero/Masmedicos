# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ResCountry(models.Model):
    _inherit = 'res.country'

    
    def get_website_sale_states(self, mode='billing'):
        bad_state = [647,648,649,650,651,652,653,654,655,656,657,658,659,660,661,662,663,664,665,666,667,668,669,670,671,672,673,674,675,676,677,678,679]
        result = self.sudo().state_ids.filtered(lambda line: line.id not in bad_state)
        new_result = []
        for res in self.sudo().state_ids.filtered(lambda line: line.id not in bad_state):
            res.update({'name': res.name.lower().title()})
            new_result.append(res)
        return new_result
