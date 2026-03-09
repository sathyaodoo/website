from odoo import http
from odoo.http import request
import json

class WebsiteAbout(http.Controller):

    @http.route('/about-us', type='http', auth="public", website=True)
    def about_page(self, **kwargs):
        return request.render('hmg_website_about.website_about')
    
class WebsiteSafety(http.Controller):
    @http.route('/safety-content', type='http', auth="public", website=True)
    def safety_page(self, **kwargs):
        return request.render('hmg_website_about.website_safety')
    
class WebsiteOriginalEquipment(http.Controller):
    @http.route('/original-equipment', type='http', auth="public", website=True)
    def original_equipment_page(self, **kwargs):
        return request.render('hmg_website_about.website_original_equipment')
    
class WebsiteShopProducts(http.Controller):
    @http.route('/shop-products', type='http', auth="public", website=True)
    def shop_products_page(self, **kwargs):
        tires = request.env['product.template'].sudo().search([
            ('public_categ_ids.name', '=', 'Tires'),
            ('sale_ok', '=', True)
        ])
        print(tires,'>>>>>>>>>>>>>>>>>>>>>>tires')

        lubricants = request.env['product.template'].sudo().search([
            ('public_categ_ids.name', '=', 'Lubricants'),
            ('sale_ok', '=', True)
        ])

        batteries = request.env['product.template'].sudo().search([
            ('public_categ_ids.name', '=', 'Batteries'),
            ('sale_ok', '=', True)
        ])

        return request.render('hmg_website_about.website_shop_products', {
            'tires': tires,
            'lubricants': lubricants,
            'batteries': batteries,
        })
        # return request.render('hmg_website_about.website_shop_products')
    
class WebsiteVideos(http.Controller):
    @http.route('/videos', type='http', auth="public", website=True)
    def videos_page(self,**kwargs):
        return request.render('hmg_website_about.website_videos')

class DealerLocator(http.Controller):
    
    @http.route('/dealers', type='http', auth="public", website=True)
    def dealer_page(self, **kwargs):

        search = kwargs.get('search')
        

        # Sample Dealer Data
        sample_dealers = [
            { "name": "Dealer 1",
        "zip": "600001",
        "city": "Chennai",
        "state": "Tamil Nadu",
        "lat": 13.0827,
        "lng": 80.2707,
        "address": "Mount Road, Chennai",
        "phone": "+91 9876543210",
        "image": "hmg_website_about/static/dealers/deal3.png"},
            { "name": "Dealer 2",
        "zip": "400001",
        "city": "Mumbai",
        "state": "Maharashtra",
        "lat": 18.9388,
        "lng": 72.8354,
        "address": "Andheri East, Mumbai",
        "phone": "+91 9123456780",
        "image": "hmg_website_about/static/dealers/deal2.png"},
            {"name": "Dealer 3", "zip": "110001", "city": "Delhi", "state": "Delhi", "lat": 28.6139, "lng": 77.2090,
               "address": "Delhi East, Delhi",
        "phone": "+91 9123456780",
        "image": "hmg_website_about/static/dealers/deal1.png"},
        ]

        filtered = sample_dealers
        nearest_dealer = None
        nearest_distance = None
        no_dealer = False

        if search:
            search_lower = search.lower()

            filtered = [
                d for d in sample_dealers
                if search_lower in d["zip"].lower()
                or search_lower in d["city"].lower()
                or search_lower in d["state"].lower()
            ]

            if not filtered:
                no_dealer = True

               

        return request.render('hmg_website_about.dealer_template', {
            'dealers': json.dumps(filtered),
            'search': search,
            'dealers_list': filtered,
            'no_dealer': no_dealer,
           
        })


    # @http.route('/dealers', type='http', auth="public", website=True)
    # def dealer_locator(self, zip=None):
    #     domain = [('is_dealer', '=', True)]
    #     if zip:
    #         domain.append(('dealer_zip', '=', zip))

    #     dealers = request.env['res.partner'].sudo().search(domain)

    #     return request.render('dealer_locator.template', {
    #     'dealers': dealers,
    # })
    
    # @http.route('/dealers', type='http', auth="public", website=True)
    # def dealer_page(self, search=None, **kwargs):

    #     # # Hardcoded Dealer Data
    #     # sample_dealers = [
    #     #     {"name": "Dealer 1", "zip": "600001", "lat": 13.0827, "lng": 80.2707},
    #     #     {"name": "Dealer 2", "zip": "400001", "lat": 18.9388, "lng": 72.8354},
    #     #     {"name": "Dealer 3", "zip": "110001", "lat": 28.6139, "lng": 77.2090},
    #     #     {"name": "Dealer 4", "zip": "560001", "lat": 12.9716, "lng": 77.5946},
    #     #     {"name": "Dealer 5", "zip": "500001", "lat": 17.3850, "lng": 78.4867},
    #     #     {"name": "Dealer 6", "zip": "700001", "lat": 22.5726, "lng": 88.3639},
    #     #     {"name": "Dealer 7", "zip": "380001", "lat": 23.0225, "lng": 72.5714},
    #     #     {"name": "Dealer 8", "zip": "682001", "lat": 9.9312, "lng": 76.2673},
    #     #     {"name": "Dealer 9", "zip": "641001", "lat": 11.0168, "lng": 76.9558},
    #     #     {"name": "Dealer 10", "zip": "302001", "lat": 26.9124, "lng": 75.7873},
    #     #     {"name": "Dealer 11", "zip": "122001", "lat": 28.4595, "lng": 77.0266},
    #     #     {"name": "Dealer 12", "zip": "751001", "lat": 20.2961, "lng": 85.8245},
    #     # ]

    #     # # Filter by ZIP if provided
    #     # if zip:
    #     #     filtered = [d for d in sample_dealers if d["zip"] == zip]
    #     #     # print(json.dumps(filtered),'JSOOOOOOOOOOOOOOO DATA')
    #     # # else:
    #     # #     filtered = random.sample(sample_dealers, 10)
    #     # #     print(filtered,'JSOOOOOOOOOOOOOOO DATA')
        
        
    #     sample_dealers = [
    #     {"name": "Dealer 1", "zip": "600001", "city": "Chennai", "state": "Tamil Nadu", "lat": 13.0827, "lng": 80.2707},
    #     {"name": "Dealer 2", "zip": "400001", "city": "Mumbai", "state": "Maharashtra", "lat": 18.9388, "lng": 72.8354},
    #     {"name": "Dealer 3", "zip": "110001", "city": "Delhi", "state": "Delhi", "lat": 28.6139, "lng": 77.2090},
    #     ]

    #     filtered = sample_dealers

    #     if search:
    #         search_lower = search.lower()
    #         filtered = [
    #             d for d in sample_dealers
    #             if search_lower in d["zip"].lower()
    #             or search_lower in d["city"].lower()
    #             or search_lower in d["state"].lower()
    #         ]
    #     print(search,'SEARCH VALUEEEEEEEEEEEEEEEEEE')
    #     return request.render('hmg_website_about.dealer_template', {
    #         'dealers':  json.dumps(filtered),
    #         'search': search,
    #     })
    
    # def calculate_distance(lat1, lon1, lat2, lon2):
    #     R = 6371  # Radius of earth in km
    #     dLat = math.radians(lat2 - lat1)
    #     dLon = math.radians(lon2 - lon1)

    #     a = (math.sin(dLat/2) ** 2 +
    #         math.cos(math.radians(lat1)) *
    #         math.cos(math.radians(lat2)) *
    #         math.sin(dLon/2) ** 2)

    #     c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    #     return R * c

    # @http.route('/dealers', type='http', auth="public", website=True)
    # def dealer_page(self, search=None, **kwargs):

        sample_dealers = [
            {"name": "Dealer 1", "zip": "600001", "city": "Chennai", "state": "Tamil Nadu", "lat": 13.0827, "lng": 80.2707},
            {"name": "Dealer 2", "zip": "400001", "city": "Mumbai", "state": "Maharashtra", "lat": 18.9388, "lng": 72.8354},
            {"name": "Dealer 3", "zip": "110001", "city": "Delhi", "state": "Delhi", "lat": 28.6139, "lng": 77.2090},
        ]

        filtered = sample_dealers
        nearest_dealer = None
        nearest_distance = None
        no_dealer = False

        if search:
            search_lower = search.lower()

            filtered = [
                d for d in sample_dealers
                if search_lower in d["zip"].lower()
                or search_lower in d["city"].lower()
                or search_lower in d["state"].lower()
            ]
            print(filtered)
            if not filtered:
                no_dealer = True

                # Fake center point for demo (India center)
                search_lat = 20.5937
                search_lng = 78.9629

                min_distance = float("inf")

                for dealer in sample_dealers:
                    dist = request.calculate_distance(
                        search_lat, search_lng,
                        dealer["lat"], dealer["lng"]
                    )
                    if dist < min_distance:
                        min_distance = dist
                        nearest_dealer = dealer

                nearest_distance = round(min_distance, 1)

        return request.render('hmg_website_about.dealer_template', {
            'dealers': json.dumps(filtered),
            'search': search,
            'no_dealer': no_dealer,
            'nearest_dealer': nearest_dealer,
            'nearest_distance': nearest_distance,
        })


class LoyaltyPage(http.Controller):

    @http.route('/loyalty', type='http', auth="public", website=True)
    def loyalty_page(self, **kwargs):
        return request.render('hmg_website_about.loyalty_page')

class GiftShopController(http.Controller):

    @http.route('/gift-shop', type='http', auth='user', website=True)
    def gift_shop(self, **kwargs):

        products = request.env['product.template'].sudo().search([
            ('website_published', '=', True)
        ], limit=8)

        gifts = []
        for product in products:
            gifts.append({
                'id': product.id,
                'name': product.name,
                'points': 100,
                'image': f'/web/image/product.template/{product.id}/image_1920'
            })

        return request.render('hmg_website_about.gift_shop_page', {
            'gifts': gifts
        })

class DownloadCenter(http.Controller):
    @http.route('/download-center', type='http', auth="public", website=True)
    def download_center(self):
        return request.render("hmg_website_about.download_center_page")

