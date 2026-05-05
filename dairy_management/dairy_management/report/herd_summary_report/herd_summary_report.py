# Copyright (c) 2026, mohtashim and contributors
# For license information, please see license.txt

import frappe
from frappe import _


def execute(filters=None):
	filters = filters or {}
	columns = get_columns()
	data = get_data(filters)
	return columns, data


def get_columns():
	return [
		{"label": _("Animal ID"), "fieldname": "animal_id", "fieldtype": "Data", "width": 130},
		{"label": _("Name"), "fieldname": "animal_name", "fieldtype": "Data", "width": 140},
		{"label": _("Breed"), "fieldname": "breed_display", "fieldtype": "Data", "width": 160},
		{"label": _("Age (Months)"), "fieldname": "age_months", "fieldtype": "Float", "precision": 1, "width": 120},
		{"label": _("Status"), "fieldname": "status", "fieldtype": "Data", "width": 120},
		{"label": _("Pen"), "fieldname": "pen_display", "fieldtype": "Data", "width": 170},
		{"label": _("Weight (kg)"), "fieldname": "weight_kg", "fieldtype": "Float", "precision": 2, "width": 110},
	]


def get_data(filters):
	conditions = []
	params = {}

	if filters.get("animal_id"):
		conditions.append("a.animal_id = %(animal_id)s")
		params["animal_id"] = filters.get("animal_id")
	if filters.get("breed"):
		conditions.append("a.breed = %(breed)s")
		params["breed"] = filters.get("breed")
	if filters.get("pen_assignment"):
		conditions.append("a.pen_assignment = %(pen_assignment)s")
		params["pen_assignment"] = filters.get("pen_assignment")
	if filters.get("status"):
		conditions.append("a.status = %(status)s")
		params["status"] = filters.get("status")

	where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""

	return frappe.db.sql(
		f"""
		SELECT
			a.animal_id,
			a.animal_name,
			COALESCE(ab.breed_name, a.breed) AS breed_display,
			ROUND(DATEDIFF(CURDATE(), a.date_of_birth) / 30, 1) AS age_months,
			a.status,
			COALESCE(p.pen_name, a.pen_assignment) AS pen_display,
			a.weight_kg
		FROM `tabAnimal` a
		LEFT JOIN `tabAnimal Breed` ab ON ab.name = a.breed
		LEFT JOIN `tabPen` p ON p.name = a.pen_assignment
		{where_clause}
		ORDER BY a.animal_id
		""",
		params,
		as_dict=True,
	)
