from pypdf import PdfReader
from pathlib import Path
import math
import firebase_admin
from datetime import datetime
import tkinter as tk
from tkinter import filedialog
import firebase_admin
from firebase_admin import credentials, firestore

# Initialize Firebase
cred = credentials.Certificate("C:\\Users\\josh.lynch\\Videos\\WaybillMaster\\bomwipstore-firebase-adminsdk-jhqev-c316244037.json")
firebase_admin.initialize_app(cred)


def GetDataList(pathName):
    reader = PdfReader(pathName)  # Open the PDF
    full_data = []
    
    # Iterate over each page in the PDF
    for page in reader.pages:
        # Extract text from the page, split into lines, and clean up empty lines
        data_lst = page.extract_text().split("\n")
        # Append non-empty, stripped lines to full_data
        full_data.extend([i.strip() for i in data_lst if i.strip()])
    
    return full_data

print(GetDataList("C:\\Users\\josh.lynch\\Videos\\WaybillMaster\\Shepherd - 400039 - PickupSJ.pdf"))
def GetDate(lst):
    for i in range(len(lst)):
        if lst[i] == "Date:":
            return f"{lst[i+1]} {lst[i+2]}"
    return "Unknown Date"


def GetNameAndLocation(mydata):
    for i in range(len(mydata)):
        if mydata[i] == "Saint John,NB,E2R 1A6,Canada":
            return mydata[i + 1].split(",")[0], f"{mydata[i + 1].split(',')[1]}, {mydata[i+2]}"
    return "Unknown", "Unknown Location"


class Device:
    def __init__(self, DeviceName, Quantity, ordrNum):
        self.Device = DeviceName
        self.Qty = Quantity
        self.OrderNumber = ordrNum

    def DetermineBoxes(self):
        box_sizes = {
            "CGM4981COM": 8, "CGM4331COM": 8, "TG4482A": 8,
            "SCXI11BEI": 10, "IPTVARXI6HD": 10, "IPTVTCXI6HD": 10,
            "SCXI11BEI-ENTOS": 10, "XS010XQ": 12, "XE2SGROG1": 24,
            "CODA5810": 5
        }
        return self.Qty / box_sizes.get(self.Device, 10)

    def DetermineWeight(self):
        weights = {
            "CGM4981COM": 4.16, "CGM4331COM": 3.64, "TG4482A": 3.64,
            "SCXI11BEI": 1.4, "SCXI11BEI-ENTOS": 1.4, "IPTVARXI6HD": 1.8,
            "IPTVTCXI6HD": 1.8, "XE2SGROG1": 0.86, "CODA5810": 3.15,
            "XS010XQ": 1.38
        }
        return weights.get(self.Device, 2.33) * self.Qty


def GetDevices(lst):
    device_data = []
    return_lst = []
    appender = False
    for i in range(len(lst)):
        if appender == True:
            device_data.append(lst[i])
        if lst[i] == "Item Description":
            appender = True
    chunks = [device_data[i:i+5] for i in range(0, len(device_data), 5)]
    chunks.pop()
    
    for i in chunks:
        formatQty = i[3].split(" ")
        orderNumber = i[0]
        device = i[1] + i[2]
        qty = int(formatQty[0])
        thisdevice = Device(device, qty, orderNumber)
        return_lst.append(thisdevice)
    return return_lst


def GetWaybill(path):
    return Path(path).stem.split(" - ")[-1]


class Order:
    def __init__(self, Name, Location, Date, Waybill, Boxes, Weight):
        self.NameOfTec = Name
        self.Destination = Location
        self.TimeOfCompletion = Date
        self.WaybillNumber = Waybill
        self.NumberOfBoxes = math.ceil(Boxes)
        self.TotalWeight = math.ceil(Weight)
        self.NumberOfSkids = math.ceil(self.NumberOfBoxes / 24)

    def PushToFirebase(self):
        try:
            db = firestore.client()
            ref = db.collection("DeliveryTracker").document(f'{self.NameOfTec} - {self.WaybillNumber}')
            date_obj = datetime.strptime(self.TimeOfCompletion, "%d/%m/%Y %I:%M:%S %p")

            data = {
                "TechName": self.NameOfTec,
                "DateCompleted": date_obj,
                "Skids": self.NumberOfSkids,
                "Waybill": self.WaybillNumber,
                "Weight": self.TotalWeight,
                "Boxes": self.NumberOfBoxes,
                "Location": self.Destination
            }
            ref.set(data)
            print(f"Pushed: {self.NameOfTec} - {self.WaybillNumber}")

        except Exception as e:
            print(f"Failed to push {self.WaybillNumber} to Firebase: {e}")


def ProcessFile(path):
    try:
        data_lst = GetDataList(path)
        name, location = GetNameAndLocation(data_lst)
        date = GetDate(data_lst)
        waybill = GetWaybill(path)
        devices = GetDevices(data_lst)
        
        total_boxes = sum(device.DetermineBoxes() for device in devices)
        total_weight = sum(device.DetermineWeight() for device in devices)

        order = Order(name, location, date, waybill, total_boxes, total_weight)
        order.PushToFirebase()

    except Exception as e:
        print(f"Error processing {path}: {e}")


def SelectAndProcessFiles():
    root = tk.Tk()
    root.withdraw()  # Hide main window

    file_paths = filedialog.askopenfilenames(
        title="Select PDF Files",
        filetypes=[("PDF Files", "*.pdf")]
    )

    if not file_paths:
        print("No files selected.")
        return

    for path in file_paths:
        ProcessFile(path)


# if __name__ == "__main__":
#     SelectAndProcessFiles()
