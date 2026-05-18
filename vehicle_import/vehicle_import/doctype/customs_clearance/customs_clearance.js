frappe.ui.form.on("Customs Clearance", {
    refresh(frm) {
        if (frm.doc.total_clearance_cost) {
            frm.dashboard.set_headline(__("Total: " + format_currency(frm.doc.total_clearance_cost)));
        }

        if (frm.is_new() === false && frm.doc.status !== "Released") {
            frm.add_custom_button(__("Next Clearance Step"), function () {
                move_to_next_clearance_step(frm);
            }).css({"background-color": "#17a2b8", "color": "white", "font-weight": "bold"});
        }
    },

    shipment(frm) {
        if (frm.doc.shipment) {
            frappe.db.get_doc("Shipment Tracking", frm.doc.shipment).then(s => {
                if (s.vehicles && s.vehicles.length > 0 && frm.doc.vehicle === undefined) {
                    frm.set_value("vehicle", s.vehicles[0].vehicle);
                }
            });
        }
    },

    vehicle(frm) {
        if (frm.doc.vehicle) {
            frappe.db.get_doc("Vehicle", frm.doc.vehicle).then(v => {
                frm.set_value("vehicle_description", v.year + " " + v.make + " " + v.model + " - VIN: " + (v.vin || "N/A"));
                
                if (frm.doc.customs_duty === undefined && v.customs) {
                    frm.set_value("customs_duty", v.customs * 0.4);
                    frm.set_value("excise_duty", v.customs * 0.2);
                    frm.set_value("import_vat", v.customs * 0.4);
                }
            });
        }
    },

    customs_duty: function(frm) { calc_total(frm); },
    excise_duty: function(frm) { calc_total(frm); },
    import_vat: function(frm) { calc_total(frm); },
    port_charges: function(frm) { calc_total(frm); },
    clearing_agent_fee: function(frm) { calc_total(frm); },
    transport_to_yard: function(frm) { calc_total(frm); },
    other_charges: function(frm) { calc_total(frm); }
});

function calc_total(frm) {
    frm.set_value("total_clearance_cost",
        flt(frm.doc.customs_duty) + flt(frm.doc.excise_duty) + flt(frm.doc.import_vat) +
        flt(frm.doc.port_charges) + flt(frm.doc.clearing_agent_fee) +
        flt(frm.doc.transport_to_yard) + flt(frm.doc.other_charges)
    );
}

function move_to_next_clearance_step(frm) {
    const steps = ["Pending", "Documents Submitted", "Assessment", "Duty Paid", "Cleared", "Released"];
    const current_idx = steps.indexOf(frm.doc.status);
    
    if (current_idx >= 0 && current_idx < steps.length - 1) {
        let next_status = steps[current_idx + 1];
        
        frappe.prompt([
            {
                fieldtype: "Select",
                label: "New Status",
                fieldname: "new_status",
                options: steps.slice(current_idx + 1).join("\n"),
                default: next_status,
                reqd: 1
            },
            {
                fieldtype: "Small Text",
                label: "Notes",
                fieldname: "notes"
            }
        ], function(values) {
            frm.set_value("status", values.new_status);
            if (values.notes) {
                frm.set_value("notes", (frm.doc.notes || "") + "\n" + frappe.datetime.now_datetime() + ": " + values.notes);
            }
            frm.save();
        }, "Update Clearance Status");
    }
}