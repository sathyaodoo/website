/** @odoo-module */
/**
 * Hide selected options from the form view (Create / Delete / Archive)
 */
import { FormController } from "@web/views/form/form_controller";
import { patch } from "@web/core/utils/patch";
import { useService } from "@web/core/utils/hooks";

const { onWillStart } = owl;

patch(FormController.prototype, {
    setup() {
        super.setup(...arguments);
        this.orm = useService("orm");

        onWillStart(async () => {
            const restrictions = await this.orm.call("access.right", "hide_buttons", []);
            for (const r of restrictions) {
                if (this.props.resModel !== r.model) continue;

                if (r.is_create_or_update) {
                    this.canCreate = false;
                    // some views rely on activeActions as well
                    if (this.archInfo?.activeActions) {
                        this.archInfo.activeActions.create = false;
                        this.archInfo.activeActions.edit = false;
                    }
                }
                if (r.is_delete && this.archInfo?.activeActions) {
                    this.archInfo.activeActions.delete = false;
                }
                if (r.is_archive && this.archInfo?.activeActions) {
                    this.archInfo.activeActions.archive = false;
                    this.archInfo.activeActions.unarchive = false;
                }
            }
        });
    },
});
