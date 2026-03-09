/** @odoo-module **/


import { MiniCart } from "@login_direct_pos/js/components/MiniCart/minicart";
import { _t } from '@web/core/l10n/translation';

import publicWidget from "@web/legacy/js/public/public_widget";
console.log('website_sale.js loaded')
export const AlanMiniCart = publicWidget.Widget.extend({
    selector: ".as_mini_cart",
    events:{
        'click':'_show_mini_cart',
    },
    _show_mini_cart:function(ev){
        ev.preventDefault();
        this.call('dialog', 'add', MiniCart)
    },
});
publicWidget.registry.AlanMiniCart = AlanMiniCart;


export default {
   
    AlanMiniCart: publicWidget.registry.AlanMiniCart,
   
};