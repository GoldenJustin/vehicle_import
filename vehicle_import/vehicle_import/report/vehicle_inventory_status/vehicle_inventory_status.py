import frappe

def execute(filters=None):
    columns = [
        {"label": "Vehicle", "fieldname": "name", "fieldtype": "Link", "options": "Vehicle", "width": 120},
        {"label": "Make", "fieldname": "make", "fieldtype": "Data", "width": 100},
        {"label": "Model", "fieldname": "model", "fieldtype": "Data", "width": 120},
        {"label": "Year", "fieldname": "year", "fieldtype": "Int", "width": 60},
        {"label": "VIN", "fieldname": "vin", "fieldtype": "Data", "width": 180},
        {"label": "Status", "fieldname": "status", "fieldtype": "Data", "width": 100},
        {"label": "Customer", "fieldname": "customer", "fieldtype": "Link", "options": "Customer", "width": 140},
        {"label": "Total Costs", "fieldname": "total_costs", "fieldtype": "Currency", "width": 120},
        {"label": "Selling Price", "fieldname": "selling_price", "fieldtype": "Currency", "width": 120},
        {"label": "Profit", "fieldname": "profit_margin", "fieldtype": "Currency", "width": 100},
    ]
    conditions = ""
    if filters:
        if filters.get("status"):
            conditions += f" AND v.status = %(status)s"
        if filters.get("make"):
            conditions += f" AND v.make = %(make)s"
    data = frappe.db.sql(f"""
        SELECT name, make, model, year, vin, status, customer, total_costs, selling_price, profit_margin
        FROM `tabVehicle` v WHERE 1=1 {conditions} ORDER BY creation DESC
    """, filters, as_dict=True)
    return columns, data