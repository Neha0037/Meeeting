	// Copyright (c) 2019, Frappe and contributors
// For license information, please see license.txt
frappe.ui.form.on('Meeeting', {
	send_emails: function(frm) {
		if(frm.doc.status==="Planned") {
			frappe.call({
				method: "meeeting.api.send_invitation_emails",
				args: {
					meeeting: frm.doc.name
				},
				callback: function(r) {

				}
			});
		}
	},
});

frappe.ui.form.on('Meeeting Attendee', {

	attendee: function(frm, cdt, cdn) {
		var attendee = frappe.model.get_doc(cdt, cdn);
		if(attendee.attendee) {
			frm.call({
				method: "meeeting.meeeting.doctype.meeeting.meeeting.get_full_name",
				args: {
					attendee: attendee.attendee
				},
				callback: function(r) {
					frappe.model.set_value(cdt, cdn, "full_name", r.message);
				}
			});
		}else {
			frappe.model.set_value(cdt, cdn, "full_name", null);
		}
	}
})

