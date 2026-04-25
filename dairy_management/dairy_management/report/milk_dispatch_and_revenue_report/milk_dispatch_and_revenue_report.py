import frappe
from frappe import _


def execute(filters=None):
	return get_columns(), get_data()


def get_columns():
	return [
		{"label": _("Date"), "fieldname": "log_date", "fieldtype": "Date", "width": 110},
		{"label": _("Tank"), "fieldname": "tank", "fieldtype": "Link", "options": "Bulk Tank", "width": 120},
		{"label": _("Buyer"), "fieldname": "buyer", "fieldtype": "Link", "options": "Customer", "width": 160},
		{"label": _("Dispatched (L)"), "fieldname": "dispatch_litres", "fieldtype": "Float", "width": 120},
		{"label": _("Rate (PKR/L)"), "fieldname": "price_per_litre", "fieldtype": "Currency", "width": 120},
		{"label": _("Revenue"), "fieldname": "revenue", "fieldtype": "Currency", "width": 120},
	]


def get_data():
	return frappe.db.sql(
		"""
		SELECT
			log_date,
			tank,
			buyer,
			IFNULL(dispatch_litres, 0) AS dispatch_litres,
			IFNULL(price_per_litre, 0) AS price_per_litre,
			IFNULL(dispatch_litres, 0) * IFNULL(price_per_litre, 0) AS revenue
		FROM `tabBulk Tank Log`
		WHERE IFNULL(dispatched, 0) = 1
		ORDER BY log_date DESC, tank
		""",
		as_dict=True,
	)
