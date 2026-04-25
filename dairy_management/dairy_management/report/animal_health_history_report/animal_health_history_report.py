import frappe
from frappe import _


def execute(filters=None):
	return get_columns(), get_data(filters or {})


def get_columns():
	return [
		{"label": _("Animal"), "fieldname": "animal", "fieldtype": "Link", "options": "Animal", "width": 120},
		{"label": _("Date"), "fieldname": "event_date", "fieldtype": "Date", "width": 100},
		{"label": _("Type"), "fieldname": "event_type", "fieldtype": "Data", "width": 110},
		{"label": _("Diagnosis"), "fieldname": "diagnosis", "fieldtype": "Link", "options": "Disease", "width": 130},
		{"label": _("Treatment"), "fieldname": "treatment", "fieldtype": "Small Text", "width": 220},
		{"label": _("Milk Safe Date"), "fieldname": "milk_safe_date", "fieldtype": "Date", "width": 120},
		{"label": _("Outcome"), "fieldname": "outcome", "fieldtype": "Data", "width": 110},
		{"label": _("Cost"), "fieldname": "cost", "fieldtype": "Currency", "width": 100},
	]


def get_data(filters):
	conditions = []
	values = {}
	if filters.get("animal"):
		conditions.append("animal = %(animal)s")
		values["animal"] = filters["animal"]
	where = f"WHERE {' AND '.join(conditions)}" if conditions else ""

	return frappe.db.sql(
		f"""
		SELECT animal, event_date, event_type, diagnosis, treatment, milk_safe_date, outcome, cost
		FROM `tabHealth Event`
		{where}
		ORDER BY event_date DESC, animal
		""",
		values,
		as_dict=True,
	)
