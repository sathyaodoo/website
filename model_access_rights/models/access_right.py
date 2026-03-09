# -*- coding: utf-8 -*-
"""This model is used to detect, which all options want to hide from the
    specified group and model"""
#############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2024-TODAY Cybrosys Technologies(<https://www.cybrosys.com>)
#    Author: Cybrosys Techno Solutions(<https://www.cybrosys.com>)
#
#    You can modify it under the terms of the GNU LESSER
#    GENERAL PUBLIC LICENSE (LGPL v3), Version 3.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU LESSER GENERAL PUBLIC LICENSE (LGPL v3) for more details.
#
#    You should have received a copy of the GNU LESSER GENERAL PUBLIC LICENSE
#    (LGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
#############################################################################
from odoo import api, fields, models


class ModelAccessRights(models.Model):
    """This class is used to detect, which all options want to hide from the
    specified group and model"""
    _name = 'access.right'
    _inherit = 'mail.thread'
    _description = 'Manage Modules Access Control'
    _rec_name = 'model_id'

    model_id = fields.Many2one('ir.model', ondelete='cascade',
                               required=True,
                               help="select the model")
    groups_id = fields.Many2one('res.groups',
                                help="select the group")
    is_delete = fields.Boolean(string="Delete", help="hide the delete option")
    is_export = fields.Boolean(string="Export",
                               help="hide the 'Export All'"
                                    " option from list view")
    is_create_or_update = fields.Boolean(string="Create/Update",
                                         help="hide the create option from list"
                                              " as well as form view")
    is_archive = fields.Boolean(string="Archive/UnArchive",
                                help="hide the archive option")
    restriction_type = fields.Selection([
        ('user', 'User Wise'),
        ('group', 'Group Wise')
    ], 'Restriction Type',required=True,default="group")
    user_id = fields.Many2one('res.users',
                                help="select the user")

    @api.model
    def hide_buttons(self):
        """Return access-right restrictions already filtered for the current user.

        The JS side should not have to resolve group external IDs. We aggregate all
        rules (group-wise + user-wise) that apply to the current user, per model.
        """
        user = self.env.user
        rules = self.sudo().search([])

        # Aggregate by technical model name (ir.model.model)
        by_model = {}
        for rule in rules:
            # Skip rules that do not apply to current user
            applies = False
            if rule.restriction_type == "user" and rule.user_id and rule.user_id.id == user.id:
                applies = True
            elif rule.restriction_type == "group" and rule.groups_id and rule.groups_id in user.group_ids.ids:
                applies = True

            if not applies:
                continue

            model_name = rule.model_id.model
            agg = by_model.setdefault(model_name, {
                "model": model_name,
                "is_delete": False,
                "is_export": False,
                "is_create_or_update": False,
                "is_archive": False,
            })
            agg["is_delete"] = agg["is_delete"] or bool(rule.is_delete)
            agg["is_export"] = agg["is_export"] or bool(rule.is_export)
            agg["is_create_or_update"] = agg["is_create_or_update"] or bool(rule.is_create_or_update)
            agg["is_archive"] = agg["is_archive"] or bool(rule.is_archive)

        return list(by_model.values())
