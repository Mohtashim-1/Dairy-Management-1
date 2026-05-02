// Copyright (c) 2026, mohtashim and contributors
// For license information, please see license.txt

frappe.ui.form.on("Milk Recording", {
	setup(frm) {
		frm.set_query("animal", () => ({
			query: "dairy_management.api.milk.milk_collection_animal_query",
		}));
	},

	refresh(frm) {
		if (frm.doc.animal) {
			frappe.call({
				method: "dairy_management.api.milk.check_animal_milk_quarantine",
				args: { animal: frm.doc.animal },
				callback(r) {
					if (r.message && r.message.quarantine) {
						frappe.msgprint({
							title: __("Animal under quarantine"),
							message: r.message.message,
							indicator: "orange",
						});
					}
				},
			});
		}
	},

	animal(frm) {
		if (!frm.doc.animal) {
			return;
		}
		frappe.call({
			method: "dairy_management.api.milk.check_animal_milk_quarantine",
			args: { animal: frm.doc.animal },
			callback(r) {
				if (r.message && r.message.quarantine) {
					frappe.msgprint({
						title: __("Animal under quarantine"),
						message: r.message.message,
						indicator: "orange",
					});
				}
			},
		});
	},

	is_sample(frm) {
		if (!frm.doc.is_sample) {
			frm.set_value("sample_id", "");
		}
	},
});
