import frappe
from frappe import _


def execute(filters=None):
	return get_columns(), get_data()


def get_columns():
	return [
		{"label": _("Period"), "fieldname": "period", "fieldtype": "Data", "width": 100},
		{"label": _("Milk Revenue"), "fieldname": "milk_revenue", "fieldtype": "Currency", "width": 120},
		{"label": _("Other Income"), "fieldname": "other_income", "fieldtype": "Currency", "width": 120},
		{"label": _("Total Income"), "fieldname": "total_income", "fieldtype": "Currency", "width": 120},
		{"label": _("Feed Cost"), "fieldname": "feed_cost", "fieldtype": "Currency", "width": 110},
		{"label": _("Vet Cost"), "fieldname": "vet_cost", "fieldtype": "Currency", "width": 110},
		{"label": _("Labour Cost"), "fieldname": "labour_cost", "fieldtype": "Currency", "width": 110},
		{"label": _("Other Expenses"), "fieldname": "other_expenses", "fieldtype": "Currency", "width": 120},
		{"label": _("Net Profit/Loss"), "fieldname": "net_profit_loss", "fieldtype": "Currency", "width": 130},
	]


def get_data():
	return frappe.db.sql(
		"""
		SELECT
			p.period,
			IFNULL(i.milk_revenue, 0) AS milk_revenue,
			IFNULL(i.other_income, 0) AS other_income,
			IFNULL(i.total_income, 0) AS total_income,
			IFNULL(e.feed_cost, 0) AS feed_cost,
			IFNULL(e.vet_cost, 0) AS vet_cost,
			IFNULL(e.labour_cost, 0) AS labour_cost,
			IFNULL(e.other_expenses, 0) AS other_expenses,
			IFNULL(i.total_income, 0) - IFNULL(e.total_expense, 0) AS net_profit_loss
		FROM (
			SELECT DATE_FORMAT(entry_date, '%Y-%m') AS period FROM `tabDairy Income Entry`
			UNION
			SELECT DATE_FORMAT(entry_date, '%Y-%m') AS period FROM `tabDairy Expense Entry`
		) p
		LEFT JOIN (
			SELECT
				DATE_FORMAT(entry_date, '%Y-%m') AS period,
				SUM(CASE WHEN income_type = 'Milk Sale' THEN IFNULL(amount, 0) ELSE 0 END) AS milk_revenue,
				SUM(CASE WHEN income_type != 'Milk Sale' THEN IFNULL(amount, 0) ELSE 0 END) AS other_income,
				SUM(IFNULL(amount, 0)) AS total_income
			FROM `tabDairy Income Entry`
			GROUP BY DATE_FORMAT(entry_date, '%Y-%m')
		) i ON i.period = p.period
		LEFT JOIN (
			SELECT
				DATE_FORMAT(entry_date, '%Y-%m') AS period,
				SUM(CASE WHEN expense_category = 'Feed' THEN IFNULL(amount, 0) ELSE 0 END) AS feed_cost,
				SUM(CASE WHEN expense_category = 'Veterinary' THEN IFNULL(amount, 0) ELSE 0 END) AS vet_cost,
				SUM(CASE WHEN expense_category = 'Labour' THEN IFNULL(amount, 0) ELSE 0 END) AS labour_cost,
				SUM(CASE WHEN expense_category NOT IN ('Feed', 'Veterinary', 'Labour') THEN IFNULL(amount, 0) ELSE 0 END) AS other_expenses,
				SUM(IFNULL(amount, 0)) AS total_expense
			FROM `tabDairy Expense Entry`
			GROUP BY DATE_FORMAT(entry_date, '%Y-%m')
		) e ON e.period = p.period
		GROUP BY p.period, i.milk_revenue, i.other_income, i.total_income, e.feed_cost, e.vet_cost, e.labour_cost, e.other_expenses, e.total_expense
		ORDER BY period DESC
		""",
		as_dict=True,
	)
