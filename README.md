# Vehicle Import Management System

A comprehensive **Vehicle Import & Sales Management** application for ERPNext, designed for businesses that import and sell vehicles.

## Features

### 🚗 Vehicle Management
- Complete vehicle records with VIN, make, model, year
- Automatic stock item creation
- Vehicle specifications tracking (engine, transmission, colors)
- Cost tracking (CIF, customs, other charges)
- Profit margin calculations
- Automatic accounting entries

### 📦 Import Operations
- **Shipment Tracking**: Track vessels from loading to arrival
  - Multi-status workflow (Loading → In Transit → Arrival → Offloading)
  - ETA monitoring with alerts
  - Multiple vehicles per shipment
  
- **Customs Clearance**: Complete duty management
  - Customs duty, excise duty, import VAT tracking
  - Clearing agent fee tracking
  - Port charges and transport costs
  - Automatic journal entry creation

### 💼 Sales & CRM
- **Vehicle Booking**: Two business models
  - Import on Demand (pre-order vehicles)
  - Ready Stock (sell available vehicles)
- **KYC Verification**: Customer identity verification
- **Payment Milestones**: Automatic payment scheduling
- **Email Notifications**: Status change alerts to customers

### 💰 Integrated Accounting
Automatic journal entries for:
- Vehicle receipt (Vehicles in Transit)
- Customs clearance (Duties & Expenses)
- Customer advance payments
- Vehicle sales (Revenue + COGS)
- Complete Chart of Accounts for vehicle import business

### 📄 Custom Print Formats
- Commercial Invoice (Royal Logistics branded)
- Quotation (with vehicle details auto-fetch)
- Salary Slip (Royal Logistics format)

## Installation

### Prerequisites
- ERPNext Version 15.x
- Frappe Framework Version 15.x

### Install Steps

```bash
# 1. Get the app
cd ~/frappe-bench
bench get-app https://github.com/GoldenJustin/vehicle_import.git

# 2. Install on site
bench --site YOUR_SITE install-app vehicle_import

# 3. Migrate
bench --site YOUR_SITE migrate

# 4. Build assets
bench build --app vehicle_import

# 5. Restart
bench restart
Chart of Accounts Created
The app automatically creates these accounts:

Assets:

Vehicle Inventory
Vehicles in Transit
Income:

Vehicle Sales
COGS:

Vehicle Cost of Goods Sold (Group)
Vehicle Purchase Cost
Import Duties and Taxes
Shipping and Freight
Expenses:

Clearing Agent Fees
Port and Transport Charges
Liabilities:

Customer Advances - Vehicles
Usage
1. Create a Vehicle
Navigate to: Vehicle Import > Vehicle > New

Enter vehicle details (Make, Model, Year, VIN)
Enter costing (CIF, Customs, Other Charges)
Set selling price
Save → Auto-creates stock item & accounting entry
2. Create Shipment Tracking
Navigate to: Vehicle Import > Shipment Tracking > New

Add shipping details (Vessel, B/L, ETA)
Add vehicles to shipment
Use "Next Shipment Step" button to progress status
3. Customs Clearance
Navigate to: Vehicle Import > Customs Clearance > New

Select shipment and vehicle
Enter duty amounts
Submit → Auto-creates journal entry
4. Vehicle Booking
Navigate to: Vehicle Import > Vehicle Booking > New

Select customer
Choose vehicle or enter specs
Select advance type (CIF or 50% of CIF)
Auto-creates payment milestones
Submit → Creates advance payment entry
5. Sales Invoice
Create sales invoice with vehicle item

Vehicle details auto-populate in print
Use "Royal Commercial Invoice" print format
Configuration
Email Templates
The app includes email templates for:

Payment Confirmation
Vehicle Inspection
Shipment Schedule
Loading Confirmation
Vessel Arrival Notice
Delivery Ready
Print Formats
Editable at: Setup > Printing > Print Format

Royal Commercial Invoice
Royal Commercial Quotation
DocTypes Created
Vehicle: Main vehicle records
Vehicle Booking: Sales bookings
Shipment Tracking: Import shipment management
Customs Clearance: Duty and clearance tracking
KYC Verification: Customer verification
Payment Milestone (Child Table)
Shipment Vehicle (Child Table)
Accounting Flow
text

1. Vehicle Purchase
   DR: Vehicles in Transit
   CR: Accounts Payable

2. Customs Clearance
   DR: Import Duties, Clearing Fees, Port Charges
   CR: Cash/Bank

3. Customer Advance
   DR: Cash/Bank
   CR: Customer Advances - Vehicles

4. Vehicle Sale
   DR: Accounts Receivable
   CR: Vehicle Sales
   
   DR: Vehicle COGS
   CR: Vehicle Inventory
   
   DR: Customer Advances
   CR: Accounts Receivable
Developer
CMHL Royal Logistics & Supplies Company Limited

Website: www.royal.co.tz
Email: sales@royal.co.tz
License
MIT License

Support
For issues and questions:

GitHub Issues: Create an issue
Email: admin@vehicleimport.co.tz
Credits
Built on top of:

Frappe Framework
ERPNext
