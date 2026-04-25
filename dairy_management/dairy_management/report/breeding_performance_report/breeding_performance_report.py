import frappe
from frappe import _


def execute(filters=None):
	columns = get_columns()
	data = get_data()
	conception_rate = get_conception_rate()
	return columns, data, None, None, [{"value": conception_rate, "label": _("Conception Rate %"), "datatype": "Percent"}]


def get_columns():
	return [
		{"label": _("Animal"), "fieldname": "animal", "fieldtype": "Link", "options": "Animal", "width": 130},
		{"label": _("Service Date"), "fieldname": "event_date", "fieldtype": "Date", "width": 110},
		{"label": _("Method"), "fieldname": "method", "fieldtype": "Data", "width": 110},
		{"label": _("Result"), "fieldname": "result", "fieldtype": "Data", "width": 150},
		{"label": _("Expected Calving"), "fieldname": "expected_calving", "fieldtype": "Date", "width": 130},
		{"label": _("Days Open"), "fieldname": "days_open", "fieldtype": "Int", "width": 100},
	]


def get_data():
	return frappe.db.sql(
		"""
		SELECT
			be.animal,
			be.event_date,
			be.method,
			be.result,
			be.expected_calving,
			DATEDIFF(
				be.event_date,
				(
					SELECT MAX(cr.calving_date)
					FROM `tabCalving Record` cr
					WHERE cr.dam = be.animal AND cr.calving_date <= be.event_date
				)
			) AS days_open
		FROM `tabBreeding Event` be
		ORDER BY be.event_date DESC, be.animal
		""",
		as_dict=True,
	)


def get_conception_rate():
	stats = frappe.db.sql(
		"""
		SELECT
			SUM(CASE WHEN result = 'Confirmed Pregnant' THEN 1 ELSE 0 END) AS confirmed,
			COUNT(*) AS total
		FROM `tabBreeding Event`
		""",
		as_dict=True,
	)[0]
	total = stats.total or 0
	return round(((stats.confirmed or 0) / total) * 100, 2) if total else 0
