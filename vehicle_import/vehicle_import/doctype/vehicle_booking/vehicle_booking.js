frappe.ui.form.on("Vehicle Booking", {
    refresh(frm) {
        show_business_dashboard(frm);
        
        if (frm.doc.order_type === "Ready Stock") {
            show_ready_stock_buttons(frm);
        } else {
            show_import_demand_buttons(frm);
        }
    },

    vehicle(frm) {
        if (frm.doc.vehicle) {
            // Wait for fetch to complete, then recalculate
            setTimeout(function() {
                calculate_all_totals(frm);
            }, 1000);
        }
    },

    // Recalculate when any field changes
    estimated_cif(frm) { calculate_all_totals(frm); },
    estimated_customs(frm) { calculate_all_totals(frm); },
    estimated_other_charges(frm) { calculate_all_totals(frm); },
    selling_price(frm) { calculate_all_totals(frm); },
    advance_type(frm) { calculate_all_totals(frm); },
    
    // Allow manual advance amount input but validate minimum
    advance_amount(frm) {
        validate_advance_amount(frm);
    }
});

function calculate_all_totals(frm) {
    // Calculate estimated total costs
    let total_costs = flt(frm.doc.estimated_cif) + flt(frm.doc.estimated_customs) + flt(frm.doc.estimated_other_charges);
    frm.set_value("estimated_total_costs", total_costs);
    
    // Auto-calculate advance based on advance type
    let cif = flt(frm.doc.estimated_cif);
    let selling_price = flt(frm.doc.selling_price);
    
    if (cif > 0 && selling_price > 0 && frm.doc.advance_type) {
        let advance_amount, advance_percentage;
        
        if (frm.doc.advance_type === "CIF") {
            // Use full CIF as advance
            advance_amount = cif;
        } else if (frm.doc.advance_type === "50% of CIF") {
            // Use 50% of CIF as advance
            advance_amount = cif * 0.5;
        }
        
        advance_percentage = (advance_amount / selling_price) * 100;
        
        frm.set_value("advance_amount", advance_amount);
        frm.set_value("advance_percentage", advance_percentage);
        
        // Show info message
        frappe.show_alert({
            message: `Minimum advance: ${format_currency(advance_amount)} (${frm.doc.advance_type}). Customer can pay more.`,
            indicator: 'blue'
        });
    }
}

function validate_advance_amount(frm) {
    if (!frm.doc.estimated_cif || !frm.doc.advance_type) return;
    
    let cif = flt(frm.doc.estimated_cif);
    let min_advance = frm.doc.advance_type === "CIF" ? cif : cif * 0.5;
    let entered_advance = flt(frm.doc.advance_amount);
    
    if (entered_advance < min_advance) {
        frappe.msgprint({
            title: "Minimum Advance Required",
            message: `Minimum advance is ${format_currency(min_advance)} based on ${frm.doc.advance_type}. You entered ${format_currency(entered_advance)}.`,
            indicator: "red"
        });
        frm.set_value("advance_amount", min_advance);
    } else if (entered_advance > min_advance) {
        frappe.show_alert({
            message: `✅ Customer paying ${format_currency(entered_advance - min_advance)} above minimum`,
            indicator: 'green'
        });
    }
    
    // Recalculate percentage
    if (frm.doc.selling_price) {
        let percentage = (entered_advance / flt(frm.doc.selling_price)) * 100;
        frm.set_value("advance_percentage", percentage);
    }
}

function show_business_dashboard(frm) {
    if (frm.doc.order_type === "Ready Stock") {
        frm.dashboard.set_headline(__("Ready Stock Sale: Vehicle Available"), "green");
    } else {
        frm.dashboard.set_headline(__("Import on Demand: Will Order Vehicle"), "blue");
    }
}

function show_ready_stock_buttons(frm) {
    if (frm.doc.status === "Payment Confirmation" && frm.doc.total_paid >= frm.doc.selling_price) {
        frm.add_custom_button(__("Complete Sale"), function() {
            frm.set_value("status", "Delivery");
            frm.save();
        }).css({"background-color": "#28a745", "color": "white"});
    }
}

function show_import_demand_buttons(frm) {
    const import_steps = ["Draft", "Payment Confirmation", "Vehicle Inspection", "Shipment Schedule (Prospective)", "Loading Confirmation", "Vessel Arrival Notice", "Offloading and Dryport then Arrival Confirmation", "Delivery"];
    
    if (frm.doc.status !== "Delivery" && frm.doc.status !== "Cancelled") {
        frm.add_custom_button(__("Next Import Step"), function() {
            let current_idx = import_steps.indexOf(frm.doc.status);
            if (current_idx >= 0 && current_idx < import_steps.length - 1) {
                frm.set_value("status", import_steps[current_idx + 1]);
                frm.save();
            }
        }).css({"background-color": "#007bff", "color": "white"});
    }
}
