# -*- coding: utf-8 -*-
# Copyright (c) 2019, Frappe and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.website.website_generator import WebsiteGenerator
# from frappe.website.website_generator import WebsiteGenerator

class Meeeting(WebsiteGenerator):
# class Meeeting(WebsiteGenerator):
# 	website = frappe._dict(
# 		template = "templates/meeeting.html"
# 		# condition_field = "published",
# 		# page_title_field = "page_name"
# 	)
		
	def validate(self):
		self.page_name = self.name.lower()
		self.validate_attendees()

	def on_update(self):
		self.sync_todos()

	def validate_attendees(self):
		found = []
		for attendee in self.attendees:
			if not attendee.full_name:
				attendee.full_name = get_full_name(attendee.attendee)

			if attendee.attendee in found:
				frappe.throw(_("Attendee {0} entered twice").format(attendee.attendee))

			found.append(attendee.attendee)

	# code for testing and debugging
	def sync_todos(self):
		# todo_added = [minute.todo for minute in self.minutes if minute.todo]
		todos_added = [todo.name for todo in 
			frappe.get_all("ToDo",
				filters={
					"reference_type": self.doctype,
					"reference_name": self.name,
					"assigned_by": ""
				})
			]
		for minute in self.minutes:
			print ('assigned_to', minute.assigned_to)
			if minute.assigned_to and minute.status=="Open":	
				print ('todo', minute.todo)
				if not minute.todo:
					todo = frappe.get_doc({
						"doctype": "ToDo",
						"description": minute.description,
						"reference_type": self.doctype,
						"reference_name": self.name,
						"owner": minute.assigned_to
						})
					todo.insert()

					minute.db_set("todo",todo.name, update_modified = False)

				else:
					todos_added.remove(minute.todo)

			else:
				minute.db_set("todo",None, update_modified = False)

		for todo in todos_added:
			todo = frappe.get_doc("ToDo",todo)
			todo.flags.from_meeeting = True
			todo.delete()
			# frappe.delete_doc("ToDo", todo)

@frappe.whitelist()
def get_full_name(attendee):
	user = frappe.get_doc("User", attendee)

	return " ".join(filter(None, [user.first_name, user.middle_name, user.last_name]))	