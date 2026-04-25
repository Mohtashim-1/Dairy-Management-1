import frappe
from frappe import _


def execute(filters=None):
	return get_columns(), get_data()


def get_columns():
	return [
		{"label": _("Equipment"), "fieldname": "equipment_name", "fieldtype": "Data", "width": 170},
		{"label": _("Category"), "fieldname": "category", "fieldtype": "Data", "width": 130},
		{"label": _("Last Service"), "fieldname": "last_service", "fieldtype": "Date", "width": 110},
		{"label": _("Next Service Due"), "fieldname": "next_service", "fieldtype": "Date", "width": 120},
		{"label": _("Days to Service"), "fieldname": "days_to_service", "fieldtype": "Int", "width": 110},
		{"label": _("Status"), "fieldname": "status", "fieldtype": "Data", "width": 110},
		{"label": _("Last Cost"), "fieldname": "last_cost", "fieldtype": "Currency", "width": 100},
	]


def get_data():
	return frappe.db.sql(
		"""
		SELECT
			e.equipment_name,
			e.category,
			e.last_service,
			e.next_service,
			DATEDIFF(e.next_service, CURDATE()) AS days_to_service,
			e.status,
			(
				SELECT ml.cost
				FROM `tabMaintenance Log` ml
				WHERE ml.equipment = e.name
				ORDER BY ml.service_date DESC, ml.creation DESC
				LIMIT 1
			) AS last_cost
		FROM `tabEquipment` e
		ORDER BY e.next_service ASC
		""",
		as_dict=True,
	)
