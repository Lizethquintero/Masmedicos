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
    policy_number = fields.Char('Número de Certificado')
    number = fields.Char(string='Número de Póliza')
    recurring_next_date = fields.Date(string='Date of Next Invoice', help="The next invoice will be created on this date then the period will be extended.")
    sponsor_id = fields.Many2one('res.partner')
    campo_vacio = fields.Boolean('Campo vacio', default=False)  
    
    
    @api.model
    def create(self, vals):
        res = super(SaleSubscription, self).create(vals)
        
        if res.recurring_invoice_line_ids[0].product_id.product_tmpl_id.sequence_id:
            sequence_id = res.recurring_invoice_line_ids[0].product_id.product_tmpl_id.sequence_id
        else:
            sequence_id = res.recurring_invoice_line_ids[0].product_id.product_tmpl_id.categ_id.sequence_id
        res.write({
            'policy_number': str(sequence_id.number_next_actual).zfill(10),
            'number': str(sequence_id.code),
            'recurring_next_date': datetime.date.today(),
            'sponsor_id': sequence_id.sponsor_id,
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
    
    
    def _prepare_invoice_data(self):
        res = super(SaleSubscription, self)._prepare_invoice_data()
        res.update({
            'sponsor_id': self.sponsor_id
        })
        return res
    