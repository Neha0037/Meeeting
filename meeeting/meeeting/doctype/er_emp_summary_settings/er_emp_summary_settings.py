# -*- coding: utf-8 -*-
# Copyright (c) 2019, hello@openetech.com and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe import enqueue
from frappe.model.document import Document
from frappe.core.page.background_jobs.background_jobs import get_info
from frappe.utils import formatdate
from frappe.utils import date_diff, add_days
#from meeeting.meeeting.doctype.er_emp_summary_settings.er_emp_summary_settings import insert_log

class EREMPSummarySettings(Document):
	def validate(self):
		if self.summarize == "Selected Employee" and not self.employee:
			frappe.throw(_("Employee is mandatory for the option of Selected Employee"))

		if self.from_date > self.posting_date:
			frappe.throw(_("From Date cannot be greater than To Date"))

@frappe.whitelist()
def schedule_summarize_emp_entry():
	if not is_queue_running('meeeting.meeeting.doctype.er_emp_summary_settings.er_emp_summary_settings.summarize_emp_entry'):
		result = frappe.utils.background_jobs.enqueue('meeeting.meeeting.doctype.er_emp_summary_settings.er_emp_summary_settings.summarize_emp_entry',
					queue = "long",
					timeout = 3600
					)
		return frappe.msgprint("Payable Summarization Process Started")
	else:
		return frappe.msgprint("A Job for Payable Summarization already running")

def get_job_queue(job_name):
	queue_info = get_info()
	queue_by_job_name = [queue for queue in queue_info if queue.get("job_name")==job_name]
	return queue_by_job_name

def is_queue_running(job_name):
	queue = get_job_queue(job_name)
	return queue and len(queue) > 0 and queue[0].get("status") in ["started", "queued"]

def summarize_emp_entry():
	company = frappe.db.get_single_value('ER EMP Summary Settings', 'company')
	posting_date = frappe.db.get_single_value('ER EMP Summary Settings', 'posting_date')
	from_date = frappe.db.get_single_value('ER EMP Summary Settings', 'from_date')
	summarize = frappe.db.get_single_value('ER EMP Summary Settings', 'summarize')
	employee = frappe.db.get_single_value('ER EMP Summary Settings', 'employee')
	truncate = frappe.db.get_single_value('ER EMP Summary Settings', 'truncate_tables')

	ap_account = frappe.db.sql('''
					select
						default_payable_account, petty_cash_account
					from
						`tabCompany`
					where
						name = %s
					''', (company))
	if ap_account:
		# print("Hii")
		# print(ap_account[0][0])
		# print(ap_account[0][1])
		account = ap_account[0][0]
		petty_cash = ap_account[0][1]
		# tup1 = ap_account[0]
		# account = tup1[0]
		# petty_cash = tup1[1]
	else:
		frappe.throw(_("EMP Control Account not configured in the Company master"))

	select_clause = 'name, company, posting_date, finance_book, party_type, party, voucher_type, voucher_no, against_voucher_type, against_voucher, debit, credit, (debit-credit), 0, "Open"'

	if truncate:
		truncate_tables()
	else:
		delete_data(company, from_date, posting_date, employee)

	if employee and summarize == "Selected Employee":
		conditions = "company=%(company)s and posting_date <= %(posting_date)s and party = %(employee)s and voucher_type = 'Purchase Invoice' and (account = %(account)s or account = %(petty_cash)s)"
		conditions1 = "company=%(company)s and posting_date <= %(posting_date)s and party = %(employee)s and voucher_type = 'Journal Entry' and (account = %(account)s or account = %(petty_cash)s)"
		query_filters = {
			"company": company,
			"from_date": from_date,
			"posting_date": posting_date,
			"employee": employee,
			"account": account,
			"petty_cash": petty_cash
		}
		insert_data(select_clause, conditions, conditions1, query_filters)
	else:
		employee = None
		date_list = date_interval(from_date, posting_date)
		for date in date_list:
			if date['to_date'] == posting_date:
				conditions = "company=%(company)s and posting_date >= %(from_date)s and posting_date <= %(posting_date)s and voucher_type = 'Purchase Invoice' and (account = %(account)s or account = %(petty_cash)s)"
				conditions1 = "company=%(company)s and posting_date >= %(from_date)s and posting_date <= %(posting_date)s and voucher_type in ('Journal Entry', 'Expense Claim') and (account = %(account)s or account = %(petty_cash)s)"
				query_filters = {
					"company": company,
					"from_date": date['from_date'],
					"posting_date": date['to_date'],
					"account": account,
					"petty_cash": petty_cash
				}
				insert_data(select_clause, conditions, conditions1, query_filters)
			else:
				conditions = "company=%(company)s and posting_date >= %(from_date)s and posting_date < %(posting_date)s and voucher_type = 'Purchase Invoice' and (account = %(account)s or account = %(petty_cash)s)"
				conditions1 = "company=%(company)s and posting_date >= %(from_date)s and posting_date < %(posting_date)s and voucher_type in ('Journal Entry', 'Expense Claim') and (account = %(account)s or account = %(petty_cash)s)"
				query_filters = {
					"company": company,
					"from_date": date['from_date'],
					"posting_date": date['to_date'],
					"account": account,
					"petty_cash": petty_cash
				}
				insert_data(select_clause, conditions, conditions1, query_filters)

	delete_history_book(company)
	update_open_invoices(company, employee)
	update_debit_notes(company, employee)
	update_ageing_details(company, posting_date, employee)
	update_user_info_status(company, employee)
	# insert_log('ER EMP Summary', company, from_date, posting_date, 'Success', employee, None)
	# email_status(from_date, posting_date, summarize, employee)

def delete_data(company, from_date, posting_date, employee = None):
	conditions = "company = %(company)s and posting_date >= %(from_date)s and posting_date <= %(posting_date)s"
	if employee:
		conditions += "and party = %(employee)s"

	query_filters = {
		"company": company,
		"employee": employee,
		"from_date": from_date,
		"posting_date": posting_date
	}
	
	delete_sales = frappe.db.sql('''
					delete 
					from 
						`tabER EMP Expense Detail`
					where
						{conditions}
					'''.format(conditions=conditions), query_filters)

	delete_jv = frappe.db.sql('''
					delete 
					from 
						`tabER EMP Journal Detail`
					where
						{conditions}
					'''.format(conditions=conditions), query_filters)

	frappe.db.commit()	

def truncate_tables():
	truncate_sales = frappe.db.sql('''
					TRUNCATE TABLE
						`tabER EMP Expense Detail`
				''')

	truncate_journal = frappe.db.sql('''
					TRUNCATE TABLE
						`tabER EMP Journal Detail`
				''')

	frappe.db.commit()

def insert_data(select_clause, conditions, conditions1, query_filters):
	insert_sales = frappe.db.sql('''
				insert into 
					`tabER EMP Expense Detail`
				(name, company, posting_date, finance_book, party_type, party, voucher_type, voucher_no, against_voucher_type, against_voucher, debit, credit, net_amount, paid_amount, status)
				select
					{select_clause}
				from 
					`tabGL Entry` 
				where 
					{conditions}
				'''.format(select_clause = select_clause, conditions=conditions), query_filters)
	frappe.db.commit()

	insert_jv = frappe.db.sql('''
				insert into 
					`tabER EMP Journal Detail`
					(name, company, posting_date, finance_book, party_type, party, voucher_type, voucher_no, against_voucher_type, against_voucher, debit, credit, net_amount, paid_amount, status)
				select
					{select_clause}
				from 
					`tabGL Entry` 
				where 
					{conditions1}
				'''.format(select_clause = select_clause, conditions1=conditions1), query_filters)
	frappe.db.commit()

def delete_history_book(company):
	delete_sales = frappe.db.sql('''
					delete from
						`tabER EMP Expense Detail`
					where
						company = %s
						and finance_book = 'FC_OLD_Then_31Mar2019'
					''',(company))

	delete_jv = frappe.db.sql('''
					delete from
						`tabER EMP Journal Detail`
					where
						company = %s
						and finance_book = 'FC_OLD_Then_31Mar2019'
					''',(company))

	frappe.db.commit()

def update_open_invoices(company, employee=None):
	conditions = "company = %(company)s and status = 'Open'"
	if employee:
		conditions += "and party = %(employee)s"

	query_filters = {
		"company": company,
		"employee": employee
	}
	update_purchase = frappe.db.sql('''
					update
						`tabER EMP Expense Detail` sales
					set sales.paid_amount = ifnull((
						select 
							sum(jv.debit - jv.credit)
						from
							`tabER EMP Journal Detail` jv
						where
							sales.status = 'Open' and
							sales.voucher_type = jv.against_voucher_type and
							sales.voucher_no = jv.against_voucher
						), 0)
					where {conditions}
						and exists
						(select 
							'X'
						from
							`tabER EMP Journal Detail` jd
						where
							jd.status = 'Open' and
							sales.voucher_type = jd.against_voucher_type and
							sales.voucher_no = jd.against_voucher
						)
					'''.format(conditions=conditions), query_filters)

	update_status = frappe.db.sql('''
					update
						`tabER EMP Expense Detail`
					set 
						status = 'Closed'
					where
						{conditions}
						and net_amount + paid_amount = 0
					'''.format(conditions=conditions), query_filters)
	frappe.db.commit()

	update_payments = frappe.db.sql('''
					update
						`tabER EMP Journal Detail` jv
					set 
						status = 'Closed'
					where 
						{conditions}
						and exists
						(select 
							'X'
						from
							`tabER EMP Expense Detail` sales
						where
							sales.voucher_type = jv.against_voucher_type and
							sales.voucher_no = jv.against_voucher
						)
					'''.format(conditions=conditions), query_filters)
	frappe.db.commit()

#change this method to debit notes
def update_debit_notes(company, employee=None):
	conditions = "company = %(company)s and status = 'Open' and net_amount > 0 and voucher_no != against_voucher and against_voucher IS NOT NULL"
	conditions1 = "company = %(company)s and status = 'Open' and net_amount + paid_amount = 0"
	if employee:
		conditions += " and party = %(employee)s"
		conditions1 += " and party = %(employee)s"

	query_filters = {
		"company": company,
		"employee": employee
	}

	open_dn_notes = frappe.db.sql('''
						select
							a.against_voucher as purchase_inv_no, a.voucher_no as debit_inv_no,
							a.net_amount as dn_amount
						from
							`tabER EMP Expense Detail` a
						where
							{conditions}
							and exists
							(select
								'X'
							from
								`tabER EMP Expense Detail` b
							where a.against_voucher = b.voucher_no
							and b.status = 'Open')
						order by
							purchase_inv_no
						'''.format(conditions=conditions), query_filters, as_dict=1)

	#Close applied debit notes
	for dn_no in open_dn_notes:
		#update paid amount
		frappe.db.sql('''
			update
				`tabER EMP Expense Detail`
			set
				paid_amount = paid_amount + %s
			where
				voucher_type = 'Purchase Invoice' and
				voucher_no = %s and
				status = 'Open'
			''', (dn_no['dn_amount'], dn_no['purchase_inv_no']))
		#update closed debit notes
		frappe.db.sql('''
			update
				`tabER EMP Expense Detail`
			set
				status = 'Closed'
			where
				voucher_type = 'Purchase Invoice' and
				voucher_no = %s and
				status = 'Open'
			''', (dn_no['debit_inv_no']))
	#close out invoices
	update_status = frappe.db.sql('''
					update
						`tabER EMP Expense Detail`
					set 
						status = 'Closed'
					where
						{conditions1}
					'''.format(conditions1=conditions1), query_filters)
	frappe.db.commit()

def update_ageing_details(company, posting_date, employee=None):
	due_date_conditions = "company = %(company)s and status = 'Open' and net_amount < 0 and due_date IS NOT NULL and due_date <= %(posting_date)s"
	posting_date_conditions = "company = %(company)s and status = 'Open' and posting_date <= %(posting_date)s"
	due_date_set = "age_days = DATEDIFF(%(as_of_date)s, due_date)"
	posting_date_set = "age_days_1 = DATEDIFF(%(as_of_date)s, posting_date)"

	if employee:
		due_date_conditions += "and party = %(employee)s"
		posting_date_conditions += "and party = %(employee)s"

	query_filters = {
		"company": company,
		"posting_date": posting_date,
		"employee": employee,
		"as_of_date": posting_date
	}

	update_sales_details = frappe.db.sql('''
								update 
									`tabER EMP Expense Detail` purchase, `tabPurchase Invoice` si
								set 
									purchase.due_date = ifnull(si.due_date,0), purchase.project = ifnull(si.project,'')
								where
									purchase.status = 'Open' and
									purchase.voucher_type = 'Purchase Invoice' and
									purchase.voucher_no = si.name
								''')
	#due date
	update_age_days = frappe.db.sql('''
					update
						`tabER EMP Expense Detail`
					set 
						{due_date_set}
					where
						{due_date_conditions}
					'''.format(due_date_set=due_date_set, due_date_conditions=due_date_conditions), query_filters)
	frappe.db.commit()
	#posting date
	update_age_days = frappe.db.sql('''
					update
						`tabER EMP Expense Detail`
					set 
						{posting_date_set}
					where
						{posting_date_conditions}
					'''.format(posting_date_set=posting_date_set, posting_date_conditions=posting_date_conditions),query_filters)
	frappe.db.commit()

def update_user_info_status(company, employee):
	conditions = "company = %(company)s"
	if employee:
		conditions += "and party = %(employee)s"

	query_filters = {
		"company": company,
		"employee": employee
	}

	update_sales = frappe.db.sql('''
				update
					`tabER EMP Expense Detail`
				set 
					owner = 'Administrator', creation = addtime(now(),'05:30:00.000000'), modified = addtime(now(),'05:30:00.000000'), modified_by = 'Administrator'
				where
					{conditions}
				'''.format(conditions=conditions), query_filters)

	update_journal = frappe.db.sql('''
				update
					`tabER EMP Journal Detail`
				set 
					owner = 'Administrator', creation = addtime(now(),'05:30:00.000000'), modified = addtime(now(),'05:30:00.000000'), modified_by = 'Administrator'
				where
					{conditions}
				'''.format(conditions=conditions), query_filters)

	update_status = frappe.db.sql('''
				update
					`tabSingles`
				set
					value = "Success"
				where
					doctype = 'ER EMP Summary Settings'
					and field = 'status'
				''')

	update_last_run = frappe.db.sql('''
				update
					`tabSingles`
				set
					value = addtime(now(),'05:30:00.000000')
				where
					doctype = 'ER EMP Summary Settings'
					and field = 'last_run_on'
				''')

def date_interval(start_date, end_date):
	date_list = []
	reference_date = start_date
	while reference_date <= end_date:
		from_date = reference_date
		reference_date = add_days(reference_date, 30)
		if reference_date > end_date:
			date_list.append({'from_date': from_date, 'to_date': end_date})
		else:
			date_list.append({'from_date': from_date, 'to_date': reference_date})

	return date_list

def email_status(from_date, posting_date, summarize, employee):
	sender_email = frappe.db.get_value("Email Account",'Matrix Action Alerts', "email_id")
	if not employee:
		supp_value = " "
	else:
		supp_value = employee
	msg = "Hi, <br><br>EMP Summary process has completed running for below settings: <br> Start Date: %s <br> End Date: %s <br> employee: %s / %s"%(formatdate(from_date), formatdate(posting_date), summarize, supp_value)
	sub = "EMP Summary process has completed running for %s to %s"%(formatdate(from_date), formatdate(posting_date))
	frappe.sendmail(sender = sender_email, recipients = 'matrix_team@elastic.run', subject = sub, content = msg)
