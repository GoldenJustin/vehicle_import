frappe.ui.form.on("Shipment Tracking", {
    refresh(frm) {
        show_shipment_progress(frm);

        if (frm.is_new() === false && frm.doc.status !== "Completed" && frm.doc.status !== "Cancelled") {
            frm.add_custom_button(__("Next Shipment Step"), function () {
                frm.call("move_to_next_step").then(() => {
                    frm.reload_doc();
                    frappe.show_alert({message: "Status updated successfully", indicator: "green"});
                });
            }).css({"background-color": "#007bff", "color": "white", "font-weight": "bold"});
        }

        if (frm.is_new() === false && frm.doc.status === "Offloading and Dryport then Arrival Confirmation") {
            frm.add_custom_button(__("Create Customs Clearance"), function () {
                create_customs_clearance(frm);
            }, __("Create")).css({"background-color": "#ffc107", "color": "black"});
        }
    }
});

function show_shipment_progress(frm) {
    if (frm.doc.eta && ["Delivery", "Completed", "Cancelled"].includes(frm.doc.status) === false) {
        let days = frappe.datetime.get_diff(frm.doc.eta, frappe.datetime.get_today());
        if (days > 0) {
            frm.dashboard.set_headline(__("<strong>" + days + " days</strong> until arrival"));
        } else if (days === 0) {
            frm.dashboard.set_headline(__("Arriving TODAY!"), "green");
        } else {
            frm.dashboard.set_headline(__(Math.abs(days) + " days overdue"), "red");
        }
    }

    frm.page.set_indicator(frm.doc.status, {
        "Shipment Schedule (Prospective)": "orange",
        "Loading Confirmation": "blue",
        "In Transit": "blue",
        "Vessel Arrival Notice": "purple",
        "Offloading and Dryport then Arrival Confirmation": "yellow",
        "Delivery": "green",
        "Completed": "green",
        "Cancelled": "red"
    }[frm.doc.status] || "grey");
}

function create_customs_clearance(frm) {
    if (frm.doc.vehicles === undefined || frm.doc.vehicles.length === 0) {
        frappe.msgprint("No vehicles in this shipment");
        return;
    }

    let vehicle = frm.doc.vehicles[0].vehicle;
    
    frappe.new_doc("Customs Clearance", {
        shipment: frm.doc.name,
        vehicle: vehicle
    });
}