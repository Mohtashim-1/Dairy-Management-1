# Copyright (c) 2026, mohtashim and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import getdate, today


class SemenBatch(Document):
	def validate(self):
		self.alert_expiring_within_seven_days()

	def alert_expiring_within_seven_days(self):
		if not self.expiry_date:
			return
		days_left = (getdate(self.expiry_date) - getdate(today())).days
		if 0 <= days_left <= 7:
			frappe.msgprint(
				_("Semen batch {0} expires on {1} ({2} day(s) remaining). Plan use or disposal.").format(
					frappe.bold(self.batch_id or self.name),
					frappe.format_date(self.expiry_date),
					days_left,
				),
				title=_("Semen batch expiry"),
				indicator="orange",
			)
