# -*- coding: utf-8 -*-
import logging
from odoo import fields, models, tools, api,_
from datetime import datetime
from odoo.osv import expression
from odoo.tools import date_utils

_logger = logging.getLogger(__name__)

    
class SftpReportLine(models.Model):
    _name = 'report.sftp'
    _auto = False
    _description = 'This is the lines in the sftp report'
    
    #name = fields.Char('Subscription ID',readonly=True)
    policy_number = fields.Char('Número de Poliza',readonly=True)
    certificate_number = fields.Char('Número de Certificado',readonly=True)
    firstname = fields.Char('Primer Nombre',readonly=True)
    othernames = fields.Char('Segundo Nombre',readonly=True)
    lastname = fields.Char('Apellidos',readonly=True)
    #lastname2 = fields.Char('Segundo Apellido',readonly=True)
    birthdate_date = fields.Date('Fecha de Nacimiento',readonly=True)
    date_start = fields.Date('Fecha de Inicio',readonly=True)
    gender = fields.Char('Sexo',readonly=True)
    identification_document = fields.Char('Número de Identificación',readonly=True)
    default_code = fields.Char('Código Producto',readonly=True)
    recurring_interval = fields.Char('Subscripción',readonly=True)
    sponsor_name = fields.Char('Tomador',readonly=True)
    sponsor_nit = fields.Char('Nit del Tomador',readonly=True)
    sponsor_payment_url = fields.Char('Pasarela de Pagos',readonly=True)
    country = fields.Char('País',readonly=True)
    email = fields.Char('Email',readonly=True)
    
    phone = fields.Char('Teléfono Fijo',readonly=True)
    mobile = fields.Char('Teléfono',readonly=True)
    street = fields.Char('Dirección',readonly=True)
    street2 = fields.Char('Dirección2',readonly=True)
    state_id = fields.Char('Departamento',readonly=True)
    city_name = fields.Char('Ciudad',readonly=True)
    partner_zip_code = fields.Char('Ciudad',readonly=True)
    ocupation = fields.Char('Ocupación',readonly=True)
    localization = fields.Char('Lozalización',readonly=True)
    salary = fields.Char('Lozalización',readonly=True)
    salary_mode = fields.Char('Lozalización',readonly=True)
    lifevolume = fields.Char('Lifevolume',readonly=True)
    addvolume = fields.Char('addvolume',readonly=True)
    email2 = fields.Char('Email',readonly=True)
    email_state = fields.Char('Email',readonly=True)
    email_city = fields.Char('Email',readonly=True)
    email_country = fields.Char('Email',readonly=True)
    zip_code = fields.Char('Email',readonly=True)
    commentaries = fields.Char('Comentarios',readonly=True)
    aniversary = fields.Char('Aniversario',readonly=True)
    first_due = fields.Char('Primer Vencimiento',readonly=True)
    change_type = fields.Char('Ocupación',readonly=True)
    second_identification = fields.Char('Segunda Indentificación',readonly=True)
    second_type_identification = fields.Char('Tipo Segunda Identificación',readonly=True)
    ocupation = fields.Char('Ocupación',readonly=True)
    reference_initial = fields.Char('Referencia Inicial',readonly=True)
    insegurability_test = fields.Char('Prueba de Asegurabilidad',readonly=True)
    subsidiary = fields.Char('Subsidiaria',readonly=True)
    
  

    
    
    def init(self):
        tools.drop_view_if_exists(self._cr, 'report_sftp')
        query = """
        CREATE or REPLACE VIEW report_sftp AS(
        
        select 
        row_number() OVER (ORDER BY sub.id) as id,
        sub.policy_number,
        seq.code as certificate_number,
        p.firstname,
        p.othernames,
        p.lastname || ' ' || p.lastname2 as lastname,
        p.birthdate_date,
        sub.date_start,
        p.gender,
        p.identification_document,
        pro.default_code,
        subtmpl.recurring_interval,
        '009'::varchar as sponsor_name,
        seq.sponsor_nit,
        seq.sponsor_payment_url,
        '79'::varchar as country,
        p.email,

        p.phone,
        p.mobile,
        p.street,
        p.street2,
        p.state_id,
        city.name as city_name,
        rcz.name as partner_zip_code,
        p.ocupation,
        ''::text as email2,
        ''::text as email_country,
        ''::text as commentaries,
        ''::text as reference_initial,
        ''::text as aniversary,
        sub.recurring_next_date as first_due,
        ''::text as second_identification,
        rpdt.name as second_type_identification,
        ''::text as insegurability_test,
        ''::text as subsidiary,
        ''::text as lifevolume,
        ''::text as addvolume,
        ''::text as email_state,
        ''::text as zip_code,
        ''::text as email_city,
        ''::text as salary_mode,
        ''::text as salary,
        'A'::text as change_type,
        ''::text as localization
        
        
        
        
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
        
        where 1=1
        );
        """
        self.env.cr.execute(query)
        #(select to_char(mp.date_planned_start,'mm')) as month,
        
        
        
        
class SftpReportBeneficiaryLine(models.Model):
    _name = 'report.beneficiary.sftp'
    _auto = False
    _description = 'This is the lines in the sftp report'
    
    #name = fields.Char('Subscription ID',readonly=True)
    policy_number = fields.Char('Número de Poliza',readonly=True)
    certificate_number = fields.Char('Número de Certificado',readonly=True)
    firstname = fields.Char('Primer Nombre',readonly=True)
    othernames = fields.Char('Segundo Nombre',readonly=True)
    lastname = fields.Char('Primer Apellido',readonly=True)
    #lastname2 = fields.Char('Segundo Apellido',readonly=True)
    birthdate_date = fields.Date('Fecha de Nacimiento',readonly=True)
    date_start = fields.Date('Fecha de Inicio',readonly=True)
    gender = fields.Char('Sexo',readonly=True)
    city_name = fields.Char('Ciudad',readonly=True)
    partner_zip_code = fields.Char('Ciudad',readonly=True)
    identification_document = fields.Char('Número de Identificación',readonly=True)
    default_code = fields.Char('Código Producto',readonly=True)
    recurring_interval = fields.Char('Subscripción',readonly=True)
    sponsor_name = fields.Char('Tomador',readonly=True)
    sponsor_nit = fields.Char('Nit del Tomador',readonly=True)
    sponsor_payment_url = fields.Char('Pasarela de Pagos',readonly=True)
    country = fields.Char('País',readonly=True)
    email = fields.Char('Email',readonly=True)
    phone = fields.Char('Teléfono Fijo',readonly=True)
    mobile = fields.Char('Teléfono',readonly=True)
    street = fields.Char('Dirección',readonly=True)
    street2 = fields.Char('Dirección2',readonly=True)
    state_id = fields.Char('Departamento',readonly=True)
    city_name = fields.Char('Ciudad',readonly=True)
    ocupation = fields.Char('Ocupación',readonly=True)
    change_date = fields.Char('Ocupación',readonly=True)
    change_type = fields.Char('Ocupación',readonly=True)
    date_end = fields.Char('Ocupación',readonly=True)
    relationship = fields.Char('Parentezco',readonly=True)
    insegurability_test = fields.Char('Prueba de Asegurabilidad',readonly=True)
    subsidiary = fields.Char('Subsidiaria',readonly=True)
    
    
    def init(self):
        tools.drop_view_if_exists(self._cr, 'report_sftp')
        query = """
        CREATE or REPLACE VIEW report_beneficiary_sftp AS(
        
        select 
        row_number() OVER (ORDER BY sub.id) as id,
        sub.policy_number,
        seq.code as certificate_number,
        p.firstname,
        p.othernames,
        p.lastname || ' ' || p.lastname2 as lastname,
        p.birthdate_date,
        sub.date_start,
        p.gender,
        p.identification_document,
        pro.default_code,
        subtmpl.recurring_interval,
        '009'::varchar as sponsor_name,
        seq.sponsor_nit,
        seq.sponsor_payment_url,
        '79'::varchar as country,
        p.email,
        p.phone,
        p.mobile,
        p.street,
        p.street2,
        p.state_id,
        city.name as city_name,
        rcz.name as partner_zip_code,
        p.ocupation,
        p.relationship,
        ''::text as email2,
        ''::text as email_country,
        ''::text as commentaries,
        ''::text as reference_initial,
        ''::text as aniversary,
        sub.recurring_next_date as first_due,
        ''::text as second_identification,
        rpdt.name as second_type_identification,
        ''::text as insegurability_test,
        ''::text as subsidiary,
        ''::text as lifevolume,
        ''::text as addvolume,
        ''::text as email_state,
        ''::text as email_city,
        ''::text as zip_code,
        ''::text as salary_mode,
        ''::text as salary,
        ''::text as localization,
        ''::text as change_date,
        'A'::text as change_type,
        ''::text as date_end
        
        
        
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
        
        where 1=1
        );
        """
        self.env.cr.execute(query)
        #(select to_char(mp.date_planned_start,'mm')) as month,