# Copyright (c) 2026, mohtashim and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import cint

# Warn when yield is below this (litres); zero yield is blocked separately.
LOW_YIELD_ALERT_LITRES = 5.0


class MilkRecording(Document):
	def validate(self):
		self.validate_yield_positive()
		self.validate_animal_lactating()
		self.alert_low_yield()
		self.alert_antibiotic_milk()

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
