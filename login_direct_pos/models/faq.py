from odoo import fields, models


class FaqModel(models.Model):
    _name = "faq.model"
    _description = "Frequently Asked Questions"

    name = fields.Char(string="Title", required=True)
    faq_line_ids = fields.One2many(
        'faqline.model',
        'faq_id',
        string="FAQ Lines"
    )
    active = fields.Boolean(default=True)


class FAQLine(models.Model):
    _name = "faqline.model"
    _description = "FAQ Line"

    faq_id = fields.Many2one(
        'faq.model',
        string="FAQ",
        ondelete="cascade"
    )
    question = fields.Char(string="Question", required=True)
    answer = fields.Html(string="Answer", required=True)
