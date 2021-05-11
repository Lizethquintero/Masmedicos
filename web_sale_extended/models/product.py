# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

import logging
_logger = logging.getLogger(__name__)


class ProductCategory(models.Model):
    _inherit = 'product.category'

    sequence_id = fields.Many2one('ir.sequence','Secuencia del Patrocinador')
    
    
class ProductProduct(models.Model):
    _inherit = 'product.product'
    
    image_variant_200 = fields.Image("Variant Image 200", related="image_variant_1920", max_width=200, max_height=200, store=True)
    image_200 = fields.Image("Image 200", compute='_compute_image_200')    
    
    def _compute_image_200(self):
        """Get the image from the template if no image is set on the variant."""
        for record in self:
            record.image_200 = record.image_variant_200 or record.product_tmpl_id.image_200
    

class ProductTemplate(models.Model):
    _inherit = 'product.template'
    
    is_product_landpage = fields.Boolean('Producto Publicado en Landpage')
    product_class = fields.Char('Clase del producto')
    
    sequence_id = fields.Many2one('ir.sequence','Secuencia del Producto')
    
    product_landpage_url = fields.Char('URL para Landpage')
    
    
#     logo_website_pdf  = fields.Binary(string="Image del Plan para el documento PDF", readonly=False)
#     logo_header_website_sponsor  = fields.Binary(string="Image del Plan del Patrocinador en el encabezado", readonly=False)
#     logo_body_website_sponsor  = fields.Binary(string="Image del Patrocinador en el cuerpo del documento", readonly=False)
#     beneficiaries_number = fields.Integer(string="Número Máximo de Beneficiarios")    
#     sponsor_payment_url = fields.Char('URL de la Plataforma de Pagos')
    
    
    