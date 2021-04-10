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
    
    @http.route(['/shop/payment/payulatam-gateway-api'], type='http', auth="public", website=True, sitemap=False)
    def payulatam_gateway_api(self, **post):
        order = request.website.sale_get_order()
        redirection = self.checkout_redirection(order)
        if redirection:
            return redirection
        
        """ Si existe una orden activa y llegan sin el metodo de pago """
        if 'method_id' not in post or 'credit_card_number' not in post:
            return request.redirect('/shop/payment')
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
        
        """ TARJETA DE CREDITO LUNH """
        luhn_ok = request.env['api.payulatam'].luhn_checksum(post['credit_card_number'])
        if not luhn_ok:
            render_values = {'error': 'Número de tarjeta invalido'}
            body_message = """
                <b><span style='color:red;'>PayU Latam - Error en Transacción con Tarjeta de Crédito</span></b><br/>
                <b>Error:</b> %s
            """ % (
                render_values['error'], 
            )
            order.message_post(body=body_message, type="comment")
            return request.render("web_sale_extended.payulatam_rejected_process", render_values)
        
        """ Proceso de Tokenización """
        creditCardToken = {
            "payerId": str(order.partner_id.id),
            #"name": post['credit_card_billing_firstname'] + ' ' + post['credit_card_billing_lastname'],
            "name": post['credit_card_name'],
            "identificationNumber": post['credit_card_partner_document'],
            "paymentMethod": post['method_id'],
            "number": post['credit_card_number'],
            "expirationDate": post['credit_card_due_year'] + "/" + post['credit_card_due_month']
        }
        token_response = request.env['api.payulatam'].payulatam_get_credit_Card_token(creditCardToken)
        if token_response['code'] == 'SUCCESS':
            order.write({
                'payulatam_credit_card_token': token_response['creditCardToken']['creditCardTokenId'],
                'payulatam_credit_card_masked': token_response['creditCardToken']['maskedNumber'],
                'payulatam_credit_card_identification': token_response['creditCardToken']['identificationNumber'],
                'payulatam_credit_card_method': token_response['creditCardToken']['paymentMethod'],
            })
            body_message = """
                <b><span style='color:green;'>PayU Latam - Proceso de tokenización exitoso</span></b><br/>
                <b>Token:</b> %s<br/>
                <b>Mascara:</b> %s<br/>
                <b>Documento:</b> %s<br/>
                <b>Metodo:</b> %s
            """ % (
                token_response['creditCardToken']['creditCardTokenId'],
                token_response['creditCardToken']['maskedNumber'],
                token_response['creditCardToken']['identificationNumber'],
                token_response['creditCardToken']['paymentMethod']
            )
            order.message_post(body=body_message, type="comment")
        else:
            render_values = {'error': token_response['error']}
            render_values.update({
                'order_id': order
            })
            body_message = """
                <b><span style='color:red;'>PayU Latam - Error en proceso de tokenizacion</span></b><br/>
                <b>Error:</b> %s
            """ % (
                token_response['error'], 
            )
            order.message_post(body=body_message, type="comment")
            return request.render("web_sale_extended.payulatam_rejected_process", render_values)
        
        _logger.error(token_response)
        tx_value = {"value": order.amount_total, "currency": "COP"}
        tx_tax = {"value": 0,"currency": "COP"}
        tx_tax_return_base = {"value": 0, "currency": "COP"}
        additionalValues = {
            "TX_VALUE": tx_value,
            "TX_TAX": tx_tax,
            "TX_TAX_RETURN_BASE": tx_tax_return_base
        }
        shippingAddress = {
            "street1": order.partner_id.street,
            "street2": "",
            "city": order.partner_id.zip_id.city_id.name,
            "state": order.partner_id.zip_id.city_id.state_id.name,
            "country": "CO",
            "postalCode": order.partner_id.zip_id.name,
            "phone": order.partner_id.phone
        }    
        buyer = {
            "merchantBuyerId": "1",
            "fullName": order.partner_id.name,
            "emailAddress": order.partner_id.email,
            "contactPhone": order.partner_id.phone,
            "dniNumber": order.partner_id.identification_document,
        }    
        order_api = {
            "accountId": accountId,
            "referenceCode": referenceCode,
            "description": 'PPS - ' + descriptionPay,
            "language": "es",
            "signature": signature,
            "notifyUrl":payulatam_response_url,
            "additionalValues": additionalValues,
            "buyer": buyer,
            "shippingAddress": shippingAddress
        }
        billingAddressPayer = {
            "street1": post['credit_card_partner_street'],
            "street2": "",
            "city": "Bogota",
            "state": "Bogota DC",
            "country": "CO",
            "postalCode": post['credit_card_zip'],
            "phone": post['credit_card_partner_phone']
        }    
        payer = {
            "merchantPayerId": "1",
            "fullName": post['credit_card_billing_firstname'] + ' ' + post['credit_card_billing_lastname'],
            "emailAddress": post['credit_card_billing_email'],
            "contactPhone": post['credit_card_partner_phone'],
            "dniNumber": post['credit_card_partner_document'],
            #"billingAddress": post['credit_card_partner_street']
        }
        
        without_token = 1
        if without_token:
            credit_card = {
                "number": post['credit_card_number'],
                "securityCode": post['credit_card_code'],
                "expirationDate": post['credit_card_due_year'] + "/" + post['credit_card_due_month'],
                "name": post['credit_card_name']
            }
            transaction = {
                "order": order_api,
                "payer": payer,
                "creditCard": credit_card,
                "type": "AUTHORIZATION_AND_CAPTURE",
                "paymentMethod": post['method_id'],
                "paymentCountry": "CO",
                "deviceSessionId": request.httprequest.cookies.get('session_id'),
                "ipAddress": "127.0.0.1",
                "cookie": request.httprequest.cookies.get('session_id'),
                #"userAgent": "Mozilla/5.0 (X11; Linux x86_64; rv:52.0) Gecko/20100101"
                "userAgent": "Firefox"
            }
        else:
            transaction = {
                "order": order_api,
                "payer": payer,
                "creditCardTokenId": order.payulatam_credit_card_token,
                "type": "AUTHORIZATION_AND_CAPTURE",
                "paymentMethod": post['method_id'],
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
        
        _logger.error(credit_card_values)
        response = request.env['api.payulatam'].payulatam_credit_cards_payment_request(credit_card_values)
        if response['code'] != 'SUCCESS':
            render_values = {'error': response['error']}
            render_values.update({
                'order_id': order
            })
            body_message = """
                <b><span style='color:red;'>PayU Latam - Error en pago con tarjeta de crédito</span></b><br/>
                <b>Código:</b> %s<br/>
                <b>Error:</b> %s
            """ % (
                response['code'],
                response['error'], 
            )
            order.message_post(body=body_message, type="comment")
            return request.render("web_sale_extended.payulatam_rejected_process", render_values)
    
        order.message_post(body=body_message, type="comment")
        if response['transactionResponse']['state'] == 'APPROVED':
            order.write({
                'payulatam_order_id': response['transactionResponse']['orderId'],
                'payulatam_transaction_id': response['transactionResponse']['transactionId'],
                'payulatam_state': response['transactionResponse']['state'],
                'payment_method_type': 'Credit Card',
                'payulatam_state': 'TRANSACCIÓN CON TARJETA DE CRÉDITO APROBADA',
                'payulatam_datetime': fields.datetime.now(),
            })
            order.action_payu_approved()
            render_values = {
                'error': '',
                'transactionId': response['transactionResponse']['transactionId'],
                'state': 'APROBADO',
                'responseCode': response['transactionResponse']['responseCode'],
                'order_Id': response['transactionResponse']['orderId'],
                'order_id': order
            }
            body_message = """
                <b><span style='color:green;'>PayU Latam - Transacción de pago con tarjeta de crédito</span></b><br/>
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
            #order.action_confirm()
            return request.render("web_sale_extended.payulatam_success_process", render_values)
        elif response['transactionResponse']['state'] == 'PENDING':
            order.write({
                'payulatam_order_id': response['transactionResponse']['orderId'],
                'payulatam_transaction_id': response['transactionResponse']['transactionId'],
                'payulatam_state': response['transactionResponse']['state'],
                'payment_method_type': 'Credit Card',
                'payulatam_state': 'TRANSACCIÓN CON TARJETA DE CRÉDITO PENDIENTE DE APROBACIÓN',
                'payulatam_datetime': fields.datetime.now(),
            })
            order.action_payu_confirm()
            error = 'Transacción %s en estado : %s' % (
                response['transactionResponse']['transactionId'],response['transactionResponse']['pendingReason']
            )
            render_values = {'error': error}
            render_values.update({
                'state': response['transactionResponse']['state'],
                'transactionId': response['transactionResponse']['transactionId'],
                'responseCode': response['transactionResponse']['responseCode'],
                'order_Id': response['transactionResponse']['orderId'],
                'order_id': order
            })
            body_message = """
                <b><span style='color:orange;'>PayU Latam - Transacción de pago con tarjeta de crédito</span></b><br/>
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
            request.session['sale_order_id'] = None
            request.session['sale_transaction_id'] = None
            return request.render("web_sale_extended.payulatam_success_process_pending", render_values)
        elif response['transactionResponse']['state'] in ['EXPIRED', 'DECLINED']:
            order.write({
                'payulatam_order_id': response['transactionResponse']['orderId'],
                'payulatam_transaction_id': response['transactionResponse']['transactionId'],
                'payulatam_state': response['transactionResponse']['state'],
                'payment_method_type': 'Credit Card',
                'payulatam_state': 'TRANSACCIÓN CON TARJETA DE CRÉDITO RECHAZADA',
                'payulatam_datetime': fields.datetime.now(),
            })
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
                <b><span style='color:red;'>PayU Latam - Transacción de pago con tarjeta de crédito</span></b><br/>
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
            return request.render("web_sale_extended.payulatam_rejected_process", render_values)
        else:
            error = 'Transacción en estado %s: %s' % (
                response['transactionResponse']['transactionId'],response['status']
            )
            order.action_cancel()
            render_values = {'error': error}
            render_values.update({
                'state': response['transactionResponse']['state'],
                'transactionId': response['transactionResponse']['transactionId'],
                'responseCode': response['transactionResponse']['responseCode'],
                'order_Id': response['transactionResponse']['orderId'],
                'order_id': order
            })
            return request.render("web_sale_extended.payulatam_rejected_process", render_values)

