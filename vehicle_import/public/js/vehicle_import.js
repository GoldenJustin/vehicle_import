// Force load on page ready
$(document).ready(function() {
    console.log("Vehicle Import JS loading...");
});

// Sales Order - Vehicle Booking
frappe.ui.form.on("Sales Order", {
    refresh(frm) {
        if (frm.doc.docstatus === 1) {
            frm.add_custom_button(__("Vehicle Booking"), function () {
                frappe.new_doc("Vehicle Booking", {
                    customer: frm.doc.customer,
                    sales_order: frm.doc.name,
                    selling_price: frm.doc.grand_total,
                    order_type: "Ready Stock"
                });
            }, __("Create"));
        }
    }
});

// Purchase Order - Shipment Tracking  
frappe.ui.form.on("Purchase Order", {
    refresh(frm) {
        console.log("Purchase Order form loaded, docstatus:", frm.doc.docstatus);
        
        if (frm.doc.docstatus === 1) {
            console.log("Adding Shipment Tracking button...");
            frm.add_custom_button(__("Shipment Tracking"), function () {
                console.log("Creating new Shipment Tracking...");
                frappe.new_doc("Shipment Tracking", {
                    supplier: frm.doc.supplier,
                    purchase_order: frm.doc.name,
                    incoterm: "CIF",
                    port_of_loading: "Yokohama",
                    port_of_discharge: "Dar es Salaam"
                });
            }, __("Create"));
        }
    }
});

console.log("✅ Vehicle Import module loaded successfully");