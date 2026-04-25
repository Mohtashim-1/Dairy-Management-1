import frappe
from frappe import _


def execute(filters=None):
	return get_columns(), get_data(filters or {})


def get_columns():
	return [
		{"label": _("Animal"), "fieldname": "animal", "fieldtype": "Link", "options": "Animal", "width": 120},
		{"label": _("Event Date"), "fieldname": "movement_date", "fieldtype": "Date", "width": 100},
		{"label": _("Movement Type"), "fieldname": "movement_type", "fieldtype": "Data", "width": 120},
		{"label": _("From"), "fieldname": "from_location", "fieldtype": "Data", "width": 130},
		{"label": _("To"), "fieldname": "to_location", "fieldtype": "Data", "width": 130},
		{"label": _("Permit No."), "fieldname": "permit_no", "fieldtype": "Data", "width": 120},
		{"label": _("Authorized By"), "fieldname": "authorized_by", "fieldtype": "Link", "options": "Employee", "width": 130},
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
		SELECT animal, movement_date, movement_type, from_location, to_location, permit_no, authorized_by
		FROM `tabAnimal Movement Record`
		{where}
		ORDER BY movement_date DESC, animal
		""",
		values,
		as_dict=True,
	)
