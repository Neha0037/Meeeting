// Copyright (c) 2016, Frappe and contributors
// For license information, please see license.txt
/* eslint-disable */

	
frappe.query_reports["Meeting Minutes"] = {
	"filters": [
		// {
		// 	"fieldname":"from_date",
		// 	"label": __("From Date"),
		// 	"fieldtype": "Date",
		// 	"default": frappe.datetime.add_months(frappe.datetime.get_today(), -1),
		// 	"width": "80"
		// },
		// {
		// 	"fieldname":"to_date",
		// 	"label": __("To Date"),
		// 	"fieldtype": "Date",
		// 	"default": frappe.datetime.get_today()
		// },
		{
			"fieldname":"party_type",
			"label": __("Party Type"),
			"fieldtype": "Link",
			"options":"DocType",
			get_query: function () {
						return {
							filters: [
								["DocType", "name", "in", ["Customer","Supplier","Meeeting"]]
							]
						};
					},
			"width": "80",
			"default": "",
			onchange: function() {
				frappe.query_report.set_filter_value("party", "");
			}
		},
		{
			"fieldname":"party",
			"label": __("Party"),
			"fieldtype": "MultiSelectList",
			get_data: function(txt) {
				// if (!frappe.query_report.filters) return;

				let party_type = frappe.query_report.get_filter_value('party_type');
				// if (!party_type) return;

				return frappe.db.get_link_options(party_type, txt);
			}
		},
		{
			"fieldname":"assigned_to",
			"label": __("Assigned to"),
			"fieldtype": "Link",
			"options":"User"
		},
		{
			"fieldname":"name",
			"label":"Name",
			"fieldtype":"Link",
			"options":"Meeeting"
		},
		{
			"fieldname":"datedefault",
			"label":__("Date Default"),
			"fieldtype":"Date"
		}
	],

	onload: async function(report) {
        var refdate = await frappe.db.get_value("MeetingDefault", "MeetingDefault", "datedefault");
        report.set_filter_value("datedefault", refdate.message.datedefault);

        var doc_list = ["Meeeting","Customer","Supplier"]
    }
};

