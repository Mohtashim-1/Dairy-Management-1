# Copyright (c) 2026, mohtashim and contributors
# For license information, please see license.txt

import frappe


def execute():
	"""Link existing Animals to Item where item code matches animal_id (legacy data)."""
	if not frappe.db.has_column("Animal", "animal_item"):
		return

	rows = frappe.db.sql(
		"""
		SELECT name, animal_id FROM `tabAnimal`
		WHERE IFNULL(animal_item, '') = ''
		""",
		as_dict=True,
	)
	for row in rows:
		item_name = frappe.db.exists("Item", row.animal_id)
		if item_name:
			frappe.db.set_value(
				"Animal",
				row.name,
				"animal_item",
				item_name,
				update_modified=False,
			)
