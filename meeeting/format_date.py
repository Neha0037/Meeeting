import frappe

@frappe.whitelist()
def get_formatdate(filters):
	d =  frappe.db.get_single_value("MeetingDefault","datedefault")
	# print(d)
	# print("hiiiii")
	# date_time_obj = datetime.datetime.strptime(d, '%Y-%m-%d %H:%M:%S.%f')
	# frappe.msgprint("date---")
	# print('Date:', date_time_obj.date())
	# return date_time_obj
	return d;
