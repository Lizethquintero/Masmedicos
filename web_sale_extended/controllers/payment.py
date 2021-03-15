# -*- coding: utf-8 -*-
import json
import logging, base64
from datetime import datetime
from datetime import date
from werkzeug.exceptions import Forbidden, NotFound
import werkzeug.utils
import werkzeug.wrappers
from odoo.exceptions import AccessError, MissingError
from odoo import fields, http, SUPERUSER_ID, tools, _
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager, get_records_pager
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.addons.payment.controllers.portal import PaymentProcessing
from odoo.addons.sale.controllers.portal import CustomerPortal
from odoo.osv import expression
import requests
from requests.auth import HTTPBasicAuth
from hashlib import md5
from werkzeug import urls
import socket
hostname = socket.gethostname()

_logger = logging.getLogger(__name__)


class WebsiteSaleExtended(WebsiteSale):
    
    def checkout_redirection(self, order):
        """ sobreescribiendo método nativo """
        # must have a draft sales order with lines at this point, otherwise reset
        if not order or order.state != 'draft':
            request.session['sale_order_id'] = None
            request.session['sale_transaction_id'] = None
            return request.redirect('/shop')
        
        checkout_landpage_redirect = request.env.user.company_id.checkout_landpage_redirect
        if order and not order.order_line:
            #return request.redirect('/shop/cart')
            request.session['sale_order_id'] = None
            request.session['sale_transaction_id'] = None
            return request.redirect('/shop')

        # if transaction pending / done: redirect to confirmation
        tx = request.env.context.get('website_sale_transaction')
        if tx and tx.state != 'draft':
            return request.redirect('/shop/payment/confirmation/%s' % order.id)

    
    @http.route(['/shop/payment'], type='http', auth="public", website=True, sitemap=False)
    def payment(self, **post):
        """ sobreescribiendo método nativo """
        order = request.website.sale_get_order()
        redirection = self.checkout_redirection(order)
        if redirection:
            return redirection

        render_values = self._get_shop_payment_values(order, **post)
        render_values['only_services'] = order and order.only_services or False

        if render_values['errors']:
            render_values.pop('acquirers', '')
            render_values.pop('tokens', '')
        
        """ PayU Latam Api """
        endpoint = 'PING' # connect status
        ping_response = request.env['api.payulatam'].payulatam_ping()
        credit_card_methods = []
        bank_list = []
        if ping_response['code'] == 'SUCCESS':
            # get payment methods
            credit_card_methods = request.env['api.payulatam'].payulatam_get_credit_cards_methods()
            #bank_list = request.env['api.payulatam'].payulatam_get_bank_list()
            #cash_list = request.env['api.payulatam'].payulatam_get_cash_method_list()
        
        #_logger.error(bank_list)
        
        mode = (False, False)
        country = request.env['res.country'].browse(49)
        credit_card_due_year_ids = list(range(2021, 2061))
        render_values.update({
            'error' : [],
            'mode' : mode,
            'cities' : [],
            'country': request.env['res.country'].browse(int(49)),
            'country_states' : country.get_website_sale_states(mode=mode[1]),
            'countries': country.get_website_sale_countries(mode=mode[1]),
            'credit_card_due_year_ids': credit_card_due_year_ids,
            'credit_card_methods': credit_card_methods,
            'bank_list': bank_list
        })
        return request.render("web_sale_extended.web_sale_extended_payment_process", render_values)
    
    @http.route(['/shop/payment/payulatam-gateway-api/response'], type='http', auth="public", website=True, sitemap=False)
    def payment_payulatam_gateway_api_response(self, **get):
        _logger.error('¡¡¡¡¡¡¡¡¡¡¡¡¡¡¡¡¡¡¡¡¡¡¡¡¡¡¡¡¡¡¡¡¡¡¡¡¡¡¡¡¡¡¡¡¡¡¡¡¡¡¡¡¡¡¡¡¡¡¡¡¡¡¡¡¡¡¡¡¡¡¡¡¡¡¡¡¡¡¡¡¡¡¡¡¡¡¡¡¡¡¡¡¡¡¡¡¡¡¡¡¡¡¡¡¡¡¡¡¡¡¡¡¡¡¡¡¡¡¡¡¡¡¡¡¡¡¡¡¡¡¡¡¡¡¡¡¡¡')
        _logger.error(get)