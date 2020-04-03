// Copyright (c) 2020, Frappe and contributors
// For license information, please see license.txt

frappe.ui.form.on('ER Distance Mapping', {

	//To check for Duplicate Entry
	//---------------------------
	// validate:function(frm){
	// 	frappe.validated = false;
	// 	frappe.call({
	// 	    method:"frappe.client.get_value",
	// 	    args: {
	// 	        doctype:"ER Distance Mapping",
	// 	        filters: {
	// 	            supplier:me.frm.doc.supplier,
	// 	            supplier_address:me.frm.doc.supplier_address,
	// 	            customer:me.frm.doc.customer,
	// 	            customer_address:me.frm.doc.customer_address
	// 	        },
	// 	        fieldname:["distance"]
	// 	    }, 
	// 	    callback: function(r) { 
	// 	        console.log(r);
	// 	        if(r.message){
	// 	        	frappe.throw(__('Duplicate Entry'))
	// 	        } else {
	// 	        	frappe.validated = true;
	// 	        }
	// 	    }
	// 	})
	// },

	// //Filter addresses in drop down based on selected supplier
	// //---------------------------------------------------------
	// supplier:function(frm) {
	// 	frm.set_value('supplier_address', '')
	// 	frm.set_value('supplier_address_detailed', '')
	// 	frm.set_query("supplier_address", function() {
	// 		return {
	// 			filters: [
	// 				["Dynamic Link","link_doctype","=","Supplier"],
	// 				["Dynamic Link","link_name","=",me.frm.doc.supplier],
	// 			]
	// 		}
	// 	});
	// },

	// //To display detailed address of supplier
	// //--------------------------------------
	// supplier_address:function(frm){
	// 	frm.set_value('supplier_address_detailed', '')
	// 	if(!frm.doc.supplier) {
	// 		frappe.throw(__('Please set Supplier'));
	// 	} else {
	// 		frappe.call({
	// 			method: "frappe.contacts.doctype.address.address.get_address_display",
	// 			args: {"address_dict": frm.doc["supplier_address"] || ''},
	// 			callback: function(r) {
	// 				if(r.message) {
	// 					frm.set_value('supplier_address_detailed', r.message)
	// 				}
	// 			}
	// 		})
	// 	}
	// },

	// //Filter addresses in drop down based on selected customer
	// //---------------------------------------------------------
	// customer:function(frm) {
	// 	frm.set_value('customer_address', '')
	// 	frm.set_value('customer_address_detailed', '')
	// 	frm.set_query("customer_address", function() {
	// 		return {
	// 			filters: [
	// 				["Dynamic Link","link_doctype","=","Customer"],
	// 				["Dynamic Link","link_name","=",me.frm.doc.customer],
	// 			]
	// 		}
	// 	});
	// },

	// //To display detailed address of customer
	// //--------------------------------------
	// customer_address:function(frm){
	// 	frm.set_value('customer_address_detailed', '')
	// 	if(!frm.doc.customer) {
	// 		frappe.throw(__('Please set Customer'));
	// 	} else {
	// 		frappe.call({
	// 			method: "frappe.contacts.doctype.address.address.get_address_display",
	// 			args: {"address_dict": frm.doc['customer_address'] || undefined },
	// 			callback: function(r) {
	// 				if(r.message) {
	// 					frm.set_value('customer_address_detailed', r.message)
	// 				}
	// 			}
	// 		})
	// 	}
	// }
});
