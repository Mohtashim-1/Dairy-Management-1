# Copyright (c) 2026, mohtashim and contributors
# For license information, please see license.txt

"""Health-driven rules for milk collection (withdrawal / milk safe date)."""

import frappe
from frappe import _
from frappe.utils import getdate


def get_latest_health_event_milk_safe_date(animal: str):
	if not animal:
		return None
	row = frappe.db.sql(
		"""
		SELECT milk_safe_date
		FROM `tabHealth Event`
		WHERE animal = %s AND milk_safe_date IS NOT NULL
		ORDER BY event_date DESC, modified DESC
		LIMIT 1
		""",
		animal,
		as_dict=True,
	)
	if not row:
		return None
	return row[0].milk_safe_date


def animal_under_milk_withdrawal(animal: str) -> bool:
	"""True if today is strictly before the vet-defined milk safe date (still in withdrawal)."""
	msd = get_latest_health_event_milk_safe_date(animal)
	if not msd:
		return False
	return getdate() < getdate(msd)


def animal_allowed_for_milk_collection(animal: str) -> bool:
	return not animal_under_milk_withdrawal(animal)
