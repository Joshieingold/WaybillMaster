from google.cloud import firestore
import firebase_admin
from firebase_admin import credentials, firestore as admin_firestore
import openpyxl
from openpyxl import Workbook
from datetime import datetime

# Initialize Firebase Admin
cred = credentials.Certificate("C:\\Users\\user\\Documents\\Repositories\\WaybillMaster\\bomwipstore-firebase-adminsdk-jhqev-c316244037.json")
firebase_admin.initialize_app(cred)

# Connect to Firestore
db = admin_firestore.client()
print("Connected to Firestore. Fetching data...")

collection_name = 'DeliveryTracker'
docs = list(db.collection(collection_name).stream())
print(f"Found {len(docs)} documents.")

# Create a new workbook and sheet
wb = Workbook()
ws = wb.active
ws.title = "Delivery Tracker Data"

# Prepare header
header = [
    'Document ID', 'Boxes', 'DateCompleted', 'Location', 'Note', 'OrderID', 
    'Skids', 'TechName', 'Waybill', 'Weight'
]
ws.append(header)

# Set to keep track of all devices dynamically
device_columns = set()

# First loop: Gather data and identify all devices
for doc in docs:
    data = doc.to_dict()
    devices = data.get('Devices', {})

    # Track device names for dynamic columns
    for device in devices:
        device_columns.add(device)

# Convert device_columns set to a sorted list to ensure consistent ordering in Excel
device_columns = sorted(device_columns)

# Add device columns to the header
header.extend(device_columns)
ws.append(header)

# Second loop: Write the actual data to the Excel sheet
for doc in docs:
    try:
        data = doc.to_dict()
        doc_id = doc.id
        boxes = data.get('Boxes')
        date_completed = data.get('DateCompleted')
        
        # Remove timezone information from 'DateCompleted'
        if isinstance(date_completed, datetime):
            date_completed = date_completed.replace(tzinfo=None)

        devices = data.get('Devices', {})
        location = data.get('Location')
        note = data.get('Note')
        order_id = data.get('OrderID')
        skids_value = data.get('Skids')
        tech_name = data.get('TechName')
        waybill = data.get('Waybill')
        weight = data.get('Weight')

        # Prepare device data based on dynamic columns
        device_data = []
        for device in device_columns:
            try:
                device_data.append(devices.get(device, 0))
            except Exception as e:
                print(f"⚠️ Error retrieving device '{device}' for document {doc_id}: {e}")
                device_data.append(0)

        # Prepare the row data
        row = [
            doc_id, boxes, date_completed, location, note, order_id, skids_value, 
            tech_name, waybill, weight
        ] + device_data

        # Add the document data as a new row in the Excel sheet
        try:
            ws.append(row)
            print(f"✅ Added {doc.id}")
        except Exception as e:
            print(f"⚠️ Error writing row for document {doc_id}: {e}")
    
    except Exception as e:
        print(f"⚠️ Error processing document {doc.id}: {e}")

# Save the workbook to a file
try:
    output_file = "Delivery_Tracker_Data.xlsx"
    wb.save(output_file)
    print(f"✅ Data saved to {output_file}")
except Exception as e:
    print(f"⚠️ Error saving Excel file: {e}")
