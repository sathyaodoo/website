# -*- coding: utf-8 -*-
"""Runtime restrictions for create/delete/archive based on model_access_rights rules.

Important:
- Do NOT copy Odoo internals (BaseModel._create/_unlink implementation changes between versions).
- We wrap the public methods (create/write/unlink) and delegate to the original
  implementation after applying our checks.

This makes the addon far more resilient across Odoo 17 -> 19 upgrades.
"""

from odoo import api, models, _
from odoo.exceptions import UserError

from odoo.models import BaseModel


def _user_is_restricted(recordset, operation):
    """Return True if current user is restricted for `operation` on recordset model.

    operation: 'create' | 'unlink' | 'archive'
    """
    env = recordset.env
    if env.is_admin():
        return False

    model_name = recordset._name
    model_rec = env['ir.model'].sudo().search([('model', '=', model_name)], limit=1)
    if not model_rec:
        return False

    # Read only relevant rules
    rules = env['access.right'].sudo().search([('model_id', '=', model_rec.id)])
    if not rules:
        return False

    user = env.user
    for rule in rules:
        applies = False
        if rule.restriction_type == 'user' and rule.user_id and rule.user_id.id == user.id:
            applies = True
        elif rule.restriction_type == 'group' and rule.groups_id and rule.groups_id in user.groups_id:
            applies = True

        if not applies:
            continue

        if operation == 'create' and rule.is_create_or_update:
            return True
        if operation == 'unlink' and rule.is_delete:
            return True
        if operation == 'archive' and rule.is_archive:
            return True

    return False


# Keep references to the original methods
_ORIGINAL_CREATE = BaseModel.create
_ORIGINAL_WRITE = BaseModel.write
_ORIGINAL_UNLINK = BaseModel.unlink


@api.model_create_multi
def create(self, vals_list):
    if _user_is_restricted(self, 'create'):
        raise UserError(_('You are restricted from performing this operation. Please contact the administrator.'))
    return _ORIGINAL_CREATE(self, vals_list)


def write(self, vals):
    # Archive/Unarchive is typically a write on the `active` field or an archive action.
    if 'active' in vals and _user_is_restricted(self, 'archive'):
        raise UserError(_('You are restricted from performing this operation. Please contact the administrator.'))
    return _ORIGINAL_WRITE(self, vals)


def unlink(self):
    if _user_is_restricted(self, 'unlink'):
        raise UserError(_('You are restricted from performing this operation. Please contact the administrator.'))
    return _ORIGINAL_UNLINK(self)


# Monkey-patch the BaseModel methods
BaseModel.create = create
BaseModel.write = write
BaseModel.unlink = unlink
