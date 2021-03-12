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
    
    
    @http.route(['/shop/payment'], type='http', auth="public", website=True, sitemap=False)
    def payment(self, **post):
        """ Payment step. This page proposes several payment means based on available
        payment.acquirer. State at this point :
         - a draft sales order with lines; otherwise, clean context / session and
           back to the shop
         - no transaction in context / session, or only a draft one, if the customer
           did go to a payment.acquirer website but closed the tab without
           paying / canceling
        """
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
        
        _logger.error(bank_list)
        
        mode = (False, False)
        country = request.env['res.country'].browse(49)
        credit_card_due_year_ids = list(range(2021, 2061))
        _logger.error(credit_card_methods)
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
    
     
    @http.route(['/shop/payment/payulatam-gateway-api'], type='http', auth="public", website=True, sitemap=False)
    def payulatam_gateway_api(self, **post):
        order = request.website.sale_get_order()
        """ verificaciones del estado de la orden """
        if not order:
            if not self.validate_csrf(token):
                if token is not None:
                    _logger.warn("sssssssssssCSRF validation failed on path '%s'",
                                 request.httprequest.path)
                else:
                    _logger.warn("sssssssNo CSRF validation token provided for path '%s'")
        
        
        """ Proceso de Pago """
        referenceCode = str(request.env['api.payulatam'].payulatam_get_sequence())
        accountId = request.env['api.payulatam'].payulatam_get_accountId()
        descriptionPay = "Payment Origin from " + order.name
        signature = request.env['api.payulatam'].payulatam_get_signature(
            order.amount_total,'COP',referenceCode)
        
        # validando tarjeta
        _logger.error("**********************+TARJETA DE CREDITO LUNH")
        luhn_ok = request.env['api.payulatam'].luhn_checksum(post['credit_card_number'])
        if not luhn_ok:
            render_values = {'error': 'Número de tarjeta invalido'}
            return request.render("web_sale_extended.payulatam_rejected_process", render_values)
        
        """ Proceso de Tokenización """
        creditCardToken = {
            "payerId": str(order.partner_id.id),
            "name": post['credit_card_billing_firstname'] + ' ' + post['credit_card_billing_lastname'],
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
        else:
            render_values = {'error': token_response['error']}
            render_values.update({
                'order_id': order
            })
            return request.render("web_sale_extended.payulatam_rejected_process", render_values)
            _logger.error('Procesooooooooooooooooooooooooooooooooooo de tokenizaciónnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnn')
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
            #"city": "Bogota",
            "state": order.partner_id.zip_id.city_id.state_id.name,
            #"state": "Bogota DC",
            "country": "CO",
            "postalCode": order.partner_id.zip_id.name,
            "phone": order.partner_id.phone
        }    
        buyer = {
            "merchantBuyerId": "1",
            #"fullName": order.partner_id.name,
            "fullName": 'APPROVED',
            "emailAddress": order.partner_id.email,
            "contactPhone": order.partner_id.phone,
            "dniNumber": order.partner_id.identification_document,
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
            #"fullName": post['credit_card_billing_firstname'] + ' ' + post['credit_card_billing_lastname'],
            "fullName": 'APPROVED',
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
            creditCardTokenId = {
                "creditCardTokenId": order.payulatam_credit_card_token,
            }
            transaction = {
                "order": order_api,
                "payer": payer,
                "creditCardTokenId": creditCardTokenId,
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
        response = request.env['api.payulatam'].payulatam_credit_cards_payment_request(credit_card_values)
        if response['code'] != 'SUCCESS':
            _logger.error(response)
            render_values = {'error': response['error']}
            render_values.update({
                'order_id': order
            })
            return request.render("web_sale_extended.payulatam_rejected_process", render_values)
        _logger.error(response)
        """poniendo mensaje en la orden de venta con la respuesta de PayU"""
        body_message = """
            <b>PayU Latam - Transacción de Pago</b><br/>
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
            order.action_confirm()
            render_values = {
                'error': '',
                'transactionId': response['transactionResponse']['transactionId'],
                'state': response['transactionResponse']['state'],
                'responseCode': response['transactionResponse']['responseCode'],
                'order_Id': response['transactionResponse']['orderId'],
                'order_id': order
            }
            return request.render("web_sale_extended.payulatam_success_process", render_values)
        elif response['transactionResponse']['state'] == 'PENDING':
            _logger.info('Notificación Recibida para el pago de PayU Latam: %s: establecido como PENDIENTE' % (response['transactionResponse']['orderId']))
            order.action_confirm()
            error = 'Se recibió un estado no reconocido para el pago de PayU Latam %s: %s, set as error' % (
                response['transactionResponse']['transactionId'],response['status']
            )
            render_values = {'error': error}
            render_values.update({
                'state': response['transactionResponse']['state'],
                'transactionId': response['transactionResponse']['transactionId'],
                'responseCode': response['transactionResponse']['responseCode'],
                'order_Id': response['transactionResponse']['orderId'],
                'order_id': order
            })
            return request.render("web_sale_extended.payulatam_success_process", render_values)
        elif response['transactionResponse']['state'] in ['EXPIRED', 'DECLINED']:
            _logger.info('Notificación recibida para el pago PayU Latam %s: Orden Cancelada' % (response['transactionResponse']['transactionId']))
            render_values = {'error': '',}
            order.action_confirm()
            if response['transactionResponse']['paymentNetworkResponseErrorMessage']:
                render_values.update({'error': response['transactionResponse']['paymentNetworkResponseErrorMessage']})
            render_values.update({
                'state': response['transactionResponse']['state'],
                'transactionId': response['transactionResponse']['transactionId'],
                'responseCode': response['transactionResponse']['responseCode'],
                'order_Id': response['transactionResponse']['orderId'],
                'order_id': order
            })
            _logger.error('************************************99999999999999999999999999999**********************************++1')
            return request.render("web_sale_extended.payulatam_success_process", render_values)
        else:
            error = 'Se recibió un estado no reconocido para el pago de PayU Latam %s: %s, set as error' % (
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
            return request.render("web_sale_extended.payulatam_success_process", render_values)



    @http.route(['/shop/payment/payulatam-gateway-api/cash_process'], type='http', auth="public", website=True, sitemap=False)
    def payulatam_gateway_api_cash_payment(self, **post):
        order = request.website.sale_get_order()
        _logger.error('*********************2cara2222222222222222221111111111111111122222222222**********************')
        """ Proceso de Pago """
        referenceCode = str(request.env['api.payulatam'].payulatam_get_sequence())
        accountId = request.env['api.payulatam'].payulatam_get_accountId()
        descriptionPay = "Payment Cash Origin from " + order.name
        signature = request.env['api.payulatam'].payulatam_get_signature(
            order.amount_total,'COP',referenceCode)
        
        tx_value = {"value": order.amount_total, "currency": "COP"}
        tx_tax = {"value": 0,"currency": "COP"}
        tx_tax_return_base = {"value": 0, "currency": "COP"}
        additionalValues = {
            "TX_VALUE": tx_value,
            "TX_TAX": tx_tax,
            "TX_TAX_RETURN_BASE": tx_tax_return_base
        }
        buyer = {
            "merchantBuyerId": "1",
            "fullName": post['cash_billing_firstname'] + ' ' + post['cash_billing_lastname'],
            #"fullName": 'APPROVED',
            "emailAddress": order.partner_id.email,
            "contactPhone": order.partner_id.phone,
            "dniNumber": order.partner_id.identification_document,
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
        transaction = {
            "order": order_api,
            "type": "AUTHORIZATION_AND_CAPTURE",
            #"paymentMethod": post['method_id'],
            "paymentMethod": "BALOTO",
            "expirationDate": "2021-05-10T00:00:00",
            "paymentCountry": "CO",
            #"deviceSessionId": request.httprequest.cookies.get('session_id'),
            "ipAddress": "127.0.0.1",
            #"cookie": request.httprequest.cookies.get('session_id'),
            #"userAgent": "Mozilla/5.0 (X11; Linux x86_64; rv:52.0) Gecko/20100101"
            #"userAgent": "Firefox"
        }
        credit_card_values = {
            "command": "SUBMIT_TRANSACTION",
            "transaction": transaction,
        }
        _logger.error('*********************22222222222222222221111111111111111122222222222**********************')
        response = request.env['api.payulatam'].payulatam_credit_cards_payment_request(credit_card_values)
        if response['code'] != 'SUCCESS':
            _logger.error(response)
            render_values = {'error': response['error']}
            return request.render("web_sale_extended.payulatam_rejected_process", render_values)
        _logger.error(response)
        """poniendo mensaje en la orden de venta con la respuesta de PayU"""
        body_message = """
            <b>PayU Latam - Transacción de Pago</b><br/>
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
            order.action_confirm()
            render_values = {
                'error': '',
                'transactionId': response['transactionResponse']['transactionId'],
                'state': response['transactionResponse']['state'],
                'responseCode': response['transactionResponse']['responseCode'],
                'order_Id': response['transactionResponse']['orderId'],
                'order_id': order
            }
            return request.render("web_sale_extended.payulatam_success_process_cash", render_values)
        elif response['transactionResponse']['state'] == 'PENDING':
            _logger.info('Notificación Recibida para el pago de PayU Latam: %s: establecido como PENDIENTE' % (response['transactionResponse']['orderId']))
            order.action_confirm()
            error = 'Se recibió un estado no reconocido para el pago de PayU Latam %s: %s, set as error' % (
                response['transactionResponse']['transactionId'],response['transactionResponse']['state']
            )
            render_values = {'error': error}
            render_values.update({
                'state': response['transactionResponse']['state'],
                'transactionId': response['transactionResponse']['transactionId'],
                'responseCode': response['transactionResponse']['responseCode'],
                'order_Id': response['transactionResponse']['orderId'],
                'order_id': order
            })
            return request.render("web_sale_extended.payulatam_success_process_cash", render_values)
        elif response['transactionResponse']['state'] in ['EXPIRED', 'DECLINED']:
            _logger.info('Notificación recibida para el pago PayU Latam %s: Orden Cancelada' % (response['transactionResponse']['transactionId']))
            render_values = {'error': '',}
            order.action_confirm()
            if response['transactionResponse']['paymentNetworkResponseErrorMessage']:
                render_values.update({'error': response['transactionResponse']['paymentNetworkResponseErrorMessage']})
            render_values.update({
                'state': response['transactionResponse']['state'],
                'transactionId': response['transactionResponse']['transactionId'],
                'responseCode': response['transactionResponse']['responseCode'],
                'order_Id': response['transactionResponse']['orderId'],
                'order_id': order
            })
            _logger.error('************************************99999999999999999999999999999**********************************++1')
            return request.render("web_sale_extended.payulatam_success_process_cash", render_values)
        else:
            error = 'Se recibió un estado no reconocido para el pago de PayU Latam %s: %s, set as error' % (
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
            return request.render("web_sale_extended.payulatam_success_process_cash", render_values)
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
                
                
                
                
                
                
    @http.route(['/shop/payment/payulatam-gateway-api/pse_process'], type='http', auth="public", website=True, sitemap=False)
    def payulatam_gateway_api_pse(self, **post):
        order = request.website.sale_get_order()
        """ Proceso de Pago """
        referenceCode = str(request.env['api.payulatam'].payulatam_get_sequence())
        accountId = request.env['api.payulatam'].payulatam_get_accountId()
        descriptionPay = "Payment Origin from " + order.name
        signature = request.env['api.payulatam'].payulatam_get_signature(
            order.amount_total,'COP',referenceCode)
        
  
        tx_value = {"value": order.amount_total, "currency": "COP"}
        tx_tax = {"value": 0,"currency": "COP"}
        tx_tax_return_base = {"value": 0, "currency": "COP"}
        additionalValues = {
            "TX_VALUE": tx_value,
            "TX_TAX": tx_tax,
            "TX_TAX_RETURN_BASE": tx_tax_return_base
        }
        """
        shippingAddress = {
            "street1": order.partner_id.street,
            "street2": "",
            "city": order.partner_id.zip_id.city_id.name,
            #"city": "Bogota",
            "state": order.partner_id.zip_id.city_id.state_id.name,
            #"state": "Bogota DC",
            "country": "CO",
            "postalCode": order.partner_id.zip_id.name,
            "phone": order.partner_id.phone
        }
        """
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
            "RESPONSE_URL": "http://www.test.com/response",
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
            _logger.error(response)
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
            order.action_confim()
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
            order.action_confirm()
            error = ''
            render_values = {'error': error}
            render_values.update({
                'state': response['transactionResponse']['state'],
                'transactionId': response['transactionResponse']['transactionId'],
                'responseCode': response['transactionResponse']['responseCode'],
                'order_Id': response['transactionResponse']['orderId'],
                'bank_url': response['transactionResponse']['orderId'],
                'order_id': order,
                'bank_url': response['transactionResponse']['extraParameters']['BANK_URL'],
                'url_payment_receipt_pdf': response['transactionResponse']['extraParameters']['URL_PAYMENT_RECEIPT_PDF']
            })
            return request.render("web_sale_extended.payulatam_success_process_pse", render_values)
        elif response['transactionResponse']['state'] in ['EXPIRED', 'DECLINED']:
            order.action_confirm()
            _logger.info('Notificación recibida para el pago PayU Latam %s: Orden Cancelada' % (response['transactionResponse']['transactionId']))
            
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
            return request.render("web_sale_extended.payulatam_success_process_pse", render_values)
        else:
            error = 'Se recibió un estado no reconocido para el pago de PayU Latam %s: %s, set as error' % (
                response['transactionResponse']['transactionId'],response['status']
            )
            order.action_cancel()
            render_values = {'error': error}
            return request.render("web_sale_extended.payulatam_rejected_process_pse", render_values)
        
        
