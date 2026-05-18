import frappe
from frappe.utils import flt, nowdate
from frappe import _

class VehicleImportAccounting:
    """Handles all accounting entries for Vehicle Import module"""
    
    ACCOUNT_MAP = {
        "vehicle_inventory": "Vehicle Inventory - RL",
        "vehicles_in_transit": "Vehicles in Transit - RL",
        "vehicle_sales": "Vehicle Sales - RL",
        "vehicle_cogs": "Vehicle Cost of Goods Sold - RL",
        "import_duties": "Import Duties and Taxes - RL",
        "shipping_freight": "Shipping and Freight - RL",
        "clearing_fees": "Clearing Agent Fees - RL",
        "port_charges": "Port and Transport Charges - RL",
        "customer_advances": "Customer Advances Vehicles - RL"
    }
    
    @staticmethod
    def get_account(account_key):
        """Get account name from map"""
        account = VehicleImportAccounting.ACCOUNT_MAP.get(account_key)
        if not frappe.db.exists("Account", account):
            frappe.throw(f"Account '{account}' not found. Please create it first.")
        return account
    
    @staticmethod
    def create_vehicle_receipt_je(vehicle):
        """Create JE when vehicle is created - Record in Vehicles in Transit"""
        if not vehicle.cif:
            return
        
        try:
            company = frappe.db.get_value("Company", {"default": 1}, "name")
            
            je = frappe.new_doc("Journal Entry")
            je.company = company
            je.posting_date = nowdate()
            je.doctype = "Journal Entry"
            je.reference_doctype = "Vehicle"
            je.reference_name = vehicle.name
            je.title = f"Vehicle Receipt: {vehicle.custom_full_title}"
            
            # DR: Vehicles in Transit
            je.append("accounts", {
                "account": VehicleImportAccounting.get_account("vehicles_in_transit"),
                "debit": flt(vehicle.cif),
                "debit_in_account_currency": flt(vehicle.cif)
            })
            
            # CR: Accounts Payable (use default payable account)
            payable_account = frappe.db.get_single_value("Accounts Settings", "default_payable_account")
            if not payable_account:
                payable_account = frappe.db.get_value("Account", 
                    {"company": company, "account_name": ["like", "%Payable%"], "is_group": 0}, 
                    "name")
            
            je.append("accounts", {
                "account": payable_account,
                "credit": flt(vehicle.cif),
                "credit_in_account_currency": flt(vehicle.cif)
            })
            
            je.insert(ignore_permissions=True)
            frappe.msgprint(f"✅ Journal Entry created: {je.name}", alert=True, indicator="green")
            
        except Exception as e:
            frappe.log_error(title="Vehicle Receipt JE Failed", message=str(e))
    
    @staticmethod
    def create_customs_clearance_je(customs_clearance):
        """Create JE for customs duties and clearing expenses"""
        if not customs_clearance.total_clearance_cost or customs_clearance.total_clearance_cost == 0:
            return
        
        try:
            company = frappe.db.get_value("Company", {"default": 1}, "name")
            
            je = frappe.new_doc("Journal Entry")
            je.company = company
            je.posting_date = nowdate()
            je.doctype = "Journal Entry"
            je.reference_doctype = "Customs Clearance"
            je.reference_name = customs_clearance.name
            je.title = f"Customs Clearance: {customs_clearance.name}"
            
            # DR: Import Duties and Taxes
            if customs_clearance.customs_duty + customs_clearance.excise_duty + customs_clearance.import_vat > 0:
                je.append("accounts", {
                    "account": VehicleImportAccounting.get_account("import_duties"),
                    "debit": flt(customs_clearance.customs_duty + customs_clearance.excise_duty + customs_clearance.import_vat),
                    "debit_in_account_currency": flt(customs_clearance.customs_duty + customs_clearance.excise_duty + customs_clearance.import_vat)
                })
            
            # DR: Clearing Agent Fees
            if customs_clearance.clearing_agent_fee > 0:
                je.append("accounts", {
                    "account": VehicleImportAccounting.get_account("clearing_fees"),
                    "debit": flt(customs_clearance.clearing_agent_fee),
                    "debit_in_account_currency": flt(customs_clearance.clearing_agent_fee)
                })
            
            # DR: Port and Transport Charges
            if customs_clearance.port_charges + customs_clearance.transport_to_yard > 0:
                je.append("accounts", {
                    "account": VehicleImportAccounting.get_account("port_charges"),
                    "debit": flt(customs_clearance.port_charges + customs_clearance.transport_to_yard),
                    "debit_in_account_currency": flt(customs_clearance.port_charges + customs_clearance.transport_to_yard)
                })
            
            # CR: Cash/Bank Account
            cash_account = frappe.db.get_single_value("Accounts Settings", "default_cash_account")
            if not cash_account:
                cash_account = frappe.db.get_value("Account",
                    {"company": company, "account_name": ["like", "%Cash%"], "is_group": 0},
                    "name")
            
            je.append("accounts", {
                "account": cash_account,
                "credit": flt(customs_clearance.total_clearance_cost),
                "credit_in_account_currency": flt(customs_clearance.total_clearance_cost)
            })
            
            je.insert(ignore_permissions=True)
            frappe.msgprint(f"✅ Customs JE created: {je.name}", alert=True, indicator="green")
            
        except Exception as e:
            frappe.log_error(title="Customs Clearance JE Failed", message=str(e))
    
    @staticmethod
    def create_vehicle_booking_advance_je(vehicle_booking):
        """Create JE for customer advance payment"""
        if not vehicle_booking.advance_amount or vehicle_booking.advance_amount == 0:
            return
        
        try:
            company = frappe.db.get_value("Company", {"default": 1}, "name")
            
            je = frappe.new_doc("Journal Entry")
            je.company = company
            je.posting_date = nowdate()
            je.doctype = "Journal Entry"
            je.reference_doctype = "Vehicle Booking"
            je.reference_name = vehicle_booking.name
            je.title = f"Advance Payment: {vehicle_booking.name}"
            
            # DR: Cash/Bank
            cash_account = frappe.db.get_single_value("Accounts Settings", "default_cash_account")
            if not cash_account:
                cash_account = frappe.db.get_value("Account",
                    {"company": company, "account_name": ["like", "%Cash%"], "is_group": 0},
                    "name")
            
            je.append("accounts", {
                "account": cash_account,
                "debit": flt(vehicle_booking.advance_amount),
                "debit_in_account_currency": flt(vehicle_booking.advance_amount)
            })
            
            # CR: Customer Advances
            je.append("accounts", {
                "account": VehicleImportAccounting.get_account("customer_advances"),
                "credit": flt(vehicle_booking.advance_amount),
                "credit_in_account_currency": flt(vehicle_booking.advance_amount)
            })
            
            je.insert(ignore_permissions=True)
            frappe.msgprint(f"✅ Advance Payment JE created: {je.name}", alert=True, indicator="green")
            
        except Exception as e:
            frappe.log_error(title="Advance Payment JE Failed", message=str(e))
    
    @staticmethod
    def create_vehicle_sale_je(vehicle_booking):
        """Create JE for vehicle sale - Revenue + COGS"""
        if not vehicle_booking.selling_price or vehicle_booking.docstatus != 1:
            return
        
        try:
            company = frappe.db.get_value("Company", {"default": 1}, "name")
            
            # Get customer AR account
            customer = frappe.get_doc("Customer", vehicle_booking.customer)
            ar_account = customer.get("receivable_account") or frappe.db.get_single_value("Accounts Settings", "default_receivable_account")
            
            if not ar_account:
                ar_account = frappe.db.get_value("Account",
                    {"company": company, "account_name": ["like", "%Receivable%"], "is_group": 0},
                    "name")
            
            # 1. REVENUE RECOGNITION JE
            je_revenue = frappe.new_doc("Journal Entry")
            je_revenue.company = company
            je_revenue.posting_date = nowdate()
            je_revenue.title = f"Vehicle Sale - Revenue: {vehicle_booking.name}"
            je_revenue.reference_doctype = "Vehicle Booking"
            je_revenue.reference_name = vehicle_booking.name
            
            # DR: Accounts Receivable
            je_revenue.append("accounts", {
                "account": ar_account,
                "debit": flt(vehicle_booking.selling_price),
                "debit_in_account_currency": flt(vehicle_booking.selling_price)
            })
            
            # CR: Vehicle Sales
            je_revenue.append("accounts", {
                "account": VehicleImportAccounting.get_account("vehicle_sales"),
                "credit": flt(vehicle_booking.selling_price),
                "credit_in_account_currency": flt(vehicle_booking.selling_price)
            })
            
            je_revenue.insert(ignore_permissions=True)
            frappe.msgprint(f"✅ Sales Revenue JE created: {je_revenue.name}", alert=True, indicator="green")
            
            # 2. COGS RECOGNITION JE
            if vehicle_booking.estimated_total_costs > 0:
                je_cogs = frappe.new_doc("Journal Entry")
                je_cogs.company = company
                je_cogs.posting_date = nowdate()
                je_cogs.title = f"Vehicle Sale - COGS: {vehicle_booking.name}"
                je_cogs.reference_doctype = "Vehicle Booking"
                je_cogs.reference_name = vehicle_booking.name
                
                # DR: Vehicle COGS
                je_cogs.append("accounts", {
                    "account": VehicleImportAccounting.get_account("vehicle_cogs"),
                    "debit": flt(vehicle_booking.estimated_total_costs),
                    "debit_in_account_currency": flt(vehicle_booking.estimated_total_costs)
                })
                
                # CR: Vehicle Inventory
                je_cogs.append("accounts", {
                    "account": VehicleImportAccounting.get_account("vehicle_inventory"),
                    "credit": flt(vehicle_booking.estimated_total_costs),
                    "credit_in_account_currency": flt(vehicle_booking.estimated_total_costs)
                })
                
                je_cogs.insert(ignore_permissions=True)
                frappe.msgprint(f"✅ COGS JE created: {je_cogs.name}", alert=True, indicator="green")
            
            # 3. CLEAR ADVANCE JE
            if vehicle_booking.advance_amount > 0:
                je_advance = frappe.new_doc("Journal Entry")
                je_advance.company = company
                je_advance.posting_date = nowdate()
                je_advance.title = f"Clear Advance: {vehicle_booking.name}"
                je_advance.reference_doctype = "Vehicle Booking"
                je_advance.reference_name = vehicle_booking.name
                
                # DR: Customer Advances
                je_advance.append("accounts", {
                    "account": VehicleImportAccounting.get_account("customer_advances"),
                    "debit": flt(vehicle_booking.advance_amount),
                    "debit_in_account_currency": flt(vehicle_booking.advance_amount)
                })
                
                # CR: Accounts Receivable
                je_advance.append("accounts", {
                    "account": ar_account,
                    "credit": flt(vehicle_booking.advance_amount),
                    "credit_in_account_currency": flt(vehicle_booking.advance_amount)
                })
                
                je_advance.insert(ignore_permissions=True)
                frappe.msgprint(f"✅ Advance Clear JE created: {je_advance.name}", alert=True, indicator="green")
            
        except Exception as e:
            frappe.log_error(title="Vehicle Sale JE Failed", message=str(e))
