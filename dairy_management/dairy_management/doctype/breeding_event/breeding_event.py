# Copyright (c) 2026, mohtashim and contributors
# For license information, please see license.txt

from frappe.model.document import Document
from frappe.utils import add_days


class BreedingEvent(Document):
	def validate(self):
		if self.event_date:
			self.expected_calving = add_days(self.event_date, 280)
