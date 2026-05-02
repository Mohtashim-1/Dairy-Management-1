# Copyright (c) 2026, mohtashim and contributors
# For license information, please see license.txt

from frappe.model.document import Document
from frappe.utils import flt


class FeedInventory(Document):
	def validate(self):
		self.sync_stock_from_warehouse()

	def sync_stock_from_warehouse(self):
		if not self.feed_item or not self.warehouse:
			return
		try:
			from erpnext.stock.utils import get_stock_balance
		except ImportError:
			return
		balance = get_stock_balance(self.feed_item, self.warehouse)
		self.current_stock_kg = flt(balance)
