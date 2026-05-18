import frappe
from frappe.utils import today

def create_kyc_verification(doc, method):
    """Auto-create KYC Verification when new customer is created"""
    if doc.customer_type == "Individual":
        kyc = frappe.new_doc("KYC Verification")
        kyc.customer = doc.name
        kyc.customer_name = doc.customer_name
        kyc.insert(ignore_permissions=True)
        
        frappe.msgprint(f"KYC Verification {kyc.name} created automatically", 
                       alert=True, indicator="blue")
