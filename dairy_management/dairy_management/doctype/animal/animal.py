# Copyright (c) 2026, mohtashim and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class Animal(Document):
	def validate(self):
		self.validate_rfid_unique()
		self.validate_pen_capacity()

	def validate_rfid_unique(self):
		rfid = (self.rfid_tag or "").strip()
		if not rfid:
			return
		dup = frappe.db.exists(
			"Animal",
			{"rfid_tag": rfid, "name": ["!=", self.name]},
		)
		if dup:
			frappe.throw(
				_("RFID Tag must be unique. Tag {0} is already assigned to animal {1}.").format(
					frappe.bold(rfid),
					frappe.bold(dup),
				)
			)

	def validate_pen_capacity(self):
		if not self.pen_assignment:
			return
		capacity = frappe.db.get_value("Pen", self.pen_assignment, "capacity")
		if capacity is None:
			return
		count_others = frappe.db.count(
			"Animal",
			{"pen_assignment": self.pen_assignment, "name": ["!=", self.name]},
		)
		if count_others + 1 > int(capacity):
			frappe.throw(
				_("Pen capacity exceeded for {0}: capacity is {1} animals but assigning this animal would place {2}.").format(
					frappe.bold(self.pen_assignment),
					int(capacity),
					count_others + 1,
				)
			)
