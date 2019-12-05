from __future__ import unicode_literals
from frappe import _

def get_data():
	return [
		{
			"label": _("Tools"),
			"icon": "octicon octicon-briefcase",
			"items": [
				{
					"type": "doctype",
					"name": "Meeeting",
					"label": _("Meeeting"),
					"description": _("Prepare agenda,invite users and record minutes"),
					"onboard": 1,
				},
			]
		}
	]