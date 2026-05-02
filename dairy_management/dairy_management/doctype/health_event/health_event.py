# Copyright (c) 2026, mohtashim and contributors
# For license information, please see license.txt

from frappe.model.document import Document
from frappe.utils import add_days


class HealthEvent(Document):
	def validate(self):
		if self.event_date and self.withdrawal_days is not None:
			self.milk_safe_date = add_days(self.event_date, int(self.withdrawal_days))
