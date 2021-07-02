# -*- coding: utf-8 -*-
import logging
import datetime
import csv
import base64
from odoo import fields, models, tools, api,_
from datetime import date, timedelta
from odoo.osv import expression
from odoo.tools import date_utils
from dateutil.relativedelta import relativedelta

_logger = logging.getLogger(__name__)

    
class CollectionsReportLine(models.Model):
    _name = 'report.collections'
    _auto = False
    _description = 'This is the lines in the collections report'
    
    
#     Número de grupo/póliza: Va el número de póliza expedido por PALIG para ese sponsor o producto, según aplique.
#     Certificado: Consecutivo único del certificado. Va entre los rangos que aparecen en el archivo.
#     Primer nombre, segundo nombre, apellidos y número de cédula no creo que haya necesidad de explicarlos (Tampoco los de arriba,        pero bueno).
#     Tipo de transacción: Siempre va a ir R de Recaudo.
#     Código de clase: El atributo Clase del producto.
#     Fecha de cambio: Es la fecha del recaudo. Ten cuidado con el formato de fecha usado por PALIG.
#     Valor recaudo no hay necesidad de explicarlo.
#     Número de cuotas: Es el número de cuotas recaudadas con el pago. Debido a la naturaleza del negocio, el cliente siempre va a        pagar 1 o 2 cuotas en el recaudo, no más.
#     Medio de pago es otro que no tiene necesidad de ser explicado, creo.
#     Número de cuotas plan: es el número de cuotas para pagar su suscripción. Es decir, 12 si es de pago mensual, 4 si es de pago    trimestral, 2 si es de pago semestral y 1 si es de pago anual.
#     Total de cuotas: La suma de todas las cuotas recaudadas hasta el momento. Por ejemplo, 3 se interpreta como que el cliente ha    pagado 3 cuotas.
#     Número de cuotas en mora: Es el número de cuotas que ha dejado de pagar el cliente hasta la fecha. Se reportará 1, cuando el    cliente que deba pagar dos cuotas para no entrar en cancelación, solamente abone una cuota y deje la cuota en mora. 
    
    
    policy_number = fields.Char('Número de Poliza', readonly=True)
    certificate_number = fields.Char('Número de Certificado', readonly=True)
    firstname = fields.Char('Primer Nombre', readonly=True)
    othernames = fields.Char('Segundo Nombre', readonly=True)
    lastname = fields.Char('Apellidos', readonly=True)
    identification_document = fields.Char('Número de Identificación', readonly=True)
    transaction_type = fields.Char('Tipo de transacción', readonly=True)
    clase = fields.Char('Clase', readonly=True)    
    change_date = fields.Char('Fecha de cambio', readonly=True)    
    collected_value = fields.Integer('Valor recaudo', readonly=True)    
    number_of_installments = fields.Char('Cuotas recaudo', readonly=True)    
    payment_method = fields.Selection([
        ("Credit Card", "Tarjeta de Crédito"), 
        ("Cash", "Efectivo"), 
        ("PSE", "PSE"),
        ("Product Without Price", "Beneficio "),
    ])
    number_of_plan_installments = fields.Integer('Cuotas plan', readonly=True)    
    total_installments = fields.Char('Pagadas a la fecha', readonly=True)    
    number_of_installments_arrears = fields.Char('#Cuotas en mora', readonly=True)
    
    def init(self):
        tools.drop_view_if_exists(self._cr, 'report_collections')
        query = """
        CREATE or REPLACE VIEW report_collections AS(        
        select 
        row_number() OVER (ORDER BY sub.id) as id,
        sub.policy_number as certificate_number,
        sub.number as policy_number,
        p.firstname,
        p.othernames,
        p.lastname || ' ' || p.lastname2 as lastname,
        p.identification_document,
        'R'::text as transaction_type,
        tmpl.product_class as clase,
        sub.date_start as change_date,
        sub.recurring_total as collected_value,        
        '1'::text as number_of_installments,        
        sorder.payment_method_type as payment_method,
        subtmpl.recurring_rule_count as number_of_plan_installments,
        '1'::text as total_installments,
        ''::text as number_of_installments_arrears        
        
        from sale_subscription sub
        left join res_partner p on p.subscription_id = sub.id
        left join res_partner_document_type rpdt on rpdt.id = p.document_type_id
        left join res_city_zip rcz on rcz.id = p.zip_id
        left join res_city city on rcz.city_id = city.id
        left join sale_subscription_line line on line.analytic_account_id = sub.id
        left join product_product pro on pro.id = line.product_id
        left join product_template tmpl on tmpl.id = pro.product_tmpl_id
        left join product_category cat on cat.id = tmpl.categ_id
        left join ir_sequence seq on seq.id = cat.sequence_id
        left join sale_subscription_template subtmpl on subtmpl.id = sub.template_id
        left join sale_order sorder on sorder.subscription_id = sub.id
        
        where p.buyer='t' and sorder.payment_method_type<>'Product Without Price'
        order by sub.id desc
        );
        """
        self.env.cr.execute(query)
        #(select to_char(mp.date_planned_start,'mm')) as month,
#         reporte entre dos fechas
#         where date_start BETWEEN '2021-05-20' AND '2021-05-26'

    def _cron_send_email_collection_file(self):
        data = []
        sum = 0
        current_date = date.today()
        start_date = current_date - timedelta(days=7)
        if start_date.month != current_date.month:
            start_date2 = start_date
            start_date = current_date.replace(day=1) 
            end_date2 = (start_date2.replace(day=1) + timedelta(days=32)).replace(day=1) - timedelta(days=1)   
            start_date2 = start_date2.strftime('%Y-%m-%d')
            end_date2 = end_date2.strftime('%Y-%m-%d')
        start_date = start_date.strftime('%Y-%m-%d')
        end_date = current_date - timedelta(days=1)
        if end_date.month != current_date.month:
            end_date = (end_date.replace(day=1) + timedelta(days=32)).replace(day=1) - timedelta(days=1)  
        end_date = end_date.strftime('%Y-%m-%d')

        headers = ['Número de Poliza', 'Número de Certificado', 'Primer Nombre', 'Segundo Nombre', 'Apellidos', 'Número de Identificación', 'Tipo de transacción', 'Clase', 'Fecha de cambio', 'Valor recaudo', 'Número de cuotas', 'Método de Pago', 'Número de cuotas plan', 'Total de cuotas', 'Número de cuotas en mora']
        data.append(headers)

        records =  self.env['report.collections'].search([('change_date', '>=', start_date), ('change_date', '<=', end_date)])
        nreg = len(records)
        for record in records:
            data.append([record.certificate_number, record.policy_number, record.firstname, record.othernames, record.lastname, record.identification_document, record.transaction_type, record.clase, record.change_date, record.collected_value, record.number_of_installments, record.payment_method, record.number_of_plan_installments, record.total_installments, record.number_of_installments_arrears])
            sum = sum + record.collected_value

        data.append(['Fecha inicio', start_date, 'Fecha fin', end_date, 'Numero de registros', nreg, '', '', 'Total', sum])

        if 'start_date2' in locals():            
            data2 = []
            sum2 = 0
            data2.append(headers)
            records2 =  self.env['report.collections'].search([('change_date', '>=', start_date2), ('change_date', '<=', end_date2)])
            nreg2 = len(records2)
            for record in records2:
                data2.append([record.certificate_number, record.policy_number, record.firstname, record.othernames, record.lastname, record.identification_document, record.transaction_type, record.clase, record.change_date, record.collected_value, record.number_of_installments, record.payment_method, record.number_of_plan_installments, record.total_installments, record.number_of_installments_arrears])
                sum2 = sum2 + record.collected_value

            data2.append(['Fecha inicio', start_date2, 'Fecha fin', end_date2, 'Numero de registros', nreg2, '', '', 'Total', sum2])
            
            with open('tmp/collection.csv', 'w', encoding='utf-8', newline='') as file, open('tmp/collection2.csv', 'w', encoding='utf-8', newline='') as file2:
                writer = csv.writer(file, delimiter=',')
                writer.writerows(data)
                writer2 = csv.writer(file2, delimiter=',')
                writer2.writerows(data2)           
            

            with open ('tmp/collection.csv', 'rb') as archivo, open ('tmp/collection2.csv', 'rb') as archivo2:
                encoded = base64.b64encode(archivo.read())
                encoded2 = base64.b64encode(archivo2.read())        
        
                att = self.env['ir.attachment'].sudo().create({
                    'name': 'archivo_%s_to_%s.csv'%(start_date, end_date),
                    'type': 'binary',
                    'datas': encoded,                    
                    'mimetype': 'text/csv'
                })

                att2 = self.env['ir.attachment'].sudo().create({
                    'name': 'archivo_%s_to_%s.csv'%(start_date2, end_date2),                    
                    'type': 'binary',
                    'datas': encoded2,
                    'mimetype': 'text/csv'
                })

                mail_values = {
                    'subject': 'Archivo de recaudos de %s hasta %s'%(start_date2, end_date2),
                    'body_html' : 'CSV',
                    'email_to': 'directordeproyectos@masmedicos.co',
                    'email_from': 'contacto@masmedicos.co',
                    'attachment_ids': [(6, 0 , [att.id, att2.id])]
                }
                self.env['mail.mail'].sudo().create(mail_values).send()
        else:
            with open ('tmp/collection.csv', 'w', encoding='utf-8', newline='') as file:
                writer = csv.writer(file, delimiter=',')
                writer.writerows(data)

            with open ('tmp/collection.csv', 'rb') as archivo:
                encoded = base64.b64encode(archivo.read())        
        
                att = self.env['ir.attachment'].sudo().create({
                    'name': 'archivo_%s_to_%s.csv'%(start_date, end_date),
                    'type': 'binary',
                    'datas': encoded,                    
                    'mimetype': 'text/csv'
                })

                mail_values = {
                    'subject': 'Archivo de recaudos de %s hasta %s'%(start_date, end_date),
                    'body_html' : 'CSV',
                    'email_to': 'directordeproyectos@masmedicos.co',
                    'email_from': 'contacto@masmedicos.co',
                    'attachment_ids': [(6, 0 , [att.id])]
                }
                self.env['mail.mail'].sudo().create(mail_values).send()

