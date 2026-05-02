# Copyright (c) 2026, mohtashim and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import add_days, today


@frappe.whitelist()
def get_milk_recording_dashboard_data():
	"""KPIs for the Milk Recording dashboard (today and last 7 days)."""
	tod = today()
	start_7 = add_days(tod, -7)

	today_totals = frappe.db.sql(
		"""
		SELECT
			COALESCE(SUM(yield_litres), 0) AS total_l,
			COUNT(*) AS recordings
		FROM `tabMilk Recording`
		WHERE recording_date = %(d)s
		""",
		{"d": tod},
		as_dict=True,
	)
	l7 = frappe.db.sql(
		"""
		SELECT COALESCE(SUM(yield_litres), 0) AS total_l
		FROM `tabMilk Recording`
		WHERE recording_date >= %(s)s AND recording_date <= %(e)s
		""",
		{"s": start_7, "e": tod},
		as_dict=True,
	)
	session = frappe.db.sql(
		"""
		SELECT session, COALESCE(SUM(yield_litres), 0) AS litres
		FROM `tabMilk Recording`
		WHERE recording_date = %(d)s
		GROUP BY session
		""",
		{"d": tod},
		as_dict=True,
	)
	return {
		"today": today_totals[0] if today_totals else {"total_l": 0, "recordings": 0},
		"last_7_days_total_l": l7[0].total_l if l7 else 0,
		"session_split": session,
		"as_of": tod,
	}
