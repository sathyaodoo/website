from odoo import http
from odoo.http import request

class WebsiteNews(http.Controller):

    @http.route('/news', type='http', auth='public', website=True)
    def news_page(self, **kwargs):

        # Get 4 latest blog posts
        posts = request.env['blog.post'].sudo().search(
            [('website_published', '=', True)],
            order='post_date desc',
            limit=4
        )

        return request.render('hmg_website_about.news_page_template', {
            'posts': posts
        })