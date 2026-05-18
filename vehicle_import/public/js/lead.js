frappe.ui.form.on("Lead", {
    refresh(frm) {
        if (frm.doc.status === "Converted") {
            frm.add_custom_button(__("Vehicle Booking"), function() {
                // Find the converted customer
                frappe.db.get_value("Customer", {"lead_name": frm.doc.name}, "name")
                .then(r => {
                    if (r.message.name) {
                        frappe.new_doc("Vehicle Booking", {
                            customer: r.message.name,
                            customer_name: frm.doc.lead_name
                        });
                    }
                });
            }, __("Create"));
        }
    }
});