# Copyright (c) 2026, mohtashim and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import cint
from frappe.utils.data import get_link_to_form

from dairy_management.dairy_health import animal_allowed_for_milk_collection, get_latest_health_event_milk_safe_date

# Warn when yield is below this (litres); zero yield is blocked separately.
LOW_YIELD_ALERT_LITRES = 5.0

# Roles notified when a parlour sample is logged (production / QA).
SAMPLE_NOTIFICATION_ROLES = ("Manufacturing User", "Stock Manager", "System Manager")


class MilkRecording(Document):
	def validate(self):
		self.validate_yield_positive()
		self.validate_animal_lactating()
		self.validate_milk_safe_gate()
		self.validate_sample_rules()
		self.alert_low_yield()
		self.alert_antibiotic_milk()

	def after_insert(self):
		self.notify_production_on_sample()

	def on_update(self):
		if self.is_sample and (
			self.has_value_changed("is_sample")
			or self.has_value_changed("sample_id")
			or self.has_value_changed("parlour")
			or self.has_value_changed("recording_date")
		):
			self.notify_production_on_sample()

	def validate_yield_positive(self):
		if self.yield_litres is None or float(self.yield_litres) <= 0:
			frappe.throw(_("Yield must be greater than zero. Milk entries with zero yield are not allowed."))

	def validate_animal_lactating(self):
		if not self.animal:
			return
		status = frappe.db.get_value("Animal", self.animal, "status")
		if status != "Lactating":
			frappe.throw(
				_("Milk recording is only allowed for lactating animals. Animal {0} has status {1}.").format(
					frappe.bold(self.animal),
					frappe.bold(status or _("(not set)")),
				)
			)

	def validate_milk_safe_gate(self):
		if not self.animal:
			return
		if not animal_allowed_for_milk_collection(self.animal):
			msd = get_latest_health_event_milk_safe_date(self.animal)
			frappe.throw(
				_("Milk collection is not allowed before Milk Safe Date. Animal {0} is under withdrawal until {1}.").format(
					frappe.bold(self.animal),
					frappe.bold(frappe.format_date(msd) if msd else ""),
				)
			)

	def validate_sample_rules(self):
		if cint(self.is_sample) and not (self.sample_id or "").strip():
			frappe.throw(_("Sample ID is mandatory when Sample is checked."))

	def alert_low_yield(self):
		if self.yield_litres is None:
			return
		yield_litres = float(self.yield_litres)
		if yield_litres <= 0:
			return
		if yield_litres < LOW_YIELD_ALERT_LITRES:
			frappe.msgprint(
				_("Low milk yield alert: recorded yield is {0} L (below {1} L). Review animal health and feeding.").format(
					yield_litres,
					LOW_YIELD_ALERT_LITRES,
				),
				title=_("Low Yield Alert"),
				indicator="orange",
			)

	def alert_antibiotic_milk(self):
		if not cint(self.antibiotic):
			return
		frappe.msgprint(
			_("Antibiotic milk alert: this recording is flagged as antibiotic-positive. Segregate and do not mix with sale milk."),
			title=_("Antibiotic Milk Alert"),
			indicator="red",
		)

	def notify_production_on_sample(self):
		if not cint(self.is_sample):
			return
		parlour_name = self.parlour_title or self.parlour or ""
		subject = _("Parlour milk sample logged — {0}").format(parlour_name or self.name)
		message = _(
			"A milk sample was recorded.<br><br>"
			"<b>Parlour:</b> {0}<br>"
			"<b>Sample ID:</b> {1}<br>"
			"<b>Date:</b> {2}<br>"
			"<b>Recording:</b> {3}"
		).format(
			frappe.bold(parlour_name or _("(not set)")),
			frappe.bold((self.sample_id or "").strip() or _("(not set)")),
			frappe.bold(str(self.recording_date or "")),
			get_link_to_form("Milk Recording", self.name),
		)
		recipients = _production_team_emails()
		if not recipients:
			return
		try:
			frappe.sendmail(recipients=recipients, subject=subject, message=message, now=False)
		except Exception:
			frappe.log_error(title=_("Milk sample notification failed"))


def _production_team_emails():
	emails = set()
	for role in SAMPLE_NOTIFICATION_ROLES:
		for row in frappe.get_all(
			"Has Role",
			filters={"role": role, "parenttype": "User"},
			pluck="parent",
		):
			user = row
			if user == "Administrator" or user == "Guest":
				continue
			email = frappe.db.get_value("User", user, "email")
			if email:
				emails.add(email)
	return sorted(emails)
