# Copyright (c) 2013, Frappe and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
# from datetime import datetime
# from frappe.model.meta import get_field_precision
from frappe import msgprint,_

def execute(filters=None):
	columns, data = [], []

	columns = [
	# {
	# 	"fieldname":"party_type",
	# 	"label": _("Party Type"),
	# 	"fieldtype": "Link",
	# 	"options":"DocType",
	# 	"width": "80"
	# },
	# {
	# 	"fieldname":"party",
	# 	"label": _("Party"),
	# 	"fieldtype": "Dynamic Link",
	# 	"options":"Customer"
	# },
	{
		"fieldname":"name",
		"label":_("Meeeting"),
		"fieldtype":"Link",
		"options":"Meeeting",
		"width":"120"
	},
	{
		"fieldname":"title",
		"label":_("Title"),
		"fieldtype":"data",
		"width":"120"
	},
	{
		"fieldname":"date",
		"label":_("Date"),
		"fieldtype":"date",
		"width":"120"
	},
	{
		"fieldname":"from_time",
		"label":_("From Time"),
		"fieldtype":"time",
		"width":"120"
	},
	{
		"fieldname":"to_time",
		"label":_("To Time"),
		"fieldtype":"time",
		"width":"120"
	},
	{
		"fieldname":"assigned_to",
		"label":_("Assigned To"),
		"fieldtype":"Link",
		"options":"User",
		"width":"120"
	}	
	]
	data = get_data(filters)
	
	return columns, data
	
def get_data(filters):
	conditions = get_conditions(filters)

	return frappe.db.sql("""
			select 
				a.name,a.title,a.date,a.from_time,a.to_time,b.assigned_to
			from 
				`tabMeeeting` a join `tabMeeeting Minute` b
			where
				b.parent = a.name
			%s """ % conditions,filters, as_dict=1);

def get_conditions(filters):
	conditions = ""

	# if filters.get("from_date"): conditions += "and a.date >= %(from_date)s"

	# if filters.get("to_date"): conditions += "and a.date <= %(to_date)s"

	if filters.get("assigned_to"): conditions += "and b.assigned_to = %(assigned_to)s"

	if filters.get("name"): conditions += "and a.name = %(name)s"

	if filters.get("datedefault"): conditions += "and a.date >= %(datedefault)s"
	return conditions;

