// Copyright (c) 2026, mohtashim and contributors
// For license information, please see license.txt

frappe.ui.form.on("Milk Recording", {
	setup(frm) {
		frm.set_query("animal", () => ({
			filters: {
				status: "Lactating",
			},
		}));
	},
});
