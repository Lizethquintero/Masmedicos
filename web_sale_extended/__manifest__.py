# -*- coding: utf-8 -*-
{
    'name': "web_sale_extended",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'website_sale', 'portal', 'product', 'sale', 'sale_subscription', 'mail'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
        'views/web_sale_shop_address.xml',
        'views/payulatam_payment_process.xml',
        'views/product_view.xml',
        'views/res_company_view.xml',
        'views/res_partner_view.xml',
        'views/mail_template_view.xml',
        'views/account.xml',
        'views/beneficiary.xml',
        'views/beneficiary_detail.xml',
        'views/sale_order_view.xml',
        'views/sale_subscription_view.xml',
        'views/ir_sequence_view.xml',
        #'reports/sale_order_report.xml',
        #'reports/res_partner_report.xml',
        'data/shop_address.xml',
        'data/tus_datos_bot.xml',
        'data/beneficiary_confirm_template.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
