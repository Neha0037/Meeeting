// Copyright (c) 2019, hello@openetech.com and contributors
// For license information, please see license.txt

frappe.ui.form.on('ER EMP Summary Settings', {
	refresh(frm) {
		frm.add_custom_button(__('Summarize'), function() 
			{
				frm.events.schedule_yearly(frm)}, __("EMP Balances"));
			},
		schedule_yearly: function(frm) {
			frappe.call({
				method: "meeeting.meeeting.doctype.er_emp_summary_settings.er_emp_summary_settings.schedule_summarize_emp_entry",
				callback: function(r) {
					console.log(r.message);
				}
			});
		}
	});
