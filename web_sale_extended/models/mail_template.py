# -*- coding: utf-8 -*-
import logging

from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError
from odoo.http import request

_logger = logging.getLogger(__name__)


class MailTemplate(models.Model):
    _inherit = 'mail.template'
    
    #tusdatos_process_send = fields.Boolean('Proceso de Verificación en Tusdatos.co')
    tusdatos_confirmation_accept = fields.Boolean('Proceso de Confirmación Exitoso en Tusdatos.co')
    tusdatos_confirmation_reject = fields.Boolean('Proceso de Confirmación Rechazado en Tusdatos.co')
    payulatam_approved_process = fields.Boolean('Proceso de Confirmación de Pago Aprobada')