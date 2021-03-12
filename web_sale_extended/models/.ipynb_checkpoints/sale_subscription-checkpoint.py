# -*- coding: utf-8 -*-
import logging
import datetime
import traceback

from collections import Counter
from dateutil.relativedelta import relativedelta
from uuid import uuid4

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.osv import expression
from odoo.tools import format_date, float_compare
from odoo.tools.safe_eval import safe_eval


_logger = logging.getLogger(__name__)


class SaleSubscription(models.Model):
    _inherit = "sale.subscription"
    
    
    #recurring_sale_order_line_ids = fields.One2many('sale.subscription.line', 'analytic_account_id', string='Subscription Lines', copy=True)
    subscription_partner_ids = fields.One2many('res.partner', 'subscription_id', string="Beneficiarios")
    policy_number = fields.Char('Número de Poliza')
    
    
    @api.model
    def create(self, vals):
        res = super(SaleSubscription, self).create(vals)
        sequence_id = res.recurring_invoice_line_ids[0].product_id.product_tmpl_id.categ_id.sequence_id
        res.write({
            'policy_number': sequence_id.number_next_actual,
        })
        sequence_id.write({
            'number_next_actual': int(sequence_id.number_next_actual) + 1,
        })
        
        '''
        order_line = self.env['sale.order.line'].search([('subscription_id','=',res.id)], limit=1)
        order = self.env['sale.order'].browse(order_line.id)
        order.write({
            'subscription_id': order.id,
        })
        '''
        
        return res
    