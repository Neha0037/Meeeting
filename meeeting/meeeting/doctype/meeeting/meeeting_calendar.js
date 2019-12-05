frappe.views.calendar["Meeeting"] = {
	field_map: {
		"start": "start",
		"end": "end",
		"from_time": "from_time",
		"to_time": "to_time",
		"id" : "name",
		"title": "title",
		"status": "status"
	},
	// options: {
	// 	header: {
	// 		left: 'prev,next today',
	// 		center: 'title',
	// 		right: 'month'
	// 	}
	// },
	get_events_method: "meeeting.api.get_meeetings"
}