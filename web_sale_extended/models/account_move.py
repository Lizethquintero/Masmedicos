# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

import logging
_logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    _inherit = 'account.move'
    
    sponsor_id = fields.Many2one('res.partner')
    campo_vacio = fields.Boolean('Campo vacio', default=False)  