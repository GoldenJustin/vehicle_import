frappe.ui.form.on("Sales Order", {
    refresh(frm) {
        if (frm.doc.docstatus === 1) {
            frm.add_custom_button(__("Vehicle Booking"), function () {
                frappe.new_doc("Vehicle Booking", {
                    customer: frm.doc.customer,
                    sales_order: frm.doc.name,
                    selling_price: frm.doc.grand_total
                });
            }, __("Create"));
        }
    }
});