/** @odoo-module */
/**
 * Hide selected options from the kanban view (Create / Delete / Archive)
 */
import { KanbanController } from "@web/views/kanban/kanban_controller";
import { patch } from "@web/core/utils/patch";
import { useService } from "@web/core/utils/hooks";

const { onWillStart } = owl;

patch(KanbanController.prototype, {
    setup() {
        super.setup(...arguments);
        this.orm = useService("orm");

        onWillStart(async () => {
            const restrictions = await this.orm.call("access.right", "hide_buttons", []);
            for (const r of restrictions) {
                if (this.props.resModel !== r.model) continue;

                const actions = this.props.archInfo?.activeActions;
                if (!actions) continue;

                if (r.is_create_or_update) {
                    actions.create = false;
                    actions.edit = false;
                }
                if (r.is_delete) {
                    actions.delete = false;
                }
                if (r.is_archive) {
                    actions.archive = false;
                    actions.unarchive = false;
                }
            }
        });
    },
});
