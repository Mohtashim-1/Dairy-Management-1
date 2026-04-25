import frappe
from frappe import _


def execute(filters=None):
	return get_columns(), get_data()


def get_columns():
	return [
		{"label": _("Date"), "fieldname": "recording_date", "fieldtype": "Date", "width": 100},
		{"label": _("Total Yield (L)"), "fieldname": "total_yield_l", "fieldtype": "Float", "width": 120},
		{"label": _("Avg Fat %"), "fieldname": "avg_fat", "fieldtype": "Float", "width": 95},
		{"label": _("Avg Protein %"), "fieldname": "avg_protein", "fieldtype": "Float", "width": 110},
		{"label": _("Avg SCC"), "fieldname": "avg_scc", "fieldtype": "Float", "width": 100},
		{"label": _("Rejection Flag"), "fieldname": "rejection_flag", "fieldtype": "Data", "width": 110},
		{"label": _("Dispatched (L)"), "fieldname": "dispatch_litres", "fieldtype": "Float", "width": 120},
	]


def get_data():
	return frappe.db.sql(
		"""
		SELECT
			mr.recording_date,
			SUM(IFNULL(mr.yield_litres, 0)) AS total_yield_l,
			ROUND(AVG(IFNULL(mr.fat_percent, 0)), 2) AS avg_fat,
			ROUND(AVG(IFNULL(mr.protein_percent, 0)), 2) AS avg_protein,
			ROUND(AVG(IFNULL(mr.scc, 0)), 0) AS avg_scc,
			CASE WHEN AVG(IFNULL(mr.scc, 0)) > 400000 THEN 'Yes' ELSE 'No' END AS rejection_flag,
			IFNULL(bt.dispatch_litres, 0) AS dispatch_litres
		FROM `tabMilk Recording` mr
		LEFT JOIN (
			SELECT log_date, SUM(IFNULL(dispatch_litres, 0)) AS dispatch_litres
			FROM `tabBulk Tank Log`
			GROUP BY log_date
		) bt ON bt.log_date = mr.recording_date
		GROUP BY mr.recording_date, bt.dispatch_litres
		ORDER BY mr.recording_date DESC
		""",
		as_dict=True,
	)
