# Copyright (c) 2026, mohtashim and contributors
# For license information, please see license.txt

"""Scheduled alerts for Dairy Management."""

import frappe
from frappe import _
from frappe.utils import add_days, format_date, today


def dairy_daily_alerts():
	send_semen_batch_expiry_alerts()
	send_vaccination_schedule_alerts()


def send_semen_batch_expiry_alerts():
	"""Email digest for semen batches expiring within 7 days."""
	until = add_days(today(), 7)
	batches = frappe.db.sql(
		"""
		SELECT name, batch_id, expiry_date
		FROM `tabSemen Batch`
		WHERE expiry_date IS NOT NULL
		AND expiry_date >= %(today)s
		AND expiry_date <= %(until)s
		ORDER BY expiry_date
		""",
		{"today": today(), "until": until},
		as_dict=True,
	)
	if not batches:
		return
	lines = "<br>".join(
		_("{0} — expires {1}").format(
			frappe.bold(b.batch_id or b.name),
			format_date(b.expiry_date),
		)
		for b in batches
	)
	recipients = _notification_recipients()
	if not recipients:
		return
	frappe.sendmail(
		recipients=recipients,
		subject=_("Semen batches expiring within 7 days"),
		message=_("The following semen batches require attention:<br><br>{0}").format(lines),
	)


def send_vaccination_schedule_alerts():
	"""Email digest for vaccinations due within 3 days (scheduled or next due)."""
	window_end = add_days(today(), 3)
	rows = frappe.db.sql(
		"""
		SELECT name, animal, vaccine_name, scheduled_date, next_due
		FROM `tabVaccination Schedule`
		WHERE docstatus < 2
		AND (
			(scheduled_date IS NOT NULL AND scheduled_date BETWEEN %(today)s AND %(end)s)
			OR (next_due IS NOT NULL AND next_due BETWEEN %(today)s AND %(end)s)
		)
		ORDER BY COALESCE(next_due, scheduled_date)
		""",
		{"today": today(), "end": window_end},
		as_dict=True,
	)
	if not rows:
		return
	lines = "<br>".join(
		_("{0} — {1} — due {2}").format(
			r.animal or _("(herd)"),
			frappe.bold(r.vaccine_name),
			format_date(r.next_due or r.scheduled_date),
		)
		for r in rows
	)
	recipients = _notification_recipients()
	if not recipients:
		return
	frappe.sendmail(
		recipients=recipients,
		subject=_("Vaccinations due within 3 days"),
		message=_("Upcoming vaccinations:<br><br>{0}").format(lines),
	)


def _notification_recipients():
	emails = set()
	for role in ("Stock Manager", "System Manager", "Manufacturing User"):
		for user in frappe.get_all(
			"Has Role",
			filters={"role": role, "parenttype": "User"},
			pluck="parent",
		):
			if user in ("Administrator", "Guest"):
				continue
			email = frappe.db.get_value("User", user, "email")
			if email:
				emails.add(email)
	return sorted(emails)
