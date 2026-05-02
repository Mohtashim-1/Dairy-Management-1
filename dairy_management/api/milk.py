# Copyright (c) 2026, mohtashim and contributors
# For license information, please see license.txt

import frappe
from frappe import _

from dairy_management.dairy_health import animal_under_milk_withdrawal, get_latest_health_event_milk_safe_date


@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def milk_collection_animal_query(doctype, txt, searchfield, start, page_len, filters):
	"""Restrict Milk Recording animal link to lactating animals past milk withdrawal."""
	today = frappe.utils.today()
	txt_clause = ""
	args = {"today": today, "start": int(start), "page_len": int(page_len)}
	if txt:
		txt_clause = " AND (a.name LIKE %(txt)s OR a.animal_name LIKE %(txt)s OR a.animal_id LIKE %(txt)s)"
		args["txt"] = f"%{txt}%"

	return frappe.db.sql(
		f"""
		SELECT a.name, IFNULL(a.animal_name, a.name)
		FROM `tabAnimal` a
		WHERE a.status = 'Lactating'
		{txt_clause}
		AND COALESCE(
			(
				SELECT he.milk_safe_date FROM `tabHealth Event` he
				WHERE he.animal = a.name AND he.milk_safe_date IS NOT NULL
				ORDER BY he.event_date DESC, he.modified DESC
				LIMIT 1
			),
			%(today)s
		) <= %(today)s
		ORDER BY a.name
		LIMIT %(start)s, %(page_len)s
		""",
		args,
	)


@frappe.whitelist()
def check_animal_milk_quarantine(animal: str | None):
	if not animal:
		return {"quarantine": False}
	if not animal_under_milk_withdrawal(animal):
		return {"quarantine": False}
	msd = get_latest_health_event_milk_safe_date(animal)
	return {
		"quarantine": True,
		"milk_safe_date": msd,
		"message": _("Animal under quarantine until Milk Safe Date ({0}).").format(
			frappe.format_date(msd) if msd else _("not set")
		),
	}
