frappe.query_reports["Vehicle Inventory Status"] = {
    filters: [
        {fieldname: "status", label: __("Status"), fieldtype: "Select", options: "\nOrdered\nIn Transit\nAt Port\nAt Customs\nIn Stock\nReserved\nSold\nDelivered"},
        {fieldname: "make", label: __("Make"), fieldtype: "Data"}
    ]
};