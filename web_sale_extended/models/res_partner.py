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
    clerk_code = fields.Char('Código de Empleado')
    
    city_2 = fields.Char('Ciudad')
    state_2 = fields.Char('Departamento / Provincia / Estado')
    
    beneficiary_country_id = fields.Many2one('res.country', 'País del beneficiario')
    beneficiary_state_id = fields.Many2one('res.country.state', 'Estado del beneficiario')
    beneficiary_zip_id = fields.Many2one('res.city.zip', 'Ciudad del beneficiario')
    
    buyer = fields.Boolean(string='Comprador', copy=False)
    beneficiary = fields.Boolean(string='Beneficiario', copy=False)
    main_insured = fields.Boolean(string='Asegurado Principal', copy=False)
    
    company_type = fields.Selection(selection_add=[('sponsor', 'Sponsor')], compute=False, default='person')
    person_type = fields.Selection(compute=False)
    sponsor_id = fields.Many2one('res.partner', 'Sponsor', domain=[('company_type', '=', 'sponsor')])
    campo_vacio = fields.Boolean('Campo vacio', default=False)  
    
    """
    def _compute_clerk_code(self):
        partners = self.env['res.partner'].search([('subscription_id', '=', self.subscription_id)])
        marital_status = self.marital_status
        for partner in partners:
    """
            


    @api.depends('zip','city_id')
    def _get_website_partner_type(self):
        for record in self:
            record.website_partner_type = record.zip + record.street
     
    
    def _write_company_type(self):
        for partner in self:
            if partner.company_type == 'company' or partner.company_type == 'sponsor':
                partner.is_company = True

    
    @api.onchange('company_type')
    def onchange_company_type(self):
        if self.company_type == 'company' or self.company_type == 'sponsor':
            self.is_company = True
            self.person_type = '1'
        else:
            self.is_company = False
            self.person_type = '2'
            
    @api.onchange("person_type")
    def onchange_person_type(self):        
        if self.person_type == "2":
            self.company_type = "person"
