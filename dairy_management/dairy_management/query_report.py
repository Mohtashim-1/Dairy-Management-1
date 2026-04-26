import frappe
from frappe.desk import query_report as _fq


_LEGACY_REPORT_NAME_MAP = {
	"Milk Dispatch & Revenue Report": "Milk Dispatch and Revenue Report",
	"Profit & Loss Summary Report": "Profit and Loss Summary Report",
}


def _canonical_report_name(report_name: str | None) -> str | None:
	if not report_name:
		return report_name
	return _LEGACY_REPORT_NAME_MAP.get(report_name, report_name)


@frappe.whitelist()
@frappe.read_only()
def run(
	report_name,
	filters=None,
	user=None,
	ignore_prepared_report=False,
	custom_columns=None,
	is_tree=False,
	parent_field=None,
	are_default_filters=True,
):
	return _fq.run(
		_canonical_report_name(report_name),
		filters=filters,
		user=user,
		ignore_prepared_report=ignore_prepared_report,
		custom_columns=custom_columns,
		is_tree=is_tree,
		parent_field=parent_field,
		are_default_filters=are_default_filters,
	)
