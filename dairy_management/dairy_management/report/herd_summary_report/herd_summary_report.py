# Copyright (c) 2026, mohtashim and contributors
# For license information, please see license.txt

import frappe
from frappe import _


def execute(filters=None):
	columns = get_columns()
	data = get_data()
	return columns, data


def get_columns():
	return [
		{"label": _("Animal ID"), "fieldname": "animal_id", "fieldtype": "Data", "width": 130},
		{"label": _("Name"), "fieldname": "animal_name", "fieldtype": "Data", "width": 140},
		{"label": _("Breed"), "fieldname": "breed", "fieldtype": "Link", "options": "Animal Breed", "width": 130},
		{"label": _("Age (Months)"), "fieldname": "age_months", "fieldtype": "Float", "precision": 1, "width": 120},
		{"label": _("Status"), "fieldname": "status", "fieldtype": "Data", "width": 120},
		{"label": _("Pen"), "fieldname": "pen_assignment", "fieldtype": "Link", "options": "Pen", "width": 150},
		{"label": _("Weight (kg)"), "fieldname": "weight_kg", "fieldtype": "Float", "precision": 2, "width": 110},
	]


def get_data():
	return frappe.db.sql(
		"""
		SELECT
			animal_id,
			animal_name,
			breed,
			ROUND(DATEDIFF(CURDATE(), date_of_birth) / 30, 1) AS age_months,
			status,
			pen_assignment,
			weight_kg
		FROM `tabAnimal`
		ORDER BY animal_id
		""",
		as_dict=True,
	)
