frappe.ui.form.on("Opportunity", {
    refresh(frm) {
        if (frm.doc.status === "Open") {
            frm.add_custom_button(__("Vehicle Booking"), function() {
                frappe.new_doc("Vehicle Booking", {
                    customer: frm.doc.party_name,
                    customer_name: frm.doc.customer_name || frm.doc.party_name
                });
            }, __("Create"));
        }
    }
});