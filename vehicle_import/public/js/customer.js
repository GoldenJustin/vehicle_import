frappe.ui.form.on("Customer", {
    refresh(frm) {
        // Make email field more prominent if it exists
        if (frm.fields_dict.email_id) {
            frm.fields_dict.email_id.df.reqd = 1;  // Make it required
            frm.fields_dict.email_id.df.bold = 1;  // Make it bold
            frm.refresh_field("email_id");
        }
        
        if (!frm.is_new()) {
            // Add Create KYC button
            frm.add_custom_button(__("KYC Verification"), function() {
                frappe.new_doc("KYC Verification", {
                    customer: frm.doc.name,
                    customer_name: frm.doc.customer_name
                });
            }, __("Create"));
            
            // Add Vehicle Booking button  
            frm.add_custom_button(__("Vehicle Booking"), function() {
                frappe.new_doc("Vehicle Booking", {
                    customer: frm.doc.name,
                    customer_name: frm.doc.customer_name
                });
            }, __("Create"));
            
            // Add View KYC button  
            frm.add_custom_button(__("KYC Records"), function() {
                frappe.route_options = {"customer": frm.doc.name};
                frappe.set_route("List", "KYC Verification");
            }, __("View"));
        }
    },
    
    // Validate email format
    email_id(frm) {
        if (frm.doc.email_id && !frappe.utils.validate_type(frm.doc.email_id, "email")) {
            frappe.msgprint("Please enter a valid email address");
            frm.set_value("email_id", "");
        }
    }
});

console.log("✅ Customer Vehicle Import customization loaded");
