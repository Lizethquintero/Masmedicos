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
import time
_logger = logging.getLogger(__name__)



class WebsiteSaleExtended(WebsiteSale):


    
    def _checkout_form_save(self, mode, checkout, all_values):
        Partner = request.env['res.partner']
        if mode[0] == 'new':
            _logger.info("****CREANDO TERCERO NUEVO*****")
            _logger.info(checkout)
            #zip_id = checkout.pop('zip_id')
            partner_id = Partner.sudo().with_context(tracking_disable=True, skip_check_zip=True).create(checkout)
            #partner_id.write({'zip_id': zip_id})
        elif mode[0] == 'edit':
            _logger.info("****EDITANDO TERCERO*****")
            _logger.info(checkout)
            partner_id = int(all_values.get('partner_id', 0))
            if partner_id:
                # double check
                order = request.website.sale_get_order()
                shippings = Partner.sudo().search([("id", "child_of", order.partner_id.commercial_partner_id.ids)])
                if partner_id not in shippings.mapped('id') and partner_id != order.partner_id.id:
                    return Forbidden()
                
                
                if "zip" in checkout:
                    checkout.pop('zip')
                if "city" in checkout:
                    checkout.pop('city')
                if "user_id" in checkout:
                    checkout.pop('user_id')
                if "name" in checkout:
                    checkout.pop('name')
                if "zip_id" in checkout:
                    checkout.pop('zip_id')
                if "state_id" in checkout:
                    checkout.pop('state_id')
                Partner.browse(partner_id).sudo().write(checkout)

        return partner_id


    @http.route(['/shop/tusdatos_request_confirmation'], type='http', methods=['GET', 'POST'], auth="public", website=True, sitemap=False)
    def tusdatos_request_confirmation(self, **kw):
        order = request.website.sale_get_order()

        #redirection = self.checkout_redirection(order)
        #if redirection:
        #    return redirection

        order.onchange_partner_shipping_id()
        order.order_line._compute_tax_id()
        request.session['sale_last_order_id'] = order.id
        request.website.sale_get_order(update_pricelist=True)
        extra_step = request.website.viewref('website_sale.extra_info_option')
        if extra_step.active:
            return request.redirect("/shop/extra_info")

        #return request.redirect("/shop/payment")


        render_values = {
            'order': order,
        }
        return request.render("web_sale_extended.tusdatos_request_confirmation", render_values)


    # toma de datos de pago y se crea el asegurador principal
    @http.route(['/shop/address'], type='http', methods=['GET', 'POST'], auth="public", website=True, sitemap=False)
    def address(self, errortusdatos= '', **kw):
        
        
        ''' Toma de datos de pago y se crea el asegurador principal '''

        Partner = request.env['res.partner'].with_context(show_address=1).sudo()
        order = request.website.sale_get_order()
        order_detail = request.env['sale.order.line'].sudo().search([('order_id', "=", int(order.id))])
        #redirection = self.checkout_redirection(order)
        #if redirection:
        #    return redirection

        mode = (False, False)
        can_edit_vat = False
        def_country_id = order.partner_id.country_id
        values, errors = {}, {}

        partner_id = int(kw.get('partner_id', -1))

        # IF PUBLIC ORDER
        if order.partner_id.id == request.website.user_id.sudo().partner_id.id:
            mode = ('new', 'billing')
            can_edit_vat = True
            country_code = request.session['geoip'].get('country_code')
            if country_code:
                def_country_id = request.env['res.country'].search([('code', '=', country_code)], limit=1)
            else:
                def_country_id = request.website.user_id.sudo().country_id
        # IF ORDER LINKED TO A PARTNER
        else:
            if partner_id > 0:
                if partner_id == order.partner_id.id:
                    mode = ('edit', 'billing')
                    can_edit_vat = order.partner_id.can_edit_vat()
                else:
                    shippings = Partner.search([('id', 'child_of', order.partner_id.commercial_partner_id.ids)])
                    if partner_id in shippings.mapped('id'):
                        mode = ('edit', 'shipping')
                    else:
                        return Forbidden()
                if mode:
                    values = Partner.browse(partner_id)
            elif partner_id == -1:
                mode = ('new', 'shipping')
            else:# no mode - refresh without post?
                _logger.info("****FORMULARIO PAGO!!!!!*****")
                return request.redirect('/shop/checkout')

        # IF POSTED
        if 'submitted' in kw:
            order.write({'tusdatos_email': kw['email']})
            _logger.info("****FORMULARIO*****")
            _logger.info(kw)
            _logger.info(' '.join([order.tusdatos_request_id, str(order.tusdatos_approved), order.tusdatos_email]))
            pre_values = self.values_preprocess(order, mode, kw)
            errors, error_msg = self.checkout_form_validate(mode, kw, pre_values)
            post, errors, error_msg = self.values_postprocess(order, mode, pre_values, errors, error_msg)

            if errors:
                errors['error_message'] = error_msg
                values = kw
            else:
                if kw['othernames'] == '':
                    post['othernames'] = ' '
                else:
                    post['othernames'] = kw['othernames']

                post['firstname'] = kw['name']
                post['lastname'] = kw['lastname']
                post['lastname2'] = kw['lastname2']
                post['document_type_id'] = int(kw["document"])
                post['person_type'] = "2"
                post['identification_document'] = kw["identification_document"]
                post["birthdate_date"] = kw["birthdate_date"]
                #post["city_id"] = kw["city"]
                post["zip"] = kw["zip"]
                post["zip_id"] = kw["zip_id"]
                post["state_id"] = kw["state_id"]

                _logger.info("\n****ZIP ID*****\n")
                _logger.info(post["zip_id"])
                partner_id = self._checkout_form_save(mode, post, kw)
                if mode[1] == 'billing':
                    order.partner_id = partner_id
                    order.with_context(not_self_saleperson=True).onchange_partner_id()
                    # This is the *only* thing that the front end user will see/edit anyway when choosing billing address
                    order.partner_invoice_id = partner_id
                    if not kw.get('use_same'):
                        kw['callback'] = kw.get('callback') or \
                            (not order.only_services and (mode[0] == 'edit' and '/shop/checkout' or '/shop/address'))
                elif mode[1] == 'shipping':
                    order.partner_shipping_id = partner_id

                # TDE FIXME: don't ever do this
                order.message_partner_ids = [(4, partner_id), (3, request.website.partner_id.id)]
                order.write({
                    'require_signature': False,
                    'require_payment': True,
                })

                #send mail
                #template = request.env['mail.template'].sudo().search([('tusdatos_process_send','=', True)], limit=1)

                if not errors:
                    if not order.tusdatos_request_id:
                        document_types = {'3': 'CC', '5':'CE', '8':'PEP', '7':'PP'}
                        expedition_date = kw["expedition_date"]
                        expedition_date = '/'.join(expedition_date.split('-')[::-1])
                        _logger.info("\n****TUS DATOS*****\n")
                        tusdatos_validation = request.env['api.tusdatos'].launch_query_tusdatos(str(kw["identification_document"]),
                                                                                                document_types[str(kw["document"])],
                                                                                                expedition_date)
                        #_logger.info(tusdatos_validation)
                        if tusdatos_validation and tusdatos_validation.get('process_id'):
                            order.write({'tusdatos_request_id': tusdatos_validation['process_id']})
                        elif tusdatos_validation and tusdatos_validation.get('error'):
                            #return request.render("web_sale_extended.address", kw)
                            #return werkzeug.utils.redirect('/shop/address')
                            #errors['error_message'] = tusdatos_validation.get('error')
                            _logger.info("\n****OOOOOOOOOOOOOOOOOOOOOOOOOooTUS DATOS ORDER*****\n")
                            
                            #return request.redirect(kw.get('callback'))
                            #order.action_cancel()
                            return werkzeug.utils.redirect('/shop/address?errortusdatos=document_invalid')
                            
                           
                            
                        # TODO: add to queue! @Jhair The process in queue is order.tusdatos_approval()
                        # TODO: fix the redirection
                        _logger.info("\n****TUS DATOS ORDER*****\n")
                        _logger.info(' '.join([order.tusdatos_request_id, order.tusdatos_email]))


                        render_values = {
                            'email': kw['email'],
                        }
                        return request.redirect(kw.get('callback') or '/shop/confirm_order')
                        #if not errors:
                        #    return request.redirect('/shop/tusdatos_request_confirmation')
                    elif not order.tusdatos_approved and order.tusdatos_request_id:
                        # TODO: DELAY approval order
                        # order.tusdatos_approval()
                        _logger.info("\n****TUS DATOS ORDER2*****\n")
                        _logger.info(' '.join([order.tusdatos_request_id, str(order.tusdatos_approved)]))
                        # TODO: fix redirection
                        #return request.redirect("/web")
                        return request.redirect(kw.get('callback') or '/shop/confirm_order')
                        #return request.redirect('/shop/tusdatos_request_confirmation')



                    if not errors:
                        return request.redirect(kw.get('callback') or '/shop/confirm_order')

        country = 'country_id' in values and values['country_id'] != '' and request.env['res.country'].browse(int(values['country_id']))
        country = country and country.exists() or def_country_id
        fiscal_position_ids = request.env['account.fiscal.position'].sudo().search([
            ('active', '=', True),
            ('website_published', '=', True),
        ])
        
        if errortusdatos:
            errors['error_message'] = errortusdatos
        
        render_values = {
            'website_sale_order': order,
            'partner_id': partner_id,
            'mode': mode,
            'checkout': values,
            'can_edit_vat': can_edit_vat,
            'country': country,
            'country_states': country.get_website_sale_states(mode=mode[1]),
            'countries': country.get_website_sale_countries(mode=mode[1]).filtered(lambda line: line.id == 49),
            'fiscal_position_ids': fiscal_position_ids,
            'error': errors,
            'callback': kw.get('callback'),
            #'cities': self.get_cities(),
            'cities': [],
            'document_types': self.get_document_types('payment'),
            'product': request.env['product.product'].sudo().browse(3),
            # 'fiscal_position': self.get_fiscal_position(),
            'only_services': order and order.only_services,
            'order_detail': order_detail,
        }
        return request.render("web_sale_extended.address", render_values)


    def get_cities(self, department=None):
        ''' LISTADOS DE TODAS LAS CIUDADES '''
        domain = []
        if department:
            domain.append(('city_id.state_id', '=', department))
        complete_cities_with_zip = request.env['res.city.zip'].sudo().search(domain)

        return complete_cities_with_zip
        #return []

    def get_document_types(self, type='All'):
        ''' LISTADOS DE TODOS LOS TIPOS DE DOCUMENTO '''

        if type == "payment":
            document_type = request.env['res.partner.document.type'].sudo().search([
                ('id','not in',[11,1,2,4,6,10,9]),
            ], order='name')
        elif type == "beneficiary":
            document_type = request.env['res.partner.document.type'].sudo().search([
                ('id','not in',[4,6,10,9]),
            ], order='name')
        else:
            document_type = request.env['res.partner.document.type'].sudo().search([], order='name')
        return document_type




    @http.route(['/my/order/beneficiaries/<int:order_id>'], type='http', methods=['GET', 'POST'], auth="public", website=True, sitemap=False)
    def get_data_beneficiary(self, order_id, **kwargs):

        ''' Captura de datos del beneficiario más no guarda informacion '''
        _logger.info("**BENEFICIARY**")

        #_logger.info(request.env.user.email)
        #InsurerPartner = request.env['res.partner'].search([('email', '=', request.env.user.email)], limit=1)

        #InsurerPartner_childs = request.env['res.partner'].search([
        #    ('parent_id', '=', InsurerPartner[0].id),
        #], limit=6)

        #order = request.env['sale.order'].sudo().search([('partner_id', "=", InsurerPartner[0].id)])
        #order_detail = request.env['sale.order.line'].sudo().search([('order_id', "=", int(order.id))])

        order = request.env['sale.order'].sudo().browse(order_id)
        _logger.error(order)
        product = order.order_line[0].product_id
        beneficiaries_number = product.product_tmpl_id.beneficiaries_number if product.product_tmpl_id.beneficiaries_number else 6

        country = request.env['res.country'].browse(int(order.partner_id.country_id))
        render_values = {
            "partner": order.partner_id,
            'country_states': country.get_website_sale_states(),
            'cities': self.get_cities(order.partner_id.state_id.id if order.partner_id.state_id else None),
            'countries': country.get_website_sale_countries().filtered(lambda line: line.id == 49),
            'document_types': self.get_document_types('beneficiary'),
            'country': country,
            'order_detail': order.order_line[0],
            'current_city':order.partner_id.zip_id.city_id.id,
            'beneficiaries_number': beneficiaries_number,
            'order_id': order.id,
        }
        return request.render("web_sale_extended.beneficiary", render_values)


    @http.route(['/beneficiary-detail'], type='http', methods=['GET', 'POST'], auth="public", website=True, sitemap=False)
    def create_beneficiary(self, print_policy=0, **kwargs):
        
        if int(print_policy):
            _logger.error('****************+PASANDO POR IMPRIMIR ==================================')
            
            
            

        ''' Guarda datos de los beneficiarios y los deja inactivo  '''
        _logger.info("***INFORME BENEFICIARIO***")
        _logger.info(kwargs)

        order = request.website.sale_get_order()
        #redirection = self.checkout_redirection(order)
        #if redirection:
        #    return redirection

        order_detail = order.order_line[0]
        Partner = order.partner_id
        BeneficiaryPartner = request.env['res.partner'].sudo()
        Subscription = order_detail.subscription_id
        beneficiary_list = []
        #if len(InsurerPartner_childs)>6:
        #    raise("Tienes muchos beneficiarios")
        #_logger.info(kwargs['beneficiario'])

        Partner.sudo().write({
            'firstname': kwargs['name'],
            'lastname': kwargs['lastname'],
            'lastname2':kwargs['lastname2'],
            'othernames': kwargs['othername'],
            'email': kwargs['email'],
            'mobile': kwargs['phone'],
            #'document_type_id': kwargs[document_type],
            'identification_document': kwargs['numero_documento'],
            'company_type': 'person',
            'active': True,
            'beneficiary_number': 1,
            'birthdate_date' : kwargs['date'],
            'gender' : kwargs['sex'],
            'marital_status' : kwargs['estado_civil'],
            #'parent_id': InsurerPartner
            'expedition_date' : kwargs['expedition_date']
        })
        beneficiary_list.append((4, Partner.id))
        order.write({
            'beneficiary0_id': Partner.id
        })

        for i in range(int(kwargs['beneficiario'])):
            firtst_name = "bfirstname"+str(i+1)
            other_name = "bfothername"+str(i+1)
            last_name = "bflastname"+str(i+1)
            last_name2 = "bflastname"+str(i+1)+"2"
            email = "bfemail"+str(i+1)
            document_type = "bfdocument"+str(i+1)
            identification_document = "bfnumero_documento"+str(i+1)
            country_id =  "bfcountry_id"+str(i+1)
            state_id = "bfdeparment"+str(i+1)
            city = "bfcity"+str(i+1)
            birthdate = "bfdate"+str(i+1)
            ocupation = "bfocupacion"+str(i+1)
            gender = "bfsex"+str(i+1)
            relationship = "bfparentesco"+str(i+1)
            address_beneficiary = "bfaddress"+str(i+1)
            phone = "bffijo"+str(i+1)
            mobile = "bfphone"+str(i+1)


            if kwargs[other_name] == '':
                kwargs[other_name] = ' '
            NewBeneficiaryPartner = BeneficiaryPartner.create({
                'firstname': kwargs[firtst_name],
                'lastname': kwargs[last_name],
                'lastname2':kwargs[last_name2],
                'othernames': kwargs[other_name],
                'email': kwargs[email],
                'person_type': "2",
                "phone": kwargs[phone],
                'mobile': kwargs[mobile],
                'document_type_id': int(kwargs[document_type]),
                'identification_document': kwargs[identification_document],
                'company_type': 'person',
                'active': True,
                'parent_id': Partner.id,
                'country_id': int(kwargs[country_id]),
                'state_id': int(kwargs[state_id]),
                'city': kwargs[city],
                'birthdate_date': kwargs[birthdate],
                #'marital_status': kwargs[marital_status],
                'ocupation': kwargs[ocupation],
                'gender': kwargs[gender],
                'relationship': kwargs[relationship],
                'address_beneficiary': kwargs[address_beneficiary],
                'beneficiary_number': i+2,
            })
            beneficiary_list.append((4, NewBeneficiaryPartner.id))
            if i == 0:
                order.write({
                    'beneficiary1_id': NewBeneficiaryPartner.id
                })
            if i == 1:
                order.write({
                    'beneficiary2_id': NewBeneficiaryPartner.id
                })
            if i == 2:
                order.write({
                    'beneficiary3_id': NewBeneficiaryPartner.id
                })
            if i == 3:
                order.write({
                    'beneficiary4_id': NewBeneficiaryPartner.id
                })
            if i == 4:
                order.write({
                    'beneficiary5_id': NewBeneficiaryPartner.id
                })
            if i == 5:
                order.write({
                    'beneficiary6_id': NewBeneficiaryPartner.id
                })


        Subscription.write({
            'subscription_partner_ids': beneficiary_list,
        })
        kwargs['order_detail'] = order_detail
        kwargs['partner'] = Partner

        return request.render("web_sale_extended.beneficiary_detail", kwargs)


    @http.route(['/beneficiary-submit'], type='http', methods=['GET', 'POST'], auth="public", website=True, sitemap=False)
    def beneficiary_submit(self, **kwargs):

        ''' Actualiza el estado de los beneficiarios a true '''

        InsurerPartner = request.env['res.partner'].search([('email', '=', request.env.user.email)], limit=1)
        InsurerPartner_childs = request.env['res.partner'].search([
            ('parent_id', '=', InsurerPartner[0].id), ('active', '=', False),
        ], limit=6)

        for beneficiary in InsurerPartner_childs:
            BeneficiaryPartner = request.env['res.partner'].browse(beneficiary.id)
            BeneficiaryPartner.sudo().write({'active': True})
            _logger.info("Beneficiario Activo")
            _logger.info(BeneficiaryPartner.firstname)

        #punto ideal para enviar el correo
        _logger.info('2****************************************\n\n++++++++++++++++++++++++++++++++++++')
        # Send Mail
        confirm_mail_template = request.env.ref('web_sale_extended.email_beneficiary_confirm_template')
        confirm_mail_template.sudo().send_mail(InsurerPartner[0].id)
        #if 1=1:
        #    context = dict(request.env.context)
        #    if confirm_mail_template:
        #        report_obj = request.env['ir.actions.report']
        #        report = report_obj._get_report_from_name('web_sale_extended.report_customreport_customeasytek_template_res_partner')
        #        pdf = report.render_qweb_pdf(InsurerPartner.id)[0]
        #        file_name = InsurerPartner.name
        #        b64_pdf = base64.b64encode(pdf)
        #        report_file = request.env['ir.attachment'].create({
        #            'name': file_name,
        #            'type': 'binary',
        #            'datas': b64_pdf,
        #            'datas_fname': file_name + '.pdf',
        #            'store_fname': file_name,
        #           'res_model': 'res.partner',
        #            'res_id': InsurerPartner.id,
         #           'mimetype': 'application/x-pdf'
         #       })
         #       values = confirm_mail_template.generate_email(InsurerPartner.id, fields=None)

          #      values['email_to'] = addr_to
           #     values['email_from'] = ''
           #     values['res_id'] = InsurerPartner.id
           #     values['attachment_ids'] = [(4, report_file.id)]
           #     if not values['email_to'] and not values['email_from']:
            #        pass
             #   mail_mail_obj = request.env['mail.mail']
              #  msg_id = mail_mail_obj.create(values)
               # if msg_id:
                #    mail_mail_obj.send(msg_id)
                 #   sendmail_ok = True

        return "Datos eviados correctamente"


    @http.route(['/report/beneficiary'],  methods=['GET'], type='http', auth="public", website=True)
    def report_poliza(self, city_id=None, **kwargs):
        report_obj = request.env['ir.actions.report']
        report = report_obj.sudo()._get_report_from_name('web_sale_extended.report_customreport_customeasytek_template')
        pdf = report.sudo().render_qweb_pdf()[0]
        file_name = "prueba"
        b64_pdf = base64.b64encode(pdf)
        report_file = request.env['ir.attachment'].sudo().create({
            'name': file_name,
            'type': 'binary',
            'datas': b64_pdf,
            # 'datas_fname': file_name + '.pdf',
            # 'store_fname': file_name,
            'res_model': 'res.partner',
            # 'res_id': 1,
            'mimetype': 'application/x-pdf'
        })
        return request.render(report_file, kwargs)


    # search cities by ajax peticion
    @http.route(['/search/cities'],  methods=['GET'], type='http', auth="public", website=True)
    def search_cities(self, city_id=None, **kwargs):
        ''' Busca las ciudades por departamentos en peticiones ajax retorna un json '''
        cities = []
        suggested_cities = request.env['res.city'].sudo().search([
            ('state_id', '=', int(kwargs['departamento']))
        ])
        complete_cities_with_zip = request.env['res.city.zip'].sudo().search([]).filtered(
            lambda line: line.city_id.state_id.id == int(kwargs['departamento'])).sorted(key=lambda r: r.city_id.name)

        #for city in suggested_cities:
        for city in complete_cities_with_zip:
            _logger.info(city.city_id.name)
            if city.city_id.state_id.id == int(kwargs['departamento']):
                cities.append({
                    'city': city.city_id.name.lower().title(),
                    'city_id': city.city_id.id,
                })
        data = {}
        data['status'] = True,
        data['error'] = None,
        data['data'] = {'cities': cities}
        return json.dumps(data)


    # search cities by ajax peticion
    @http.route(['/search/zipcodes'],  methods=['GET'], type='http', auth="public", website=True)
    def search_zipcodes(self, **kwargs):
        suggested_zipcode = request.env['res.city.zip'].sudo().search([('city_id', '=', int(kwargs['city_id']))], limit=1)
        data = {}
        data['status'] = True,
        data['error'] = None,
        data['data'] = {'zipcode': suggested_zipcode.name, 'zipid': suggested_zipcode.id}
        return json.dumps(data)


    def _get_shop_payment_values(self, order, **kwargs):
        values = dict(
            website_sale_order=order,
            errors=[],
            partner=order.partner_id.id,
            order=order,
            payment_action_id=request.env.ref('payment.action_payment_acquirer').id,
            return_url= '/shop/payment/validate',
            bootstrap_formatting= True
        )

        domain = expression.AND([
            ['&', ('state', 'in', ['enabled','test']), ('company_id', '=', order.company_id.id)],
            ['|', ('website_id', '=', False), ('website_id', '=', request.website.id)],
            ['|', ('country_ids', '=', False), ('country_ids', 'in', [order.partner_id.country_id.id])]
        ])
        acquirers = request.env['payment.acquirer'].search(domain)

        values['access_token'] = order.access_token
        values['acquirers'] = [acq for acq in acquirers if (acq.payment_flow == 'form' and acq.view_template_id) or
                                    (acq.payment_flow == 's2s' and acq.registration_view_template_id)]
        values['tokens'] = request.env['payment.token'].search(
            [('partner_id', '=', order.partner_id.id),
            ('acquirer_id', 'in', acquirers.ids)])

        if order:
            values['acq_extra_fees'] = acquirers.get_acquirer_extra_fees(order.amount_total, order.currency_id, order.partner_id.country_id.id)
        return values


    """
    @http.route(['/shop/payment'], type='http', auth="public", website=True, sitemap=False)
    def payment(self, **post):
        order = request.website.sale_get_order()
        
        
        redirection = self.checkout_redirection(order)
        if redirection:
            return redirection

        render_values = self._get_shop_payment_values(order, **post)
        render_values['only_services'] = order and order.only_services or False

        render_values['product'] = request.env['product.product'].sudo().browse(3),

        if render_values['errors']:
            render_values.pop('acquirers', '')
            render_values.pop('tokens', '')

        return request.render("website_sale.payment", render_values)
    """


    @http.route(['/shop/product/<model("product.template"):product>'], type='http', auth="public", website=True)
    def product(self, product, category='', search='', **kwargs):
        if not product.can_access_from_current_website():
            raise NotFound()
            
        if product.id in (1,2,3):
            """This route is called when adding a product to cart (no options)."""
            sale_order = request.website.sale_get_order(force_create=True)
            if sale_order.state != 'draft':
                request.session['sale_order_id'] = None
                sale_order = request.website.sale_get_order(force_create=True)

            product_custom_attribute_values = None
            if kwargs.get('product_custom_attribute_values'):
                product_custom_attribute_values = json.loads(kw.get('product_custom_attribute_values'))

            no_variant_attribute_values = None
            if kwargs.get('no_variant_attribute_values'):
                no_variant_attribute_values = json.loads(kw.get('no_variant_attribute_values'))
            sale_order.website_order_line.unlink()

            #for line in sale_order.get_order_lines
            sale_order._cart_update(
                product_id=int(product.id),
                add_qty=1,
                set_qty=0,
                product_custom_attribute_values=product_custom_attribute_values,
                no_variant_attribute_values=no_variant_attribute_values
            )
            #request.website.sale_reset()
            return request.redirect("/shop/address")
            #return request.redirect("/shop/checkout?express=1&product_id=" + str(product.id))
        return request.redirect("/web/login")



    def sitemap_shop(env, rule, qs):
        if not qs or qs.lower() in '/shop':
            yield {'loc': '/shop'}

        Category = env['product.public.category']
        dom = sitemap_qs2dom(qs, '/shop/category', Category._rec_name)
        dom += env['website'].get_current_website().website_domain()
        for cat in Category.search(dom):
            loc = '/shop/category/%s' % slug(cat)
            if not qs or qs.lower() in loc:
                yield {'loc': loc}


    """
    @http.route([
        '''/shop''',
        '''/shop/page/<int:page>''',
        '''/shop/category/<model("product.public.category"):category>''',
        '''/shop/category/<model("product.public.category"):category>/page/<int:page>'''
    ], type='http', auth="public", website=True, sitemap=sitemap_shop)
    def shop(self, page=0, category=None, search='', ppg=False, **post):
        # quitando acceso y funcionalidad a /shop*
        return request.redirect(request.httprequest.referrer or '/web/login')
    """

    @http.route(['/shop/confirmation'], type='http', auth="public", website=True, sitemap=False)
    def payment_confirmation(self, **post):
        """ End of checkout process controller. Confirmation is basically seing
        the status of a sale.order. State at this point :
         - should not have any context / session info: clean them
         - take a sale.order id, because we request a sale.order and are not
           session dependant anymore
        """
        _logger.error('3********************************\n+++++++++++++++++++++++++++++++++++++')
        _logger.error('order')
        sale_order_id = request.session.get('sale_last_order_id')
        if sale_order_id:
            order = request.env['sale.order'].sudo().browse(sale_order_id)
            if order.action_confirm():
                return request.render("website_sale.confirmation", {'order': order})
        else:
            return request.redirect('/shop')





    @http.route('/shop/payment/token', type='http', auth='public', website=True, sitemap=False)
    def payment_token(self, pm_id=None, **kwargs):
        """ Method that handles payment using saved tokens
        :param int pm_id: id of the payment.token that we want to use to pay.
        """
        order = request.website.sale_get_order()
        # do not crash if the user has already paid and try to pay again
        if not order:
            return request.redirect('/shop/?error=no_order')

        assert order.partner_id.id != request.website.partner_id.id

        try:
            pm_id = int(pm_id)
        except ValueError:
            return request.redirect('/shop/?error=invalid_token_id')

        # We retrieve the token the user want to use to pay
        if not request.env['payment.token'].sudo().search_count([('id', '=', pm_id)]):
            return request.redirect('/shop/?error=token_not_found')

        # Create transaction
        vals = {'payment_token_id': pm_id, 'return_url': '/shop/payment/validate'}

        tx = order._create_payment_transaction(vals)
        PaymentProcessing.add_payment_transaction(tx)
        return request.redirect('/payment/process')






class SalePortalExtended(CustomerPortal):



    # note dbo: website_sale code
    @http.route(['/my/orders/<int:order_id>/transaction/'], type='json', auth="public", website=True)
    def payment_transaction_token(self, acquirer_id, order_id, save_token=False, access_token=None, **kwargs):
        """ Json method that creates a payment.transaction, used to create a
        transaction when the user clicks on 'pay now' button. After having
        created the transaction, the event continues and the user is redirected
        to the acquirer website.
        :param int acquirer_id: id of a payment.acquirer record. If not set the
                                user is redirected to the checkout page
        """
        _logger.error('*****************************2222oeeeeeeeeeeeeeeeeeeeeeeeeeeeee ++++++++++++++++++++++++++++++++++')
        _logger.error('order_sudo.state')
        # Ensure a payment acquirer is selected
        if not acquirer_id:
            return False

        try:
            acquirer_id = int(acquirer_id)
        except:
            return False

        order = request.env['sale.order'].sudo().browse(order_id)
        if not order or not order.order_line or not order.has_to_be_paid():
            return False

        # Create transaction
        vals = {
            'acquirer_id': acquirer_id,
            'type': order._get_payment_type(save_token),
            'return_url': order.get_portal_url(),
        }

        transaction = order._create_payment_transaction(vals)
        PaymentProcessing.add_payment_transaction(transaction)
        order = request.website.sale_get_order()

        return transaction.render_sale_button(
            order,
            submit_txt=_('Pay & Confirm'),
            render_values={
                'type': order._get_payment_type(save_token),
                'alias_usage': _('If we store your payment information on our server, subscription payments will be made automatically.'),
            }
        )



    @http.route(['/my/orders/<int:order_id>/accept'], type='json', auth="public", website=True)
    def portal_quote_accept(self, order_id, access_token=None, name=None, signature=None):
        time.sleep(4)
        _logger.error('*****************************oeeeeeeeeeeeeeeeeeeeeeeeeeeeee ++++++++++++++++++++++++++++++++++')
        _logger.error('order_sudo.state')
        # get from query string if not on json param
        access_token = access_token or request.httprequest.args.get('access_token')
        try:
            order_sudo = self._document_check_access('sale.order', order_id, access_token=access_token)
        except (AccessError, MissingError):
            return {'error': _('Invalid order.')}

        if not order_sudo.has_to_be_signed():
            return {'error': _('The order is not in a state requiring customer signature.')}
        if not signature:
            return {'error': _('Signature is missing.')}

        try:
            order_sudo.write({
                'signed_by': name,
                'signed_on': fields.Datetime.now(),
                'signature': signature,
            })
            request.env.cr.commit()
        except (TypeError, binascii.Error) as e:
            return {'error': _('Invalid signature data.')}

        if not order_sudo.has_to_be_paid():
            order_sudo.action_confirm()
            order_sudo._send_order_confirmation_mail()

        pdf = request.env.ref('sale.action_report_saleorder').sudo().render_qweb_pdf([order_sudo.id])[0]

        _message_post_helper(
            'sale.order', order_sudo.id, _('Order signed by %s') % (name,),
            attachments=[('%s.pdf' % order_sudo.name, pdf)],
            **({'token': access_token} if access_token else {}))

        query_string = '&message=sign_ok'
        if order_sudo.has_to_be_paid(True):
            query_string += '#allow_payment=yes'




        return {
            'force_refresh': True,
            'redirect_url': order_sudo.get_portal_url(query_string=query_string),
        }


class WebsitePaymentExtended(PaymentProcessing):



    @http.route(['/payment/process'], type="http", auth="public", website=True, sitemap=False)
    def payment_status_page(self, **kwargs):
        time.sleep(4)
        # When the customer is redirect to this website page,
        # we retrieve the payment transaction list from his session
        tx_ids_list = self.get_payment_transaction_ids()
        payment_transaction_ids = request.env['payment.transaction'].sudo().browse(tx_ids_list).exists()
        order = request.website.sale_get_order()
        render_ctx = {
            'payment_tx_ids': payment_transaction_ids.ids,
            'message': 'sign_ok',
            'sale_order': order.id,
        }
        order = request.website.sale_get_order()
        url = "/my/order/beneficiaries/" + str(order.id)

        order.action_confirm()
        return request.redirect(url)
        #return request.render("payment.payment_process_page", render_ctx)
        #return request.render("beneficiaries_process_page", render_ctx)



class OdooWebsiteSearchCity(http.Controller):

    @http.route(['/search/suggestion_city'],  methods=['GET'], type='http', auth="public", website=True)
    def search_suggestion(self, city_id=None, **post):
        time.sleep(4)
        cities = []
        complete_cities_with_zip = request.env['res.city.zip'].sudo().search([])
        prueba = request.env['res.country.state'].sudo().search([('country_id', '=', 49),])
        for states in prueba:
            _logger.info(states.name)
            cities.append({
                'state': states.name,
                'country_id': states.country_id
            })

        data = {}
        data['status'] = True,
        data['error'] = None,
        data['data'] = {'cities': cities}
        return json.dumps(data)
