frappe.ui.form.on("Purchase Order", {
    refresh(frm) {
        if (frm.doc.docstatus === 1) {
            frm.add_custom_button(__("Shipment Tracking"), function () {
                frappe.new_doc("Shipment Tracking", {
                    supplier: frm.doc.supplier,
                    purchase_order: frm.doc.name,
                    incoterm: "CIF"
                });
            }, __("Create"));
        }
    }
});