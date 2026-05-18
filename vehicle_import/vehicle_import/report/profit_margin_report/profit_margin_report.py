import frappe
from frappe.utils import flt

def execute(filters=None):
    columns = [
        {"label": "Vehicle", "fieldname": "name", "fieldtype": "Link", "options": "Vehicle", "width": 120},
        {"label": "Description", "fieldname": "description", "fieldtype": "Data", "width": 220},
        {"label": "Customer", "fieldname": "customer", "fieldtype": "Link", "options": "Customer", "width": 140},
        {"label": "CIF", "fieldname": "cif", "fieldtype": "Currency", "width": 120},
        {"label": "Customs", "fieldname": "customs", "fieldtype": "Currency", "width": 120},
        {"label": "Other Charges", "fieldname": "other_charges", "fieldtype": "Currency", "width": 130},
        {"label": "Total Costs", "fieldname": "total_costs", "fieldtype": "Currency", "width": 130},
        {"label": "Selling Price", "fieldname": "selling_price", "fieldtype": "Currency", "width": 130},
        {"label": "Profit", "fieldname": "profit", "fieldtype": "Currency", "width": 120},
        {"label": "Margin %", "fieldname": "margin_pct", "fieldtype": "Percent", "width": 90}
    ]

    data = frappe.db.sql("""
        SELECT
            name,
            CONCAT(COALESCE(year, ''), ' ', COALESCE(make, ''), ' ', COALESCE(model, '')) as description,
            customer,
            cif,
            customs,
            other_charges,
            total_costs,
            selling_price,
            profit_margin as profit,
            CASE 
                WHEN selling_price > 0 THEN (profit_margin / selling_price) * 100
                ELSE 0 
            END as margin_pct
        FROM `tabVehicle`
        WHERE status IN ('Sold', 'Delivered')
        ORDER BY creation DESC
    """, as_dict=True)

    return columns, data