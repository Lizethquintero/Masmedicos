# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging
import uuid
import json
from hashlib import md5
from werkzeug import urls
from datetime import datetime
from odoo import api, fields, models, _
from odoo.addons.payment.models.payment_acquirer import ValidationError
from odoo.tools.float_utils import float_compare
import requests
from requests.auth import HTTPBasicAuth


_logger = logging.getLogger(__name__)


class PayULatamApi(models.TransientModel):
    _name = "api.payulatam"
    _description = "Api PayU Latam"
    
    value = fields.Integer('Valor de la Compra', readonly="True")
    currency = fields.Char('Moneda', readonly="True", default='COP')
    language = fields.Char('Moneda', readonly="True", default='es')
    
    
    def request_payulatam_api(self, endpoint: str, query: dict) -> dict:
        payulatam_api_env = self.env.user.company_id.payulatam_api_env
        
        if payulatam_api_env == 'prod':
            payulatam_merchant_id = self.env.user.company_id.payulatam_merchant_id
            payulatam_account_id = self.env.user.company_id.payulatam_account_id
            payulatam_api_key = self.env.user.company_id.payulatam_api_key
            payulatam_api_login = self.env.user.company_id.payulatam_api_login
        else:
            """datos de cuenta para sandbox, vienen de la documentación"""
            payulatam_merchant_id = '508029'
            payulatam_account_id = '512321'
            payulatam_api_key = '4Vj8eK4rloUd272L48hsrarnUA'
            payulatam_api_login = 'pRRXKOl8ikMmt9u'
        
        language = self.language if self.language else 'es'
        api_post = ['PING','GET_PAYMENT_METHODS','SUBMIT_TRANSACTION','AUTHORIZATION_AND_CAPTURE','GET_BANKS_LIST','CREATE_TOKEN']
        
        if endpoint in api_post:
            headers = {'accept': 'application/json', 'Content-Type': 'application/json'}
            provider = 'https://sandbox.api.payulatam.com/payments-api/4.0/service.cgi'
            if payulatam_api_env == 'prod':
                provider = 'https://api.payulatam.com/payments-api/4.0/service.cgi'
                
            auth = HTTPBasicAuth('apikey', payulatam_api_key)
            headers = {'accept': 'application/json', 'Content-Type': 'application/json'}
            # general values
            query.update({
                'language': language,
                "merchant": {
                    "apiLogin": payulatam_api_login,
                    "apiKey": payulatam_api_key
                },
            })
            query.update({"test": True})
            if payulatam_api_env == 'prod':
                query.update({"test": False})
            
            
            _logger.error('******************1111111111111111111111111111111112')
            _logger.error(query)
            #query = json.dumps(query)
            _logger.error(query)
            response = requests.post(provider, json=query, auth=auth, headers=headers)
            if response.status_code != 200:
                _logger.error(f'****** ERROR {response.status_code}: validation failed, {response.json()}. ******')
                raise f'Bad Status Code, expected 200 but given {response.status_code}: validation failed, {response.json()}. ******'
            response.close
            return response.json()
        else:
            raise 'Error: Bad endpoint build for PayU Latam Api'
        
    def payulatam_ping(self):
        command = 'PING'
        query = {"command": command}
        response = self.request_payulatam_api(command, query)
        return response
    
    def payulatam_get_credit_cards_methods(self):
        command = 'GET_PAYMENT_METHODS'
        query = {"command": command}
        response = self.request_payulatam_api(command, query)
        if response['code'] == 'SUCCESS':
            payment_method_ids = response['paymentMethods']
            payment_method_list = {}
            for method in payment_method_ids:
                if method['country'] == 'CO' and method['enabled']:
                    payment_method_list.update({method['description']: method['description']})
            keys = [
                "VISA",
                "MASTERCARD",
                "DINERS",
                "CODENSA",
                "AMEX",
                "TEST CREDIT CARD"
            ]
            new_vals = {
                required_key: payment_method_list[required_key]
                for required_key in keys
                if required_key in payment_method_list
            }
            return new_vals
        
    def payulatam_credit_cards_payment_request(self, values):
        command = 'AUTHORIZATION_AND_CAPTURE'
        query = {"command": command}
        query.update(values)
        response = self.request_payulatam_api(command, query)
        return response
    
    def payulatam_cash_payment_request(self, values):
        command = 'AUTHORIZATION_AND_CAPTURE'
        query = {"command": command}
        query.update(values)
        response = self.request_payulatam_api(command, query)
        return response
        
        



    def payulatam_form_generate_values_api(self, values):
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        tx = self.env['payment.transaction'].search([('reference', '=', values.get('reference'))])
        # payulatam will not allow any payment twise even if payment was failed last time.
        # so, replace reference code if payment is not done or pending.
        if tx.state not in ['done', 'pending']:
            tx.reference = str(uuid.uuid4())
        payulatam_values = dict(
            values,
            merchantId=self.payulatam_merchant_id,
            accountId=self.payulatam_account_id,
            description=values.get('reference'),
            referenceCode=tx.reference,
            amount=values['amount'],
            tax='0',  # This is the transaction VAT. If VAT zero is sent the system, 19% will be applied automatically. It can contain two decimals. Eg 19000.00. In the where you do not charge VAT, it should should be set as 0.
            taxReturnBase='0',
            currency=values['currency'].name,
            buyerEmail=values['partner_email'],
            responseUrl=urls.url_join(base_url, '/payment/payulatam-gateway-api/response'),
        )
        payulatam_values['signature'] = self._payulatam_generate_sign("in", payulatam_values)
        return payulatam_values


    def payulatam_get_sequence(self):
        sequence_id =  self.env.user.company_id.payulatam_api_ref_seq_id
        referenceCode = sequence_id.number_next_actual
        sequence_id.write({
            'number_next_actual': int(sequence_id.number_next_actual) + 1,
        })
        return referenceCode
        
    def payulatam_get_accountId(self):
        payulatam_api_env = self.env.user.company_id.payulatam_api_env
        payulatam_account_id = '512321'
        if payulatam_api_env == 'prod':
            payulatam_account_id = self.env.user.company_id.payulatam_account_id
        return payulatam_account_id
    
    def payulatam_get_signature(self, amount_value, currency, referenceCode):
        payulatam_api_env = self.env.user.company_id.payulatam_api_env
        if payulatam_api_env == 'prod':
            payulatam_merchant_id = self.env.user.company_id.payulatam_merchant_id
            payulatam_api_key = self.env.user.company_id.payulatam_api_key
        else:
            """datos de cuenta para sandbox, vienen de la documentación"""
            payulatam_merchant_id = '508029'
            payulatam_api_key = '4Vj8eK4rloUd272L48hsrarnUA'
        data_string = ('~').join((payulatam_api_key, payulatam_merchant_id, str(referenceCode),
                                      str(int(amount_value)), currency))
        data_string = md5(data_string.encode('utf-8')).hexdigest()
        return data_string
    
    
    def luhn_checksum(self, card_number):
        sum = 0
        num_digits = len(card_number)
        oddeven = num_digits & 1
        for count in range(0, num_digits):
            digit = int(card_number[count])
            if not (( count & 1 ) ^ oddeven ):
                digit = digit * 2
            if digit > 9:
                digit = digit - 9
            sum = sum + digit
        return ( (sum % 10) == 0 )
    
    def payulatam_get_bank_list(self):
        command = 'GET_BANKS_LIST'
        query = {"command": command}
        bankListInformation = {
            "paymentMethod": "PSE",
            "paymentCountry": "CO"
        }
        query.update({
            'bankListInformation': bankListInformation,
        })
        response = self.request_payulatam_api(command, query)
        if response['code'] == 'SUCCESS':
            payment_method_ids = response['banks']
            payment_method_list = []
            for method in payment_method_ids:
                payment_method_list.append({
                    method['description']: method['description'],
                    method['pseCode']: method['pseCode']
                })
            """
            keys = [
                "VISA",
                "MASTERCARD",
                "DINERS",
                "CODENSA",
                "AMEX",
                "TEST CREDIT CARD"
            ]
            new_vals = {
                required_key: payment_method_list[required_key]
                for required_key in keys
                if required_key in payment_method_list
            }
            return new_vals
            """
            return dict(payment_method_list)
        
    def payulatam_get_credit_Card_token(self, creditCardToken):
        command = 'CREATE_TOKEN'
        query = {"command": command}
        query.update({
            'creditCardToken': creditCardToken,
        })
        response = self.request_payulatam_api(command, query)
        return response
        