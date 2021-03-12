# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

import logging
_logger = logging.getLogger(__name__)


class AccountFiscalPosition(models.Model):
    _inherit = 'account.fiscal.position'
    
    website_published = fields.Boolean('Publicado', help="Publicado en Sitio Web")