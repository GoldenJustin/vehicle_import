import frappe
from frappe.model.document import Document
from frappe.utils import flt
from vehicle_import.accounting_integration import VehicleImportAccounting

class Vehicle(Document):
    def validate(self):
        self.update_vehicle_title()
        self.calculate_costs_and_profit()

    def after_insert(self):
        if self.vin:
            self.create_stock_item()
        # Create accounting entry for vehicle receipt
        VehicleImportAccounting.create_vehicle_receipt_je(self)

    def update_vehicle_title(self):
        self.vehicle_title = f"{self.year or ''} {self.make or ''} {self.model or ''}".strip()

    def calculate_costs_and_profit(self):
        """Calculate total costs and profit margin"""
        cif = flt(self.cif or 0)
        customs = flt(self.customs or 0) 
        other_charges = flt(self.other_charges or 0)
        selling_price = flt(self.selling_price or 0)
        
        self.total_costs = cif + customs + other_charges
        self.profit_margin = selling_price - self.total_costs

    def create_stock_item(self):
        """Create stock item automatically"""
        if not self.vin:
            return

        item_code = f"VEH-{self.vin}"
        
        if not frappe.db.exists("Item", item_code):
            try:
                item = frappe.new_doc("Item")
                item.item_code = item_code
                item.item_name = self.vehicle_title or f"{self.make} {self.model}"
                item.item_group = "Vehicles"
                item.stock_uom = "Nos"
                item.is_stock_item = 1
                item.maintain_stock = 1
                item.has_serial_no = 1
                item.valuation_rate = flt(self.total_costs)
                item.standard_rate = flt(self.selling_price)
                
                item.insert(ignore_permissions=True)
                self.db_set("item_code", item.name, update_modified=False)
                frappe.msgprint(f"✅ Stock Item created: {item.name}", alert=True, indicator="green")
                
            except Exception as e:
                frappe.msgprint(f"Failed to create stock item: {str(e)}", alert=True, indicator="red")
