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
                
    @http.route(['/shop/payment/payulatam-gateway-api/pse_process'], type='http', auth="public", website=True, sitemap=False)
    def payulatam_gateway_api_pse(self, **post):
        order = request.website.sale_get_order()
        """ Proceso de Pago """
        referenceCode = str(request.env['api.payulatam'].payulatam_get_sequence())
        accountId = request.env['api.payulatam'].payulatam_get_accountId()
        descriptionPay = "Payment Origin from " + order.name
        signature = request.env['api.payulatam'].payulatam_get_signature(
            order.amount_total,'COP',referenceCode)
        payulatam_api_env = request.env.user.company_id.payulatam_api_env
        if payulatam_api_env == 'prod':
            payulatam_response_url = request.env.user.company_id.payulatam_api_response_url
        else:
            payulatam_response_url = request.env.user.company_id.payulatam_api_response_sandbox_url
        tx_value = {"value": order.amount_total, "currency": "COP"}
        tx_tax = {"value": 0,"currency": "COP"}
        tx_tax_return_base = {"value": 0, "currency": "COP"}
        additionalValues = {
            "TX_VALUE": tx_value,
            "TX_TAX": tx_tax,
            "TX_TAX_RETURN_BASE": tx_tax_return_base
        }
        buyer = {
            #"merchantBuyerId": "1",
            #"fullName": order.partner_id.name,
            #"fullName": 'APPROVED',
            "emailAddress": order.partner_id.email,
            #"contactPhone": order.partner_id.phone,
            #"dniNumber": order.partner_id.identification_document,
            #"shippingAddress": shippingAddress
        }    
        order_api = {
            "accountId": accountId,
            "referenceCode": referenceCode,
            "description": descriptionPay,
            "language": "es",
            "signature": signature,
            #"notifyUrl": "https://easytek-confacturacion-2123332.dev.odoo.com/shop/payment/payulatam-gateway-api/response",
            "additionalValues": additionalValues,
            "buyer": buyer,
            #"shippingAddress": shippingAddress
        }
        payer = {
            #"merchantPayerId": "1",
            #"fullName": post['credit_card_billing_firstname'] + ' ' + post['credit_card_billing_lastname'],
            "fullName": 'APPROVED',
            "emailAddress": post['pse_billing_email'],
            "contactPhone": post['pse_partner_phone'],
            #"dniNumber": post['credit_card_partner_document'],
            #"billingAddress": post['credit_card_partner_street']
        }
        extraParameters = {
            "RESPONSE_URL": payulatam_response_url,
            "PSE_REFERENCE1": "127.0.0.1",
            "FINANCIAL_INSTITUTION_CODE": post['pse_bank'],
            "USER_TYPE": post['pse_person_type'],
            "PSE_REFERENCE2": post['pse_partner_type'],
            "PSE_REFERENCE3": post['pse_partner_document']
        }    
        transaction = {
            "order": order_api,
            "payer": payer,
            "extraParameters": extraParameters,
            "type": "AUTHORIZATION_AND_CAPTURE",
            "paymentMethod": "PSE",
            "paymentCountry": "CO",
            "deviceSessionId": request.httprequest.cookies.get('session_id'),
            "ipAddress": "127.0.0.1",
            "cookie": request.httprequest.cookies.get('session_id'),
            #"userAgent": "Mozilla/5.0 (X11; Linux x86_64; rv:52.0) Gecko/20100101"
            "userAgent": "Firefox"
        }
        credit_card_values = {
            "command": "SUBMIT_TRANSACTION",
            "transaction": transaction,
        }
        response = request.env['api.payulatam'].payulatam_credit_cards_payment_request(credit_card_values)
        if response['code'] != 'SUCCESS':
            render_values = {'error': response['error']}
            return request.render("web_sale_extended.payulatam_rejected_process", render_values)
        _logger.error(response)
        """poniendo mensaje en la orden de venta con la respuesta de PayU"""
        body_message = """
            <b>PayU Latam - Transacción de Pago PSE</b><br/>
            <b>Orden ID:</b> %s<br/>
            <b>Transacción ID:</b> %s<br/>
            <b>Estado:</b> %s<br/>
            <b>Código Respuesta:</b> %s
        """ % (
            response['transactionResponse']['orderId'], 
            response['transactionResponse']['transactionId'], 
            response['transactionResponse']['state'], 
            response['transactionResponse']['responseCode']
        )
        order.message_post(body=body_message, type="comment")
        if response['transactionResponse']['state'] == 'APPROVED':
            _logger.info('APPROVED Validated PayU Latam payment for tx %s: set as done' % (response['transactionResponse']['orderId']))
            order.action_payu_confirm()
            render_values = {'error': ''}
            render_values.update({
                'state': response['transactionResponse']['state'],
                'transactionId': response['transactionResponse']['transactionId'],
                'responseCode': response['transactionResponse']['responseCode'],
                'order_Id': response['transactionResponse']['orderId'],
                'order_id': order
            })
            return request.render("web_sale_extended.payulatam_success_process_pse", render_values)
        elif response['transactionResponse']['state'] == 'PENDING':
            _logger.info('Notificación recibida para el pago de PayU Latam: %s: establecido como PENDIENTE' % (response['transactionResponse']['orderId']))
            order.action_payu_confirm()
            #request.session['sale_order_id'] = None
            #request.session['sale_transaction_id'] = None
            error = ''
            render_values = {'error': error}
            render_values.update({
                'state': response['transactionResponse']['state'],
                'transactionId': response['transactionResponse']['transactionId'],
                'responseCode': response['transactionResponse']['responseCode'],
                'order_Id': response['transactionResponse']['orderId'],
                'bank_url': response['transactionResponse']['orderId'],
                'order_id': order,
                'bank_url': response['transactionResponse']['extraParameters']['BANK_URL']
            })
            return request.render("web_sale_extended.payulatam_success_process_pse", render_values)
        elif response['transactionResponse']['state'] in ['EXPIRED', 'DECLINED']:
            render_values = {}
            #if 'paymentNetworkResponseErrorMessage' in response['transactionResponse']:
            #    if 'ya se encuentra registrada con la referencia' in response['transactionResponse']['paymentNetworkResponseErrorMessage']:
            render_values = {'error': '',}
            if response['transactionResponse']['paymentNetworkResponseErrorMessage']:
                render_values.update({'error': response['transactionResponse']['paymentNetworkResponseErrorMessage']})
            render_values.update({
                'state': response['transactionResponse']['state'],
                'transactionId': response['transactionResponse']['transactionId'],
                'responseCode': response['transactionResponse']['responseCode'],
                'order_Id': response['transactionResponse']['orderId'],
                'order_id': order
            })
            return request.render("web_sale_extended.payulatam_rejected_process_pse", render_values)
        else:
            error = 'Se recibió un estado no reconocido para el pago de PayU Latam %s: %s, set as error' % (
                response['transactionResponse']['transactionId'],response['status']
            )
            order.action_cancel()
            render_values = {'error': error}
            return request.render("web_sale_extended.payulatam_rejected_process_pse", render_values)
        
        