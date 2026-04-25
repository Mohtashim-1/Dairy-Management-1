# Copyright (c) 2026, mohtashim and contributors
# For license information, please see license.txt

from frappe.model.document import Document
import frappe


class FeedingLog(Document):
	def validate(self):
		if self.ration_plan and self.qty_kg is not None:
			planned = frappe.db.get_value("Ration Plan", self.ration_plan, "qty_per_head_kg") or 0
			self.variance_kg = float(self.qty_kg or 0) - float(planned)
