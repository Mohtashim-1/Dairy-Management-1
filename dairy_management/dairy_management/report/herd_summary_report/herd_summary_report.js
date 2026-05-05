// Copyright (c) 2026, mohtashim and contributors
// For license information, please see license.txt

frappe.query_reports["Herd Summary Report"] = {
	"filters": [
		{
			fieldname: "animal_id",
			label: __("Animal ID"),
			fieldtype: "Data",
		},
		{
			fieldname: "breed",
			label: __("Breed"),
			fieldtype: "Link",
			options: "Animal Breed",
		},
		{
			fieldname: "pen_assignment",
			label: __("Pen"),
			fieldtype: "Link",
			options: "Pen",
		},
		{
			fieldname: "status",
			label: __("Status"),
			fieldtype: "Select",
			options: "\nActive\nDry\nSick\nSold\nDeceased",
		},
	]
};
