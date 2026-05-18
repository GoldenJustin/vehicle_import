frappe.ui.form.on("KYC Verification", {
    refresh(frm) {
        if (frm.doc.status === "Pending" && !frm.is_new()) {
            frm.add_custom_button(__("Approve"), function () {
                frm.set_value("status", "Verified");
                frm.save();
            }, __("Actions"));
            frm.add_custom_button(__("Reject"), function () {
                frappe.prompt({fieldtype: "Small Text", label: "Reason", reqd: 1}, function (values) {
                    frm.set_value("status", "Rejected");
                    frm.set_value("rejection_reason", values.value);
                    frm.save();
                }, __("Rejection Reason"));
            }, __("Actions"));
        }
    }
});