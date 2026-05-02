// Copyright (c) 2026, mohtashim and contributors
// For license information, please see license.txt

frappe.ui.form.on("Feed Inventory", {
	refresh(frm) {
		frm.set_intro(
			__(
				"Current stock is read-only from the Stock Ledger for the selected warehouse. Update quantities using Stock Entry and other stock transactions only."
			),
			"blue"
		);
	},
});
