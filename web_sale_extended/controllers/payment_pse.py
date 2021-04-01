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
        descriptionPay = "Payment Origin from " + str(order.name)
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
            body_message = """
                <b><span style='color:red;'>PayU Latam - Error en pago con PSE</span></b><br/>
                <b>Código:</b> %s<br/>
                <b>Error:</b> %s
            """ % (
                response['code'],
                "Error de comunicación con PayU Latam"
            )
            if not request.session['sale_order_id']:
                checkout_landpage_redirect = request.env.user.company_id.checkout_landpage_redirect
                if checkout_landpage_redirect:
                    return request.redirect(checkout_landpage_redirect)
                return request.redirect("/web/login")
            else:
                order.message_post(body=body_message, type="comment")
                render_values = {'error': response['error']}
                return request.render("web_sale_extended.payulatam_rejected_process", render_values)        

        if response['transactionResponse']['state'] == 'APPROVED':
            order.write({
                'payulatam_order_id': response['transactionResponse']['orderId'],
                'payulatam_transaction_id': response['transactionResponse']['transactionId'],
                'payulatam_state': response['transactionResponse']['state'],
                'payment_method_type': 'PSE',
                'payulatam_state': 'TRANSACCIÓN CON PSE PENDIENTE DE APROBACIÓN',
                'payulatam_datetime': fields.datetime.now(),
            })
            order.action_payu_approved()
            render_values = {'error': ''}
            render_values.update({
                'state': response['transactionResponse']['state'],
                'transactionId': response['transactionResponse']['transactionId'],
                'responseCode': response['transactionResponse']['responseCode'],
                'order_Id': response['transactionResponse']['orderId'],
                'order_id': order
            })
            body_message = """
                <b><span style='color:green;'>PayU Latam - Transacción de pago con PSE</span></b><br/>
                <b>Orden ID:</b> %s<br/>
                <b>Transacción ID:</b> %s<br/>
                <b>Estado:</b> %s<br/>
                <b>Código Respuesta:</b> %s
            """ % (
                response['transactionResponse']['orderId'], 
                response['transactionResponse']['transactionId'], 
                'APROBADO', 
                response['transactionResponse']['responseCode']
            )
            order.message_post(body=body_message, type="comment")
            return request.render("web_sale_extended.payulatam_success_process_pse", render_values)
        elif response['transactionResponse']['state'] == 'PENDING':
            order.action_payu_confirm()
            #request.session['sale_order_id'] = None
            #request.session['sale_transaction_id'] = None
            order.write({
                'payulatam_order_id': response['transactionResponse']['orderId'],
                'payulatam_transaction_id': response['transactionResponse']['transactionId'],
                'payulatam_state': response['transactionResponse']['state'],
                'payment_method_type': 'PSE',
                'payulatam_state': 'TRANSACCIÓN CON PSE PENDIENTE DE APROBACIÓN',
                'payulatam_datetime': fields.datetime.now(),
            })
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
            body_message = """
                <b><span style='color:orange;'>PayU Latam - Transacción de pago con PSE</span></b><br/>
                <b>Orden ID:</b> %s<br/>
                <b>Transacción ID:</b> %s<br/>
                <b>Estado:</b> %s<br/>
                <b>Código Respuesta:</b> %s
            """ % (
                response['transactionResponse']['orderId'], 
                response['transactionResponse']['transactionId'], 
                'PENDIENTE DE APROBACIÓN', 
                response['transactionResponse']['responseCode']
            )
            order.message_post(body=body_message, type="comment")
            return request.render("web_sale_extended.payulatam_success_process_pse", render_values)
        elif response['transactionResponse']['state'] in ['EXPIRED', 'DECLINED']:
            order.write({
                'payulatam_order_id': response['transactionResponse']['orderId'],
                'payulatam_transaction_id': response['transactionResponse']['transactionId'],
                'payulatam_state': response['transactionResponse']['state'],
                'payment_method_type': 'PSE',
                'payulatam_state': 'TRANSACCIÓN CON PSE RECHAZADA',
                'payulatam_datetime': fields.datetime.now(),
            })
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
            body_message = """
                <b><span style='color:red;'>PayU Latam - Transacción de pago con PSE</span></b><br/>
                <b>Orden ID:</b> %s<br/>
                <b>Transacción ID:</b> %s<br/>
                <b>Estado:</b> %s<br/>
                <b>Código Respuesta:</b> %s
            """ % (
                response['transactionResponse']['orderId'], 
                response['transactionResponse']['transactionId'], 
                'RECHAZADO', 
                response['transactionResponse']['responseCode']
            )
            order.message_post(body=body_message, type="comment")
            #order.action_cancel()
            return request.render("web_sale_extended.payulatam_rejected_process_pse", render_values)
        else:
            error = 'Se recibió un estado no reconocido para el pago de PayU Latam %s: %s, set as error' % (
                response['transactionResponse']['transactionId'],response['status']
            )
            order.action_cancel()
            render_values = {'error': error}
            return request.render("web_sale_extended.payulatam_rejected_process_pse", render_values)
        
        