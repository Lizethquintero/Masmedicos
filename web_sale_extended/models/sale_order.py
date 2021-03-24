# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import time
import logging

_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    logo = fields.Binary(related="company_id.logo")
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
    payulatam_order_id = fields.Char('ID de Orden de PayU')
    payulatam_transaction_id = fields.Char('ID de Transacción de PayU')
    payulatam_state = fields.Char('Estado Transacción de PayU')
    payulatam_credit_card_token = fields.Char('Token Para Tarjetas de Crédito')
    payulatam_credit_card_masked = fields.Char('Mascara del Número de Tarjeta')
    payulatam_credit_card_identification = fields.Char('Identificación')
    payulatam_credit_card_method = fields.Char('Metodo de Pago')
    state =  fields.Selection(selection_add=[('payu_pending', 'PAYU ESPERANDO APROBACIÓN')])
    main_product_id = fields.Many2one('product.product', string="Plan Elegido", compute="_compute_main_product_id", store=True)
    
    
    def action_payu_confirm(self):
        if self._get_forbidden_state_confirm() & set(self.mapped('state')):
            raise UserError(_(
                'It is not allowed to confirm an order in the following states: %s'
            ) % (', '.join(self._get_forbidden_state_confirm())))

        for order in self.filtered(lambda order: order.partner_id not in order.message_partner_ids):
            order.message_subscribe([order.partner_id.id])
        self.write({
            'state': 'payu_pending',
            'date_order': fields.Datetime.now()
        })

        # Context key 'default_name' is sometimes propagated up to here.
        # We don't need it and it creates issues in the creation of linked records.
        context = self._context.copy()
        context.pop('default_name', None)

        #self.with_context(context)._action_confirm()
        #if self.env.user.has_group('sale.group_auto_done_setting'):
        #    self.action_done()
        return True
    
    @api.depends('order_line')
    def _compute_main_product_id(self):
        for line in self.order_line:
            if line.product_id.is_product_landpage:
                self.main_product_id = line.product_id
            
            

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
                _logger.error('***************************** CONSULTA EN TUS DATOS ++++++++++++++++++++++++++++++++++')
                approval = self.env['api.tusdatos'].personal_data_approval(process_id)
                if approval[0]:
                    _logger.error('***************************** LLEGA POSITIVO LA VERIFICACION EN TUS DATOS ++++++++++++++++++++++++++++++++++')
                    _logger.error(approval[0])
                    sale_id.write({'tusdatos_approved': approval})
                    if '-' in process_id:
                        sale_id.write({'tusdatos_request_id': approval[1]['id']})
                        body_message = """
                            <b><span style='color:blue;'>TusDatos - Solicitud de Verificación</span></b><br/>
                            <b>No. Solicitud:</b> %s<br/>
                        """ % (
                            tusdatos_validation['process_id'],
                        )
                        order.message_post(body=body_message, type="comment")
                        
                        
                  
                else:
                    if approval[1] and 'estado' in approval[1]:
                        if approval[1]['estado'] in ('error, tarea no valida'):
                            message = """Respuesta Error en Tusdatos.co: Esta respuesta se puede dar por que transcurrieron 4 horas o más 
                                        entre la consulta en tusdatos al momento de la compra y la verificación de Odoo en tus datos para 
                                        ver si la respuesta en positiva o negativa """
                            sale_id.write({'tusdatos_request_expired' : True,})
                            sale_id.message_post(body=message)
                    else:
                        message = """Respuesta Negativa en Tusdatos.co: Esta respuesta se da por que el documento del comprador se encuentra reportado
                        en las lista Onu o OFAC"""
                        sale_id.write({'tusdatos_request_expired' : True,})
                        sale_id.message_post(body=message)
                        """
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
                        """
            """Aseguramos que las transacciones ocurren cada 5 segundos"""
            time.sleep(6)
                    

                    