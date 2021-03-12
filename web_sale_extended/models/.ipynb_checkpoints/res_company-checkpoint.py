# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

import logging
_logger = logging.getLogger(__name__)


class ResCompany(models.Model):
    _inherit = 'res.company'
    
    logo_website_pdf  = fields.Binary(string="Logo Website PDF", readonly=False)
    logo_supervigilado  = fields.Binary(string="Logo Supervigilado", readonly=False)

    mail_tusdatos = fields.Char("E-mail TusDatos")
    password_tusdatos = fields.Char("Password TusDatos")
    
    payulatam_merchant_id = fields.Char(string="PayU Latam Merchant ID", groups='base.group_user')
    payulatam_account_id = fields.Char(string="PayU Latam Account ID", groups='base.group_user')
    payulatam_api_key = fields.Char(string="PayU Latam API Key", groups='base.group_user')
    payulatam_api_login = fields.Char(string="PayU Latam API Login", groups='base.group_user')
    payulatam_api_env = fields.Selection(
        [("test", "Sanbox - Test"), ("prod", "Producción")]
    )
    payulatam_api_ref_seq_id = fields.Many2one('ir.sequence','Referencia API')