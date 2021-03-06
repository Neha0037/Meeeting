import frappe
from frappe import _
from frappe.utils import nowdate, add_days,formatdate
import dateutil.parser
import datetime
from datetime import datetime, timedelta
# from frappe.utils.data import get_date

@frappe.whitelist()
def send_invitation_emails(meeeting):
	meeeting = frappe.get_doc("Meeeting",meeeting)
	meeeting.check_permission("email")

	if meeeting.status == "Planned":
		frappe.sendmail(
			recepients = [d.attendee for d in meeeting.attendees],
			sender = frappe.session.user,
			subject = meeeting.title,
			message= meeeting.invitation_message,
			reference_doctype= meeeting.doctype,
			reference_name= meeeting.name,
			as_bulk=True
		)

		meeeting.status = "Invitation Sent"
		meeeting.save()

		frappe.msgprint(_("Invitation Sent"))

	else:
		frappe.msgprint(_("Meeeting status must be 'Planned'"))

@frappe.whitelist()
def get_meeetings(start, end):
	if not frappe.has_permission("Meeeting","read"):
		raise frappe.PermissionError
	return frappe.db.sql("""select 
		timestamp(`date`,from_time) as start,
		timestamp(`date`,to_time) as end,
		from_time,
		to_time,
		name,
		title,
		status	
		from `tabMeeeting`
		where `date` between %(start)s and %(end)s""", {
		"start" : start,
		"end" : end
	}, as_dict = True)

def make_orientation_meeeting(doc, method):
	meeeting = frappe.get_doc({
			"doctype": "Meeeting",
			"title": "Orientation for {0}".format(doc.first_name),
			"date": add_days(nowdate(), 1),
			"from_time": "09:00",
			"to_time": "09:30",
			"status": "Planned",
			"attendees": [{
				"attendee": doc.name
			}]
		})
	meeeting.flags.ignore_permissions = True
	meeeting.insert()
	frappe.msgprint(_("Orientation meeting created"))

def update_minute_status(doc, method = None):
	if doc.reference_type != "Meeeting" or doc.flags.from_meeting:
		return

	if method =="on_trash" or doc.status=="Closed":
		meeeting = frappe.get_doc(doc.reference_type.doc.reference_name)
		for minute in meeeting.minutes:
			if minute.todo == doc.name:
				minute.db_set("todo", None, update_modified = False)
				minute.db_set("status","Closed", update_modified = False)

def update_payment_status(self, method):
	for mode in self.payments:
		if mode.mode_of_payment == 'Credit Card':
			frappe.db.set(self,'reconcilation_status','Unreconciled')
			# frappe.msgprint('check')
			break

def date_interval(start_date,end_date,interval):
	interval_dict = {}
	intv = timedelta(interval)
	diff = (end_date  - start_date ) / intv
	for i in range(int(diff) + 1):
		interval_dict[i] = [start_date + intv * i]
		interval_dict[i].append((start_date + intv * (i + 1) - timedelta(1)))
	interval_dict.pop(len(interval_dict) - 1)
	a = (start_date + intv * (len(interval_dict) + 1) - timedelta(1))
	interval_dict[len(interval_dict)] = [(start_date + intv * (len(interval_dict)))]
	if(a < end_date):
		interval_dict[len(interval_dict) - 1].append((start_date + intv * [len(interval_dict) + 1] - timedelta(1)))
	else:
		interval_dict[len(interval_dict) - 1].append(end_date)
	return interval_dict