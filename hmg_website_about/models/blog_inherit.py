from odoo import models, fields

class BlogPost(models.Model):
    _inherit = "blog.post"

    news_image = fields.Binary("News Image", attachment=True)