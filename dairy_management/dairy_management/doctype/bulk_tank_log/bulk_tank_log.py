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
		self.sync_quantity_from_milk_recordings()
		self.sync_price_from_item_master()
		self.alert_temperature_breach()
		self.alert_antibiotic_milk()
		self.validate_dispatch_rules()

	def sync_quantity_from_milk_recordings(self):
		if not self.tank or not self.log_date:
			return
		total = frappe.db.sql(
			"""
			SELECT COALESCE(SUM(yield_litres), 0)
			FROM `tabMilk Recording`
			WHERE collected_tank = %s AND recording_date = %s
			""",
			(self.tank, self.log_date),
		)[0][0]
		self.quantity_litres = flt(total)

	def sync_price_from_item_master(self):
		if not self.tank:
			return
		milk_item = frappe.db.get_value("Bulk Tank", self.tank, "milk_item")
		if not milk_item:
			self.price_per_litre = 0
			return
		rate = frappe.db.get_value("Item", milk_item, "standard_rate")
		self.price_per_litre = flt(rate)

	def alert_temperature_breach(self):
		if self.temperature_c is None:
			return
		temp = flt(self.temperature_c)
		if temp > MAX_SAFE_BULK_TEMP_C:
			frappe.msgprint(
				_("Alert: temperature is above {0} °C (recorded {1} °C). Check cooling immediately.").format(
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


@frappe.whitelist()
def make_stock_entry_from_bulk_tank_log(source_name):
	"""Create a draft Material Issue Stock Entry from Bulk Tank Log (for Sales / dispatch flow)."""
	if not frappe.db.exists("DocType", "Stock Entry"):
		frappe.throw(_("ERPNext Stock Entry is not available on this site."))

	doc = frappe.get_doc("Bulk Tank Log", source_name)
	tank = frappe.get_doc("Bulk Tank", doc.tank)
	if not tank.milk_item:
		frappe.throw(_("Set Milk Item on Bulk Tank {0}.").format(doc.tank))
	if not tank.warehouse:
		frappe.throw(_("Set Warehouse on Bulk Tank {0}.").format(doc.tank))

	qty = flt(doc.dispatch_litres) if cint(doc.dispatched) else flt(doc.quantity_litres)
	if qty <= 0:
		frappe.throw(_("Quantity must be greater than zero (set Dispatched and Dispatch Litres or record milk first)."))

	se = frappe.new_doc("Stock Entry")
	se.stock_entry_type = "Material Issue"
	se.company = (
		frappe.defaults.get_user_default("Company")
		or frappe.db.get_single_value("Global Defaults", "default_company")
		or frappe.db.get_single_value("Company", "name")
	)
	se.append(
		"items",
		{
			"item_code": tank.milk_item,
			"qty": qty,
			"s_warehouse": tank.warehouse,
		},
	)
	se.insert()
	return se.name
