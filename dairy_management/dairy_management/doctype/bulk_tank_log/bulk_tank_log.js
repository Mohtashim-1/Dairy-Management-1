// Copyright (c) 2026, mohtashim and contributors
// For license information, please see license.txt

frappe.ui.form.on("Bulk Tank Log", {
	refresh(frm) {
		if (frm.doc.__islocal) {
			return;
		}
		frm.add_custom_button(__("Make Stock Entry"), () => {
			frappe.call({
				method: "dairy_management.dairy_management.doctype.bulk_tank_log.bulk_tank_log.make_stock_entry_from_bulk_tank_log",
				args: { source_name: frm.doc.name },
				callback(r) {
					if (r.message) {
						frappe.set_route("Form", "Stock Entry", r.message);
					}
				},
			});
		});
	},
});
