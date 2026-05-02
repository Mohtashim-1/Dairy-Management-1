// Copyright (c) 2026, mohtashim and contributors
// For license information, please see license.txt

frappe.query_reports["Daily Milk Production Report"] = {
	filters: [
		{
			fieldname: "from_date",
			label: __("From Date"),
			fieldtype: "Date",
			default: frappe.datetime.add_months(frappe.datetime.get_today(), -1),
			reqd: 1,
		},
		{
			fieldname: "to_date",
			label: __("To Date"),
			fieldtype: "Date",
			default: frappe.datetime.get_today(),
			reqd: 1,
		},
		{
			fieldname: "animal",
			label: __("Animal"),
			fieldtype: "Link",
			options: "Animal",
		},
		{
			fieldname: "breed",
			label: __("Breed"),
			fieldtype: "Link",
			options: "Animal Breed",
		},
		{
			fieldname: "parlour",
			label: __("Parlour"),
			fieldtype: "Link",
			options: "Parlour",
		},
	],
};
