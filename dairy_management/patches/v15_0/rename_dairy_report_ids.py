import frappe


def execute():
	# Report document `name` is used to build the python import path; characters like `&` break imports.
	renames = {
		"Milk Dispatch & Revenue Report": "Milk Dispatch and Revenue Report",
		"Profit & Loss Summary Report": "Profit and Loss Summary Report",
	}

	for old, new in renames.items():
		if not frappe.db.exists("Report", old):
			continue
		if frappe.db.exists("Report", new):
			continue
		frappe.rename_doc("Report", old, new, force=True, merge=False)
