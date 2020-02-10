# -*- coding: utf-8 -*-
# Copyright (c) 2019, Frappe and Contributors
# See license.txt
from __future__ import unicode_literals

import frappe
import unittest
#
#
#

class TestMeeeting(unittest.TestCase):
	# pass
	def test_sync_todos(self):
		meeeting = make_meeeting()

		todos = get_todos(meeeting)

		self.assertEquals(todos[0].name, meeeting.minutes[0].todo)
		self.assertEquals(todos[0].description, meeeting.minutes[0].description)

	def test_sync_todos_remove(self):
		meeeting = make_meeeting()

		meeeting.minutes[0].status = "Closed"
		meeeting.save()

		todos = get_todos(meeeting)

		self.assertEquals(len(todos),0)

	def test_sync_todos_on_close_todos(self):
		meeeting = make_meeeting()

		todos = get_todos(meeeting)
		todo = frappe.get_doc("ToDo", todos[0].name)
		todo.status = "Closed"
		todo.save()

		meeeting.reload()
		self.assertEquals(meeeting.minutes[0].status, "Closed")
		self.assertFalse(meeeting.minutes[0].todo)

	def test_sync_todos_on_delete_todos(self):
		meeeting = make_meeeting()

		todos = get_todos(meeeting)
		todo = frappe.get_doc("ToDo", todos[0].name)
		todo.delete()

		meeeting.reload()
		self.assertEquals(meeeting.minutes[0].status, "Closed")
		self.assertFalse(meeeting.minutes[0].todo)


def make_meeeting():
	meeeting =  frappe.get_doc({
		"doctype" : "Meeeting",
		"title" : "Test Meeeting",
		"status" : "Planned",
		"date": "2019-01-01",
		"from_time": "09:00",
		"to_time": "10:00",
		"minutes": [
			{
				"description": "Test Minute 1",
				"status": "Open",
				"assigned_to": "neha@gmail.com",
				"complete_by": "2019-02-02"
			}
		],
		"attendees": [
			{
				"attendee": "sneha@gmail.com"
			}
		]
	})
	meeeting.insert()
	return meeeting

def get_todos(meeeting):
	return frappe.get_all("ToDo", 
		filters = {
		"reference_type": meeeting.doctype,
		"reference_name": meeeting.name,
		"owner": "neha@gmail.com"
		},
		fields = ["name","description"])