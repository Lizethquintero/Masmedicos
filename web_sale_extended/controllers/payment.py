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
    def payment_payulatam_gateway_api_response(self, **kwargs):
        _logger.error('**********************545+++++++++++++++++++++++++++++++++++++')
        _logger.error(kwargs)
        order = request.website.sale_get_order()
        if not order and kwargs['transactionId']:
            order = request.env['sale.order'].sudo().search([('payulatam_transaction_id', '=', kwargs['transactionId'])])
        if not order:
            redirection = self.checkout_redirection(order)
            if redirection:
                return redirection

        
        #request.session['sale_order_id'] = None
        #request.session['sale_transaction_id'] = None
        domain = [('payulatam_transaction_id', '=', kwargs['transactionId'])]
        lapTransactionState = kwargs['lapTransactionState']
        lapResponseCode = kwargs['lapResponseCode']
        lapResponseCode = kwargs['lapResponseCode']
        payulatam_transaction_id = request.env['sale.order'].sudo().search(domain, limit=1)
        if payulatam_transaction_id:
            if lapTransactionState == 'APPROVED':
                payulatam_transaction_id.write({
                    'payulatam_state': 'TRANSACCIÓN APROBADA',
                    'state': 'payu_approved'
                })
                if request.session['sale_order_id'] and order == payulatam_transaction_id:
                    """ En este caso el usuario puede continuar directamente la transacción """
                    render_values = {}
                    render_values.update({
                        'order_id': order,
                        'response': dict(kwargs),
                        'order_detail': order.order_line[0],
                    })
                    """ Mensaje en la orden de venta con la respuesta de PayU """
                    body_message = """
                        <b><span style='color:green;'>PayU Latam - Transacción de Pago Aprobada</span></b><br/>
                        <b>Orden ID:</b> %s<br/>
                        <b>Transacción ID:</b> %s<br/>
                        <b>Estado:</b> %s<br/>
                        <b>Código Respuesta:</b> %s<br/>
                    """ % (
                        kwargs['reference_pol'], 
                        kwargs['transactionId'],
                        kwargs['lapTransactionState'],
                        kwargs['lapResponseCode'],
                    )
                    payulatam_transaction_id.message_post(body=body_message, type="comment")
                    return request.render("web_sale_extended.web_sale_extended_payment_response_process", render_values)
                else:
                    """ En caso contrario se envía correo con la información para seguir """
                    render_values = {}
                    render_values.update({
                        'order_id': order,
                        'response': dict(kwargs),
                    })
                    template = request.env['mail.template'].sudo().search([('payulatam_approved_process', '=', True)], limit=1)
                    context = dict(request.env.context)
                    if template:
                        _logger.error('*************+******+++++++++++***+*')
                        _logger.error(template)
                        _logger.error(payulatam_transaction_id.id)
                        #template.sudo().send_mail(payulatam_transaction_id.id)
                        payulatam_transaction_id._send_order_payu_latam_approved()
                        """
                        template_values = template.generate_email(payulatam_transaction_id.id, fields=None)
                        template_values.update({
                            #'email_to': sale_id.tusdatos_email,
                            'email_to': payulatam_transaction_id.partner_id.email,
                            'auto_delete': False,
                            #'partner_to': False,
                            'scheduled_date': False,
                        })
                        template.write(template_values)
                        cleaned_ctx = dict(request.env.context)
                        cleaned_ctx.pop('default_type', None)
                        template.with_context(lang=request.env.user.lang).send_mail(payulatam_transaction_id.id, force_send=True, raise_exception=True)
                        """

                        """ Mensaje en la orden de venta con la respuesta de PayU """
                        body_message = """
                            <b><span style='color:green;'>PayU Latam - Transacción de Pago Aprobada</span></b><br/>
                            <b>Orden ID:</b> %s<br/>
                            <b>Transacción ID:</b> %s<br/>
                            <b>Estado:</b> %s<br/>
                            <b>Código Respuesta:</b> %s<br/>
                        """ % (
                            kwargs['reference_pol'], 
                            kwargs['transactionId'],
                            kwargs['lapTransactionState'],
                            kwargs['lapResponseCode'],
                        )
                        payulatam_transaction_id.message_post(body=body_message, type="comment")
                        return request.render("web_sale_extended.web_sale_extended_payment_response_process", render_values)
                #request.session['sale_order_id'] = None
                #request.session['sale_transaction_id'] = None
            else:
                render_values = {}
                render_values.update({
                    'order_id': order,
                    'response': dict(kwargs),
                })
                payulatam_transaction_id.write({
                    'payulatam_state': 'TRANSACCIÓN DECLINADA',
                })
                payulatam_transaction_id.action_cancel()
                request.session['sale_order_id'] = None
                request.session['sale_transaction_id'] = None
                body_message = """
                    <b><span style='color:red;'>PayU Latam - Transacción de Pago PSE RECHAZADA</span></b><br/>
                    <b>Orden ID:</b> %s<br/>
                    <b>Transacción ID:</b> %s<br/>
                    <b>Estado:</b> %s<br/>
                    <b>Código Respuesta:</b> %s<br/>
                """ % (
                    kwargs['reference_pol'], 
                    kwargs['transactionId'],
                    kwargs['lapTransactionState'],
                    kwargs['lapResponseCode'],
                )
                payulatam_transaction_id.message_post(body=body_message, type="comment")
                return request.render("web_sale_extended.payulatam_rejected_process_pse", render_values)
            