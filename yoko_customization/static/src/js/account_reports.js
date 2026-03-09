odoo.define('yoko_custom.account_report', function (require) {

    var core = require('web.core');
    var _t = core._t;

    accountReportsWidget = require('account_reports.account_report');
    var PartnerInfoM2MFilters = require('yoko_custom.m2mfilter');

    accountReportsWidget.include({
        custom_events: _.extend({}, accountReportsWidget.prototype.custom_events, {
            'value_changed': function(ev) {
                 var self = this;
                 self.report_options.partner_ids = ev.data.partner_ids;
                 self.report_options.partner_categories = ev.data.partner_categories;
                 self.report_options.analytic_accounts = ev.data.analytic_accounts;
                 self.report_options.analytic_tags = ev.data.analytic_tags;
                 self.report_options.parent_company_ids = ev.data.parent_ids;
                 self.report_options.customer_category_ids = ev.data.category_ids;
                 return self.reload().then(function () {
                     self.$searchview_buttons.find('.account_partner_filter').click();
                     self.$searchview_buttons.find('.account_analytic_filter').click();
                 });
            }
        }),

        render_searchview_buttons: function() {
            var self = this;
            self._super();
            if (this.report_options.partner_info) {
                if (!this.PartnerInfoM2MFilters) {
                    var fields = {};
                    if ('parent_company_ids' in this.report_options) {
                        fields['parent_ids'] = {
                            label: _t('Parent Company'),
                            modelName: 'res.partner',
                            value: this.report_options.parent_company_ids.map(Number),
                        };
                    }
                    if ('customer_category_ids' in this.report_options) {
                        fields['category_ids'] = {
                            label: _t('Customer Category'),
                            modelName: 'customer.category',
                            value: this.report_options.customer_category_ids.map(Number),
                        };
                    }
                    if (!_.isEmpty(fields)) {
                        this.PartnerInfoM2MFilters = new PartnerInfoM2MFilters(this, fields);
                        this.PartnerInfoM2MFilters.appendTo(this.$searchview_buttons.find('.js_account_partner_info_m2m'));
                    }
                } else {
                    this.$searchview_buttons.find('.js_account_partner_info_m2m').append(this.PartnerInfoM2MFilters.$el);
                }
            }
        },
    });

    return accountReportsWidget;
})