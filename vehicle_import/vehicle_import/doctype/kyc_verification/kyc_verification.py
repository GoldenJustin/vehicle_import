import frappe
from frappe.model.document import Document
from frappe.utils import today

class KYCVerification(Document):
    def validate(self):
        if self.status == "Rejected" and not self.rejection_reason:
            frappe.throw("Please provide a rejection reason")

    def before_save(self):
        if self.has_value_changed("status"):
            if self.status in ("Verified", "Rejected"):
                self.verification_date = today()
                self.verified_by = frappe.session.user
