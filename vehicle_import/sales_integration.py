import frappe

def create_vehicle_booking_from_so(doc, method):
    """Create Vehicle Booking from Sales Order if it contains vehicles"""
    
    # Check if sales order contains vehicle items
    vehicle_items = []
    for item in doc.items:
        if item.item_code and item.item_code.startswith("VEH-"):
            # Find the corresponding vehicle
            vehicle = frappe.db.get_value("Vehicle", {"item_code": item.item_code}, "name")
            if vehicle:
                vehicle_items.append({
                    "vehicle": vehicle,
                    "item_code": item.item_code,
                    "rate": item.rate
                })
    
    # Create Vehicle Booking if vehicles found
    if vehicle_items:
        for v_item in vehicle_items:
            booking = frappe.new_doc("Vehicle Booking")
            booking.customer = doc.customer
            booking.customer_name = doc.customer_name
            booking.sales_order = doc.name
            booking.selling_price = v_item["rate"]
            booking.order_type = "Ready Stock"
            booking.vehicle = v_item["vehicle"]
            
            # Get vehicle details
            vehicle_doc = frappe.get_doc("Vehicle", v_item["vehicle"])
            booking.make = vehicle_doc.make
            booking.model = vehicle_doc.model
            booking.year = vehicle_doc.year
            
            booking.insert(ignore_permissions=True)
            
            frappe.msgprint(f"Vehicle Booking {booking.name} created from Sales Order", 
                           alert=True, indicator="green")
