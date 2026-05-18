import frappe
from frappe.model.document import Document
from frappe.utils import today

class ShipmentTracking(Document):
    def validate(self):
        self.total_vehicles = len(self.vehicles or [])

    @frappe.whitelist()
    def move_to_next_step(self):
        steps = [
            'Shipment Schedule (Prospective)',
            'Loading Confirmation',
            'In Transit',
            'Vessel Arrival Notice',
            'Offloading and Dryport then Arrival Confirmation',
            'Delivery',
            'Completed'
        ]

        if self.status not in steps:
            self.status = steps[0]
        else:
            idx = steps.index(self.status)
            if idx < len(steps) - 1:
                self.status = steps[idx + 1]

        if self.status == 'Vessel Arrival Notice' and not self.actual_arrival_date:
            self.actual_arrival_date = today()

        self.save(ignore_permissions=True)
        frappe.db.commit()
        return self.status
