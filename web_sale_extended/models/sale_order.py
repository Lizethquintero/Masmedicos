# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import time
import logging

_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    logo = fields.Binary(related="company_id.logo")
    # TusDatos.co
    tusdatos_request_id = fields.Char('Report id', default='')
    tusdatos_approved = fields.Boolean('Approved', default=False)
    tusdatos_email = fields.Char('Client e-mail', default='')
    tusdatos_request_expired = fields.Boolean('Request Expired')
    
    subscription_id = fields.Many2one('sale.subscription', 'Suscription ID')
    beneficiary0_id = fields.Many2one('res.partner')
    beneficiary1_id = fields.Many2one('res.partner')
    beneficiary2_id = fields.Many2one('res.partner')
    beneficiary3_id = fields.Many2one('res.partner')
    beneficiary4_id = fields.Many2one('res.partner')
    beneficiary5_id = fields.Many2one('res.partner')
    beneficiary6_id = fields.Many2one('res.partner')
    
    #payulatam_order_id = fields.Char('ID de Orden de PayU')
    #payulatam_transaction_id = fields.Char('ID de Transacción de PayU')
    #payulatam_state = fields.Char('Estado Transacción de PayU')
    
    payulatam_credit_card_token = fields.Char('Token Para Tarjetas de Crédito')
    payulatam_credit_card_masked = fields.Char('Mascara del Número de Tarjeta')
    payulatam_credit_card_identification = fields.Char('Identificación')
    payulatam_credit_card_method = fields.Char('Metodo de Pago')
    

    def tusdatos_approval(self):
        for record in self:
            approval = record.tusdatos_approved
            process_id = record.tusdatos_request_id
            # user_id = record.user_id
            if process_id and not approval:
                _logger.info(' '.join([str(approval), process_id]))
                # TusDatos API!!!!
                approval = self.env['api.tusdatos'].personal_data_approval(process_id)
                _logger.info(' '.join([str(approval)]))
                if approval[0]:
                    record.write({'tusdatos_approval': approval})
                    if '-' in process_id:
                        record.write({'tusdatos_request_id': approval[1]['id']})
                    # EMAIL!!! (subir)
                    record.action_quatition_send()
                else:
                    template = request.env.ref('web_sale_extended_template_sale_update',
                                               raise_if_not_found=False)
                    context = dict(self.env.context)
                    if template:
                        template_values = template.generate_email(record.id, fields=None)
                        template_values.update({
                            'email_to': record.tusdatos_email,
                            'auto_delete': False,
                            'partner_to': False,
                            'scheduled_date': False,
                        })

                        template.write(template_values)
                        cleaned_ctx = dict(self.env.context)
                        cleaned_ctx.pop('default_type', None)
                        template.with_context(lang=self.env.user.lang).send_mail(record.id, force_send=True, raise_exception=True)


    #@api.model
    #def create(self, vals):

    """
    def action_quotation_sent(self):
        _logger.error('*****************************ORDEN DE VENTA CREADA ++++++++++++++++++++++++++++++++++')
        _logger.error(self)
        super(SaleOrder, self).action_quotation_sent()
        self.action_confirm()
    """
    
    
    def cron_get_status_tusdatos(self):
        """Se tienen en cuenta únicamente ordenes de venta que no esten aprobadas pero que tengan un número de proceso
        de parte de tusdatos."""
        sale_ids = self.env['sale.order'].search([
            ('tusdatos_approved', '=', False),
            ('tusdatos_request_id', '!=', False),
            ('tusdatos_request_expired', '=', False)
        ])
        _logger.error('***************************** INICIANDO CRON DE CONSULTAS EN TUSDATOS ++++++++++++++++++++++++++++++++++')
        for sale_id in sale_ids:
            # verificando estado del proceso de consulta
            approval = sale_id.tusdatos_approved
            process_id = sale_id.tusdatos_request_id
            # user_id = record.user_id
            if process_id and not approval:
                _logger.info(' '.join([str(approval), process_id]))
                # TusDatos API!!!!
                _logger.error('***************************** CONSULTA EN TUS DATOS ++++++++++++++++++++++++++++++++++')
                approval = self.env['api.tusdatos'].personal_data_approval(process_id)
                
                #_logger.info(' '.join([str(approval)]))
                if approval[0]:
                    _logger.error('***************************** LLEGA POSITIVO LA VERIFICACION EN TUS DATOS ++++++++++++++++++++++++++++++++++')
                    _logger.error(approval[0])
                    sale_id.write({'tusdatos_approved': approval})
                    if '-' in process_id:
                        sale_id.write({'tusdatos_request_id': approval[1]['id']})
                    # EMAIL!!! (subir)
                    #record.action_quatition_send()
                    #template = request.env.ref('web_sale_extended_template_sale_update',
                    #                       raise_if_not_found=False)
                    #template_id = self.env['mail.template'].search([('tusdatos_confirmation_accept', '=', True)], limit=1)
                    template_id = self._find_mail_template(force_confirmation_template=True)
                    context = dict(self.env.context)
                    if template_id:
                        sale_id.with_context(force_send=True).message_post_with_template(
                            int(template_id), composition_mode='comment', email_layout_xmlid="mail.mail_notification_paynow")
                        
                        
                        
                        """
                        _logger.error('***************************** TUS DATOS CONFIRMACION ++++++++++++++++++++++++++++++++++')
                        _logger.error(template)
                        
                        
                        #template_values = template.generate_email(sale_id.id, fields=None)
                        template_values = {}
                        _logger.error('***************************** 777777777777777777777 ++++++++++++++++++++++++++++++++++')
                        _logger.error(template_values)
                        ctx = {
                            'default_model': 'sale.order',
                            'default_res_id': sale_id.id,
                            'default_use_template': bool(template.id),
                            'default_template_id': template.id,
                            'default_composition_mode': 'comment',
                            'mark_so_as_sent': True,
                            'custom_layout': "mail.mail_notification_paynow",
                            'proforma': self.env.context.get('proforma', False),
                            'force_email': True,
                            'model_description': self.with_context(lang=self.env.user.lang).type_name,
                        }
                        body = template.with_context(ctx)._render_template(template.body_html, 'sale.order', sale_id.id)
                        _logger.error(body)
                        template_values.update({
                            #'email_to': sale_id.tusdatos_email,
                            #'email_to': sale_id.partner_id.email,
                            'auto_delete': False,
                            'partner_to': sale_id.partner_id.id,
                            'scheduled_date': False,
                            'body_html': body,
                        })
                        
                        
                        if "partner_ids" in template_values:
                            template_values.pop('partner_ids')
                        template.write(template_values)
                        cleaned_ctx = dict(self.env.context)
                        cleaned_ctx.pop('default_type', None)
                        cleaned_ctx['custom_layout'] = 'mail.mail_notification_paynow'
                        cleaned_ctx['mark_so_as_sent'] = True
                        template.with_context(cleaned_ctx).send_mail(sale_id.id, force_send=True, raise_exception=True)
                        """
                else:
                    _logger.error('***************************** LLEGA NEGATIVA LA RESPUESTA DE TUSDATOS ++++++++++++++++++++++++++++++++++')
                    _logger.error(approval[1])
                    if approval[1] and 'estado' in approval[1]:
                        if approval[1]['estado'] in ('error, tarea no valida'):
                            _logger.error('***************************** RESPUESTA: error, tarea no valida ++++++++++++++++++++++++++++++++++')
                            message = """Respuesta Error en Tusdatos.co: Esta respuesta se puede dar por que transcurrieron 4 horas o más 
                                        entre la consulta en tusdatos al momento de la compra y la verificación de Odoo en tus datos para 
                                        ver si la respuesta en positiva o negativa """
                            sale_id.write({
                                'tusdatos_request_expired' : True,
                            })
                            sale_id.message_post(body=message)
                    else:
                        _logger.error('***************************** ENVIANDO CORREO DE RESPUESTA NEGATIVA  ++++++++++++++++++++++++++++++++++')
                        template = self.env['mail.template'].search([('tusdatos_confirmation_reject', '=', True)], limit=1)
                        context = dict(self.env.context)
                        if template:
                            template_values = template.generate_email(sale_id.id, fields=None)
                            template_values.update({
                                #'email_to': sale_id.tusdatos_email,
                                'email_to': sale_id.partner_id.email,
                                'auto_delete': False,
                                #'partner_to': False,
                                'scheduled_date': False,
                            })
                            template.write(template_values)
                            cleaned_ctx = dict(self.env.context)
                            cleaned_ctx.pop('default_type', None)
                            template.with_context(lang=self.env.user.lang).send_mail(sale_id.id, force_send=True, raise_exception=True)
                    """Aseguramos que las transacciones ocurren cada 5 segundos"""
                    time.sleep(6)
                    

                    