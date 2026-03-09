import time
import babel
from odoo import models, fields, api, tools, _
from datetime import datetime
import base64
from io import BytesIO
from PIL import Image

import logging

_logger = logging.getLogger(__name__)


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    signature = fields.Binary(string='Signature')

    def get_signature_image(self):
        self.ensure_one()
        if not self.signature:
            return False
        try:
            # The signature widget stores the image as PNG
            return Image.open(BytesIO(base64.b64decode(self.signature)))
        except:
            return False
