import frappe
from frappe import _


def execute(filters=None):
	return get_columns(), get_data()


def get_columns():
	return [
		{"label": _("Date"), "fieldname": "recording_date", "fieldtype": "Date", "width": 110},
		{"label": _("Animal"), "fieldname": "animal", "fieldtype": "Link", "options": "Animal", "width": 130},
		{"label": _("Breed"), "fieldname": "breed", "fieldtype": "Link", "options": "Animal Breed", "width": 120},
		{"label": _("Morning (L)"), "fieldname": "morning_l", "fieldtype": "Float", "width": 100},
		{"label": _("Evening (L)"), "fieldname": "evening_l", "fieldtype": "Float", "width": 100},
		{"label": _("Total Yield (L)"), "fieldname": "total_yield_l", "fieldtype": "Float", "width": 110},
		{"label": _("Fat %"), "fieldname": "fat_percent", "fieldtype": "Float", "width": 80},
		{"label": _("SCC"), "fieldname": "scc", "fieldtype": "Int", "width": 90},
	]


def get_data():
	return frappe.db.sql(
		"""
		SELECT
			mr.recording_date,
			mr.animal,
			a.breed,
			SUM(CASE WHEN mr.session = 'Morning' THEN mr.yield_litres ELSE 0 END) AS morning_l,
			SUM(CASE WHEN mr.session = 'Evening' THEN mr.yield_litres ELSE 0 END) AS evening_l,
			SUM(mr.yield_litres) AS total_yield_l,
			ROUND(AVG(mr.fat_percent), 2) AS fat_percent,
			MAX(mr.scc) AS scc
		FROM `tabMilk Recording` mr
		LEFT JOIN `tabAnimal` a ON a.name = mr.animal
		GROUP BY mr.recording_date, mr.animal, a.breed
		ORDER BY mr.recording_date DESC, mr.animal
		""",
		as_dict=True,
	)
