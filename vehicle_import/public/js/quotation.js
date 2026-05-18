frappe.ui.form.on("Quotation", {
    refresh(frm) {
        if (frm.doc.docstatus === 1 && frm.doc.status === "Open") {
            frm.add_custom_button(__("Vehicle Booking"), function() {
                // Check if quotation has vehicle items
                let has_vehicle_items = false;
                let vehicle_item = null;
                
                if (frm.doc.items) {
                    for (let item of frm.doc.items) {
                        if (item.item_code && item.item_code.startsWith("VEH-")) {
                            has_vehicle_items = true;
                            vehicle_item = item;
                            break;
                        }
                    }
                }
                
                if (has_vehicle_items) {
                    // Find the vehicle from item code
                    frappe.db.get_value("Vehicle", {"item_code": vehicle_item.item_code}, "name")
                    .then(r => {
                        if (r.message.name) {
                            // Create with specific vehicle
                            frappe.new_doc("Vehicle Booking", {
                                customer: frm.doc.party_name,
                                customer_name: frm.doc.customer_name || frm.doc.party_name,
                                quotation: frm.doc.name,
                                vehicle: r.message.name,
                                selling_price: vehicle_item.rate,
                                order_type: "Import on Demand"
                            });
                        } else {
                            create_generic_booking(frm);
                        }
                    });
                } else {
                    create_generic_booking(frm);
                }
            }, __("Create"));
        }
    }
});

function create_generic_booking(frm) {
    // Create generic booking without specific vehicle
    frappe.new_doc("Vehicle Booking", {
        customer: frm.doc.party_name,
        customer_name: frm.doc.customer_name || frm.doc.party_name,
        quotation: frm.doc.name,
        selling_price: frm.doc.grand_total,
        order_type: "Import on Demand"
    });
}
