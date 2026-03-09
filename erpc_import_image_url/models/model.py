# -*- coding: utf-8 -*-
from odoo import models

class ResUsers(models.Model):
    _inherit = 'res.users'

    def _can_import_remote_urls(self):
        """ Hook to decide whether the current user is allowed to import
        images via URL. Allows administrators and users in the import URL group.
        """
        self.ensure_one()
        return self._is_admin() or self.has_group('erpc_import_image_url.group_import_image_url')