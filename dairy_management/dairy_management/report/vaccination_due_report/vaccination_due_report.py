import frappe
from frappe import _


def execute(filters=None):
	return get_columns(), get_data()


def get_columns():
	return [
		{"label": _("Animal"), "fieldname": "animal", "fieldtype": "Link", "options": "Animal", "width": 120},
		{"label": _("Vaccine"), "fieldname": "vaccine_name", "fieldtype": "Data", "width": 180},
		{"label": _("Last Given"), "fieldname": "administered_date", "fieldtype": "Date", "width": 110},
		{"label": _("Next Due"), "fieldname": "next_due", "fieldtype": "Date", "width": 110},
		{"label": _("Days Overdue"), "fieldname": "days_overdue", "fieldtype": "Int", "width": 110},
	]


def get_data():
	return frappe.db.sql(
		"""
		SELECT
			animal,
			vaccine_name,
			administered_date,
			next_due,
			GREATEST(DATEDIFF(CURDATE(), next_due), 0) AS days_overdue
		FROM `tabVaccination Schedule`
		WHERE next_due IS NOT NULL
		ORDER BY next_due ASC
		""",
		as_dict=True,
	)
