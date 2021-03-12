# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

import logging
_logger = logging.getLogger(__name__)



class IrSequence(models.Model):
    _inherit = 'ir.sequence'
    
    logo_website_pdf  = fields.Binary(string="Image del Plan para el documento PDF", readonly=False)
    logo_header_website_sponsor  = fields.Binary(string="Image del Plan del Patrocinador en el encabezado", readonly=False)
    logo_body_website_sponsor  = fields.Binary(string="Image del Patrocinador en el cuerpo del documento", readonly=False)
    beneficiaries_number = fields.Integer(string="Número Máximo de Beneficiarios")
    sponsor_name = fields.Char('Nombre del Sponsor')
    sponsor_nit = fields.Char('Identificación del Sponsor')
    sponsor_payment_url = fields.Char('URL de la Plataforma de Pagos')
    
    