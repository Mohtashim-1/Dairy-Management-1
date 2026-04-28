# Copyright (c) 2026, mohtashim and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import cint, flt

# Chill threshold for bulk milk (°C); above this triggers a temperature breach alert.
MAX_SAFE_BULK_TEMP_C = 5.0


class BulkTankLog(Document):
	def validate(self):
		self.alert_temperature_breach()
		self.alert_antibiotic_milk()
		self.validate_dispatch_rules()

	def alert_temperature_breach(self):
		if self.temperature_c is None:
			return
		temp = flt(self.temperature_c)
		if temp > MAX_SAFE_BULK_TEMP_C:
			frappe.msgprint(
				_("Temperature breach: bulk milk is above {0} °C (recorded {1} °C). Check cooling immediately.").format(
					MAX_SAFE_BULK_TEMP_C,
					temp,
				),
				title=_("Temperature Alert"),
				indicator="red",
			)

	def alert_antibiotic_milk(self):
		if not self.tank:
			return
		if not cint(frappe.db.get_value("Bulk Tank", self.tank, "antibiotic")):
			return
		frappe.msgprint(
			_("Antibiotic milk alert: bulk tank {0} is flagged as antibiotic-positive.").format(
				frappe.bold(self.tank)
			),
			title=_("Antibiotic Milk Alert"),
			indicator="orange",
		)

	def validate_dispatch_rules(self):
		if not self.tank:
			return
		qty = flt(self.quantity_litres)
		dispatch_qty = flt(self.dispatch_litres)
		dispatched = cint(self.dispatched)

		if dispatched:
			if cint(frappe.db.get_value("Bulk Tank", self.tank, "antibiotic")):
				frappe.throw(_("Dispatch is blocked while Bulk Tank {0} has Antibiotic enabled.").format(self.tank))

			if dispatch_qty <= 0:
				frappe.throw(_("Dispatch Litres must be greater than zero when Dispatched is checked."))

			if dispatch_qty > qty:
				frappe.throw(
					_("Dispatch quantity ({0} L) cannot exceed available quantity in tank ({1} L).").format(
						dispatch_qty,
						qty,
					)
				)
