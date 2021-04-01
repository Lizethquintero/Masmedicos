# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

import logging
_logger = logging.getLogger(__name__)


class ResPartnerDocumentType(models.Model):
    _inherit = 'res.partner.document.type'
    
    abbreviation = fields.Char('Abreviación')
    
    


class ResPartner(models.Model):
    _inherit = 'res.partner'

    logo = fields.Binary(related="company_id.logo")
    website_partner_type = fields.Char(string='partner_type', compute='_get_website_partner_type', store=False)
    birthdate_date = fields.Date("Birthdate")
    expedition_date = fields.Date("Fecha de Expedición del Documento")
    ocupation = fields.Char("Ocupation")
    #age = fields.Integer(string="Age", readonly=True, compute="_compute_age")
    gender = fields.Selection(
        [("M", _("Male")), ("F", _("Female")), ("O", _("Other"))]
    )
    relationship = fields.Selection(
        [("P", "Principal"), ("C", "Conyugue"), ("D", "PADRES"), ("H", "HIJOS"), ("M", "HERMANOS"), ("S", "SUEGROS")]
    )
    marital_status = fields.Selection(
        [ ("Soltero", "Soltero"), ("Casado", "Casado"), ("Unión Libre", "Unión Libre"), ("Divorciado", "Divorciado"), ("Viudo", "Viudo")]
    )
    address_beneficiary = fields.Char('Dirección del Beneficiario')

    subscription_id = fields.Many2one('sale.subscription', 'ID de Subscripción')
    beneficiary_number = fields.Integer('Número de Beneficiario')


    @api.depends('zip','city_id')
    def _get_website_partner_type(self):
        for record in self:
            record.website_partner_type = record.zip + record.street
