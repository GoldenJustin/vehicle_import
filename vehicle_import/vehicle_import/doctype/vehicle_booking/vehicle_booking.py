import frappe
from frappe.model.document import Document
from frappe.utils import flt, add_days, today
from vehicle_import.accounting_integration import VehicleImportAccounting

class VehicleBooking(Document):
    def validate(self):
        self.calculate_totals()
        self.calculate_advance()
        self.create_payment_milestones()
        self.calculate_payment_totals()

    def calculate_totals(self):
        """Calculate estimated total costs"""
        self.estimated_total_costs = (
            flt(self.estimated_cif) + 
            flt(self.estimated_customs) + 
            flt(self.estimated_other_charges)
        )

    def calculate_advance(self):
        """Calculate advance based on selected advance type"""
        cif = flt(self.estimated_cif)
        selling_price = flt(self.selling_price)
        
        if cif > 0 and selling_price > 0:
            if self.advance_type == "CIF":
                self.advance_amount = cif
                self.advance_percentage = (cif / selling_price) * 100
            elif self.advance_type == "50% of CIF":
                self.advance_amount = cif * 0.5
                self.advance_percentage = (cif * 0.5 / selling_price) * 100
            else:
                self.advance_amount = cif
                self.advance_percentage = (cif / selling_price) * 100
        else:
            self.advance_amount = 0
            self.advance_percentage = 0

    def create_payment_milestones(self):
        """Auto-create payment milestones"""
        if not self.selling_price or not self.advance_amount or self.payment_milestones:
            return
            
        selling_price = flt(self.selling_price)
        advance_amount = flt(self.advance_amount)
        balance = selling_price - advance_amount
        
        if self.order_type == "Import on Demand":
            milestones = [
                {"milestone": "Import Advance", "amount": advance_amount, "percentage": (advance_amount / selling_price) * 100, "due_date": add_days(today(), 7), "milestone_status": "Pending"},
                {"milestone": "Final Payment", "amount": balance, "percentage": (balance / selling_price) * 100, "due_date": add_days(today(), 60), "milestone_status": "Pending"}
            ]
        else:
            milestones = [
                {"milestone": "Advance Payment", "amount": advance_amount, "percentage": (advance_amount / selling_price) * 100, "due_date": add_days(today(), 3), "milestone_status": "Pending"},
                {"milestone": "Delivery Payment", "amount": balance, "percentage": (balance / selling_price) * 100, "due_date": add_days(today(), 7), "milestone_status": "Pending"}
            ]
        
        for milestone_data in milestones:
            milestone = self.append("payment_milestones", {})
            milestone.update(milestone_data)

    def calculate_payment_totals(self):
        """Calculate payment totals"""
        total_paid = 0
        if self.payment_milestones:
            for row in self.payment_milestones:
                if row.milestone_status == "Paid":
                    total_paid += flt(row.amount)
                    
        self.total_paid = total_paid
        self.total_balance = flt(self.selling_price) - total_paid
        
        if self.selling_price:
            self.payment_progress = (total_paid / flt(self.selling_price)) * 100
        else:
            self.payment_progress = 0

    def on_submit(self):
        """Create accounting entries when booking is submitted"""
        # Create advance payment JE
        VehicleImportAccounting.create_vehicle_booking_advance_je(self)

    def on_update(self):
        """Send email when status changes"""
        if self.has_value_changed("status") and self.status == "Delivery":
            # Create sale JE when delivered
            VehicleImportAccounting.create_vehicle_sale_je(self)
            
            # Send email
            frappe.enqueue(
                method="vehicle_import.vehicle_import.doctype.vehicle_booking.vehicle_booking.send_status_change_email",
                queue="short",
                timeout=30,
                is_async=False,
                booking_name=self.name,
                new_status=self.status
            )

    def get_customer_email(self):
        """Get customer email"""
        if not self.customer:
            return None
        customer_email = frappe.db.get_value("Customer", self.customer, "email_id")
        if customer_email and customer_email.strip():
            return customer_email.strip()
        return None

@frappe.whitelist()
def send_status_change_email(booking_name, new_status):
    """Send email"""
    try:
        booking = frappe.get_doc("Vehicle Booking", booking_name)
        customer_email = booking.get_customer_email()
        
        if not customer_email:
            return False

        email_templates = {
            "Payment Confirmation": "Vehicle Booking - Payment Confirmation",
            "Vehicle Inspection": "Vehicle Booking - Vehicle Inspection",
            "Shipment Schedule (Prospective)": "Vehicle Booking - Shipment Schedule",
            "Loading Confirmation": "Vehicle Booking - Loading Confirmation",
            "Vessel Arrival Notice": "Vehicle Booking - Vessel Arrival Notice",
            "Offloading and Dryport then Arrival Confirmation": "Vehicle Booking - Offloading Confirmation",
            "Delivery": "Vehicle Booking - Delivery Ready"
        }
        
        template_name = email_templates.get(new_status)
        if not template_name or not frappe.db.exists("Email Template", template_name):
            return False
            
        email_template = frappe.get_doc("Email Template", template_name)
        context = {"doc": booking, "frappe": frappe}
        subject = frappe.render_template(email_template.subject, context)
        message = frappe.render_template(email_template.response, context)
        
        frappe.sendmail(
            recipients=[customer_email],
            subject=subject,
            message=message,
            reference_doctype=booking.doctype,
            reference_name=booking.name,
            now=True
        )
        
        frappe.msgprint(f"📧 Email sent to {customer_email}", alert=True, indicator="green")
        return True
        
    except Exception as e:
        frappe.log_error(title=f"Email Failed", message=str(e))
        return False
