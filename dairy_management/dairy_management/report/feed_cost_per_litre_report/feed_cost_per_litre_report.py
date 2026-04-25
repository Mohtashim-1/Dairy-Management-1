import frappe
from frappe import _


def execute(filters=None):
	return get_columns(), get_data()


def get_columns():
	return [
		{"label": _("Date"), "fieldname": "log_date", "fieldtype": "Date", "width": 105},
		{"label": _("Pen / Group"), "fieldname": "pen", "fieldtype": "Link", "options": "Pen", "width": 120},
		{"label": _("Total Feed Cost"), "fieldname": "total_feed_cost", "fieldtype": "Currency", "width": 120},
		{"label": _("Total Milk (L)"), "fieldname": "total_milk_l", "fieldtype": "Float", "width": 110},
		{"label": _("Cost per Litre"), "fieldname": "cost_per_litre", "fieldtype": "Currency", "width": 110},
		{"label": _("Budget vs Actual"), "fieldname": "budget_vs_actual", "fieldtype": "Currency", "width": 130},
	]


def get_data():
	return frappe.db.sql(
		"""
		SELECT
			f.log_date,
			f.pen,
			SUM(IFNULL(f.cost, 0)) AS total_feed_cost,
			IFNULL(m.total_milk_l, 0) AS total_milk_l,
			CASE WHEN IFNULL(m.total_milk_l, 0) > 0 THEN SUM(IFNULL(f.cost, 0)) / m.total_milk_l ELSE 0 END AS cost_per_litre,
			SUM(IFNULL(f.cost, 0)) - SUM(IFNULL(rp.total_cost_day, 0)) AS budget_vs_actual
		FROM `tabFeeding Log` f
		LEFT JOIN `tabRation Plan` rp ON rp.name = f.ration_plan
		LEFT JOIN (
			SELECT
				mr.recording_date,
				a.pen_assignment AS pen,
				SUM(IFNULL(mr.yield_litres, 0)) AS total_milk_l
			FROM `tabMilk Recording` mr
			LEFT JOIN `tabAnimal` a ON a.name = mr.animal
			GROUP BY mr.recording_date, a.pen_assignment
		) m ON m.recording_date = f.log_date AND m.pen = f.pen
		GROUP BY f.log_date, f.pen, m.total_milk_l
		ORDER BY f.log_date DESC, f.pen
		""",
		as_dict=True,
	)
