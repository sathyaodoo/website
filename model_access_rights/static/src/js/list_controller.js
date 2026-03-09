/** @odoo-module */
/**
 * Hide selected options from the list view (Create / Delete / Export / Archive)
 */
import { ListController } from "@web/views/list/list_controller";
import { patch } from "@web/core/utils/patch";
import { useService } from "@web/core/utils/hooks";

const { onWillStart } = owl;

patch(ListController.prototype, {
    setup() {
        super.setup(...arguments);
        this.orm = useService("orm");

        onWillStart(async () => {
            const restrictions = await this.orm.call("access.right", "hide_buttons", []);
            for (const r of restrictions) {
                if (this.props.resModel !== r.model) continue;

                if (r.is_create_or_update && this.activeActions) {
                    this.activeActions.create = false;
                }
                if (r.is_delete && this.activeActions) {
                    this.activeActions.delete = false;
                }
                if (r.is_archive && this.activeActions) {
                    this.activeActions.archive = false;
                    this.activeActions.unarchive = false;
                }
                // Export is controlled by the list controller capability flags.
                if (r.is_export) {
                    if ("isExportEnable" in this) {
                        this.isExportEnable = false;
                    }
                }
            }
        });
    },
});
