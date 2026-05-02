# Copyright (c) 2026, mohtashim and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import getdate


def execute(filters=None):
	filters = filters or {}
	return get_columns(), get_data(filters)


def get_columns():
	return [
		{"label": _("Date"), "fieldname": "recording_date", "fieldtype": "Date", "width": 110},
		{"label": _("Animal"), "fieldname": "animal", "fieldtype": "Link", "options": "Animal", "width": 130},
		{"label": _("Breed"), "fieldname": "breed_name", "fieldtype": "Data", "width": 120},
		{"label": _("Morning (L)"), "fieldname": "morning_l", "fieldtype": "Float", "width": 100},
		{"label": _("Evening (L)"), "fieldname": "evening_l", "fieldtype": "Float", "width": 100},
		{"label": _("Total Yield (L)"), "fieldname": "total_yield_l", "fieldtype": "Float", "width": 110},
		{"label": _("Fat %"), "fieldname": "fat_percent", "fieldtype": "Float", "width": 80},
		{"label": _("SCC"), "fieldname": "scc", "fieldtype": "Int", "width": 90},
	]


def get_data(filters):
	conditions = ["1=1"]
	values: dict = {}

	if filters.get("from_date"):
		conditions.append("mr.recording_date >= %(from_date)s")
		values["from_date"] = getdate(filters["from_date"])
	if filters.get("to_date"):
		conditions.append("mr.recording_date <= %(to_date)s")
		values["to_date"] = getdate(filters["to_date"])
	if filters.get("animal"):
		conditions.append("mr.animal = %(animal)s")
		values["animal"] = filters["animal"]
	if filters.get("breed"):
		conditions.append("a.breed = %(breed)s")
		values["breed"] = filters["breed"]
	if filters.get("parlour"):
		conditions.append("mr.parlour = %(parlour)s")
		values["parlour"] = filters["parlour"]

	where_sql = " AND ".join(conditions)

	return frappe.db.sql(
		f"""
		SELECT
			mr.recording_date,
			mr.animal,
			IFNULL(b.breed_name, '') AS breed_name,
			SUM(CASE WHEN mr.session = 'Morning' THEN mr.yield_litres ELSE 0 END) AS morning_l,
			SUM(CASE WHEN mr.session = 'Evening' THEN mr.yield_litres ELSE 0 END) AS evening_l,
			SUM(mr.yield_litres) AS total_yield_l,
			ROUND(AVG(mr.fat_percent), 2) AS fat_percent,
			MAX(mr.scc) AS scc
		FROM `tabMilk Recording` mr
		LEFT JOIN `tabAnimal` a ON a.name = mr.animal
		LEFT JOIN `tabAnimal Breed` b ON b.name = a.breed
		WHERE {where_sql}
		GROUP BY mr.recording_date, mr.animal, a.breed
		ORDER BY mr.recording_date DESC, mr.animal
		""",
		values,
		as_dict=True,
	)
