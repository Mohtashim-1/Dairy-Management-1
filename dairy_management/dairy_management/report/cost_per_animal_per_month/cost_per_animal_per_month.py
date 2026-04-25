import frappe
from frappe import _


def execute(filters=None):
	return get_columns(), get_data()


def get_columns():
	return [
		{"label": _("Animal"), "fieldname": "animal", "fieldtype": "Link", "options": "Animal", "width": 130},
		{"label": _("Month"), "fieldname": "month", "fieldtype": "Data", "width": 100},
		{"label": _("Feed Cost"), "fieldname": "feed_cost", "fieldtype": "Currency", "width": 110},
		{"label": _("Health Cost"), "fieldname": "health_cost", "fieldtype": "Currency", "width": 110},
		{"label": _("Total Cost"), "fieldname": "total_cost", "fieldtype": "Currency", "width": 110},
		{"label": _("Milk Yield (L)"), "fieldname": "milk_yield_l", "fieldtype": "Float", "width": 110},
		{"label": _("Revenue"), "fieldname": "revenue", "fieldtype": "Currency", "width": 110},
		{"label": _("Margin"), "fieldname": "margin", "fieldtype": "Currency", "width": 110},
	]


def get_data():
	return frappe.db.sql(
		"""
		SELECT
			m.animal,
			m.month,
			ROUND(IFNULL(fc.feed_cost_total, 0) / NULLIF(mc.animals_in_month, 0), 2) AS feed_cost,
			IFNULL(h.health_cost, 0) AS health_cost,
			ROUND((IFNULL(fc.feed_cost_total, 0) / NULLIF(mc.animals_in_month, 0)) + IFNULL(h.health_cost, 0), 2) AS total_cost,
			IFNULL(m.milk_yield_l, 0) AS milk_yield_l,
			ROUND(IFNULL(m.milk_yield_l, 0) * IFNULL(pr.milk_price, 0), 2) AS revenue,
			ROUND((IFNULL(m.milk_yield_l, 0) * IFNULL(pr.milk_price, 0)) - ((IFNULL(fc.feed_cost_total, 0) / NULLIF(mc.animals_in_month, 0)) + IFNULL(h.health_cost, 0)), 2) AS margin
		FROM (
			SELECT animal, DATE_FORMAT(recording_date, '%Y-%m') AS month, SUM(IFNULL(yield_litres, 0)) AS milk_yield_l
			FROM `tabMilk Recording`
			GROUP BY animal, DATE_FORMAT(recording_date, '%Y-%m')
		) m
		LEFT JOIN (
			SELECT animal, DATE_FORMAT(event_date, '%Y-%m') AS month, SUM(IFNULL(cost, 0)) AS health_cost
			FROM `tabHealth Event`
			GROUP BY animal, DATE_FORMAT(event_date, '%Y-%m')
		) h ON h.animal = m.animal AND h.month = m.month
		LEFT JOIN (
			SELECT DATE_FORMAT(entry_date, '%Y-%m') AS month, SUM(IFNULL(amount, 0)) AS feed_cost_total
			FROM `tabDairy Expense Entry`
			WHERE expense_category = 'Feed'
			GROUP BY DATE_FORMAT(entry_date, '%Y-%m')
		) fc ON fc.month = m.month
		LEFT JOIN (
			SELECT DATE_FORMAT(recording_date, '%Y-%m') AS month, COUNT(DISTINCT animal) AS animals_in_month
			FROM `tabMilk Recording`
			GROUP BY DATE_FORMAT(recording_date, '%Y-%m')
		) mc ON mc.month = m.month
		LEFT JOIN (
			SELECT DATE_FORMAT(entry_date, '%Y-%m') AS month,
				AVG(CASE WHEN income_type = 'Milk Sale' AND IFNULL(quantity, 0) > 0 THEN amount / quantity END) AS milk_price
			FROM `tabDairy Income Entry`
			GROUP BY DATE_FORMAT(entry_date, '%Y-%m')
		) pr ON pr.month = m.month
		ORDER BY m.month DESC, m.animal
		""",
		as_dict=True,
	)
