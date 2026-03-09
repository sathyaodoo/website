import binascii

from odoo import fields, http, SUPERUSER_ID, _
from odoo.exceptions import AccessError, MissingError, ValidationError
from odoo.fields import Command
from odoo.http import request

from odoo.addons.payment.controllers import portal as payment_portal
from odoo.addons.payment import utils as payment_utils
from odoo.addons.portal.controllers.mail import _message_post_helper
from odoo.addons.portal.controllers import portal
from odoo.addons.portal.controllers.portal import pager as portal_pager
from odoo.addons.sale.controllers.portal import CustomerPortal


class CustomerPortal(CustomerPortal):

    @http.route(['/my/orders/<int:order_id>/accept'], type='jsonrpc', auth="public", website=True)
    def portal_quote_accept(self, order_id, access_token=None, name=None, signature=None):
        # get from query string if not on json param
        access_token = access_token or request.httprequest.args.get('access_token')
        try:
            order_sudo = self._document_check_access('sale.order', order_id, access_token=access_token)
        except (AccessError, MissingError):
            return {'error': _('Invalid order.')}

        if not order_sudo._has_to_be_signed():
            return {'error': _('The order is not in a state requiring customer signature.')}
        if not signature:
            return {'error': _('Signature is missing.')}

        try:
            order_sudo.write({
                'signed_by': name,
                'signed_on': fields.Datetime.now(),
                'signature': signature,
                'client_update': 'accepted',
            })
            # flush now to make signature data available to PDF render request
            request.env.cr.flush()
        except (TypeError, binascii.Error) as e:
            return {'error': _('Invalid signature data.')}

        if not order_sudo._has_to_be_paid():
            order_sudo._validate_order()

        pdf = request.env['ir.actions.report'].sudo()._render_qweb_pdf('sale.action_report_saleorder', [order_sudo.id])[
            0]

        order_sudo.message_post(
            attachments=[('%s.pdf' % order_sudo.name, pdf)],
            author_id=(
                order_sudo.partner_id.id
                if request.env.user._is_public()
                else request.env.user.partner_id.id
            ),
            body=_('Order signed by %s', name),
            message_type='comment',
            subtype_xmlid='mail.mt_comment',
        )

        query_string = '&message=sign_ok'
        if order_sudo._has_to_be_paid(True):
            query_string += '&allow_payment=yes'
        return {
            'force_refresh': True,
            'redirect_url': order_sudo.get_portal_url(query_string=query_string),
        }

    @http.route(['/my/orders/<int:order_id>/decline'], type='http', auth="public", methods=['POST'], website=True)
    def portal_quote_decline(self, order_id, access_token=None, decline_message=None, **kwargs):
        try:
            order_sudo = self._document_check_access('sale.order', order_id, access_token=access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')

        if order_sudo._has_to_be_signed() and decline_message:

            order_sudo.write({
                'client_update': 'declined',
                'decline_reason': str(decline_message),
            })
            # request.env.cr.commit()

            order_sudo._action_cancel()
            # The currency is manually cached while in a sudoed environment to prevent an
            # AccessError. The state of the Sales Order is a dependency of
            # `untaxed_amount_to_invoice`, which is a monetary field. They require the currency to
            # ensure the values are saved in the correct format. However, the currency cannot be
            # read directly during the flush due to access rights, necessitating manual caching.
            order_sudo.order_line.currency_id

            order_sudo.message_post(
                author_id=(
                    order_sudo.partner_id.id
                    if request.env.user._is_public()
                    else request.env.user.partner_id.id
                ),
                body=decline_message,
                message_type='comment',
                subtype_xmlid='mail.mt_comment',
            )
            redirect_url = order_sudo.get_portal_url()
        else:
            redirect_url = order_sudo.get_portal_url(query_string="&message=cant_reject")

        return request.redirect(redirect_url)
