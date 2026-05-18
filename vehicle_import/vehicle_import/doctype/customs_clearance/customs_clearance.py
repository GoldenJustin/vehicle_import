import frappe
from frappe.model.document import Document
from frappe.utils import flt
from vehicle_import.accounting_integration import VehicleImportAccounting

class CustomsClearance(Document):
    def validate(self):
        self.calculate_total()

    def on_submit(self):
        # Create accounting entry for customs clearance
        VehicleImportAccounting.create_customs_clearance_je(self)

    def calculate_total(self):
        self.total_clearance_cost = (
            flt(self.customs_duty) +
            flt(self.excise_duty) +
            flt(self.import_vat) +
            flt(self.port_charges) +
            flt(self.clearing_agent_fee) +
            flt(self.transport_to_yard) +
            flt(self.other_charges)
        )
