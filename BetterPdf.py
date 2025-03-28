from pypdf import PdfReader
import math
from pathlib import Path
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime
import tkinter as tk
from tkinter import filedialog

cred = credentials.Certificate("C:\\Users\\user\\Documents\\Repositories\\WaybillMaster\\bomwipstore-firebase-adminsdk-jhqev-c316244037.json")
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
def GetDate(Data):
    for i in range(len(Data)):
        if Data[i] == "Date:":
            return (Data[i+1].split(" "))[0]
def GetNameAndLocation(Data):
    LocationBurr = False
    username = ""
    location_lst = []
    
    # Search for the specific location to find the username
    for i in range(len(Data)):
        if Data[i] == "Saint John,NB,E2R 1A6,Canada":
            username = Data[i+1]  # Username is the next item in the list
            if "," in username:  # If the username contains commas (split it for location)
                temp = username.split(",")
                for j in range(len(temp)):
                    if j == 0:
                        username = temp[j]  # First part is the username
                    else:
                        location_lst.append(temp[j])  # Add the rest to the location list
            break  # Exit the loop once username and location are found

    # Now look for the username in the data to gather further location info
    for i in range(len(Data)):
        if username in Data[i]:  # Found the username
            LocationBurr = True  # Set the flag to start collecting the location
            continue
        if LocationBurr:  # If flag is true, start collecting location data
            while i < len(Data) and Data[i] != "Load Number:":  # Stop at the "Load Number:" line
                location_lst.append(Data[i])  # Collect all data until "Load Number:"
                i += 1  # Move to the next item in the list
            break  # Exit the loop after location data is collected
    
    # Join location data into a single string and return both username and location
    return [username, " ".join(location_lst)]
def GetWaybill(pathName):
    file = Path(pathName).stem
    if " - " in file:
        return file.split(" - ")[-1]
    else:
        temp = file.split("-")
        if (temp[-1]).upper().endswith("SJ"):
            return f'PickupSJ'
        else: 
            return temp[-1]
def GetDeviceChunks(Data):
    DeviceTime = False
    device_lst = []
    for i in range(len(Data)):
        if DeviceTime == True:
            device_lst.append(Data[i])
        if Data[i] == "Item Description":
            DeviceTime = True
    return device_lst
def ParseDeviceData(Data):
    UnfilteredList = GetDeviceChunks(Data)
    OrderID = UnfilteredList[0]
    DeviceList = []
    DeviceNameScanner = False 
    DeviceString = ""
    for i in range(len(UnfilteredList)):
        if "UNITS" in UnfilteredList[i]:
            DeviceNameScanner = False
            qty = (UnfilteredList[i].split(" "))[0]
            DeviceString += f' {qty}'
            DeviceList.append(DeviceString)
            DeviceString = ""
        if DeviceNameScanner == True:
            DeviceString += UnfilteredList[i]
        if UnfilteredList[i] == OrderID:
            DeviceNameScanner = True
    return [DeviceList, OrderID]
def EstimateBoxesAndWeight(DeviceList):           
    box_sizes = {
            "CGM4981COM": 8, "CGM4331COM": 8, "TG4482A": 8,
            "SCXI11BEI": 10, "IPTVARXI6HD": 10, "IPTVTCXI6HD": 10,
            "SCXI11BEI-ENTOS": 10, "XS010XQ": 12, "XE2SGROG1": 24,
            "CODA5810": 5
        }
    weights = {
            "CGM4981COM": 4.16, "CGM4331COM": 3.64, "TG4482A": 3.64,
            "SCXI11BEI": 1.4, "SCXI11BEI-ENTOS": 1.4, "IPTVARXI6HD": 1.8,
            "IPTVTCXI6HD": 1.8, "XE2SGROG1": 0.86, "CODA5810": 3.15,
            "XS010XQ": 1.38
        }
    TotalBoxes = 0
    TotalWeight = 0
    for DeviceSet in DeviceList:
        Device, Qty = DeviceSet.split(" ")
        TotalBoxes += float(Qty) / (box_sizes.get(Device, 10))
        TotalWeight += float(Qty) * (weights.get(Device, 2.33))
    return [TotalBoxes, TotalWeight]

# Order Class
class Order:
    def __init__(self, Name, Location, Date, Waybill, Boxes, Weight, DeviceList, OrderID):
        self.NameOfTec = Name
        self.Destination = Location
        self.TimeOfCompletion = Date
        self.WaybillNumber = Waybill
        self.NumberOfBoxes = round(Boxes)
        self.TotalWeight = math.ceil(Weight)
        self.NumberOfSkids = self.NumberOfBoxes / 24
        self.Devices = DeviceList
        self.OrderID = OrderID
    def DefineDetails(self):
        print(f'Order for: {self.NameOfTec}')
        print(f'Going to: {self.Destination}')
        print(f'Order completed on: {self.TimeOfCompletion}')
        print(f'Shipped under the waybill: {self.WaybillNumber}')
        print(f'Estimated boxes sent: {self.NumberOfBoxes}')
        print(f'Estimated weight: {self.TotalWeight}lb')
        print(f'Estimated Number of Skids: {self.NumberOfSkids}')
        print(f'Devices Associated with this order:')
        for i in range(len(self.Devices)):
            print(f'{i + 1}: {self.Devices[i]}')
    def PushToFirebase(self):
        try:
            db = firestore.client()
            ref = db.collection("DeliveryTracker").document(f'{self.NameOfTec} - {self.OrderID} - {self.WaybillNumber}')
            date_obj = datetime.strptime(self.TimeOfCompletion, "%d/%m/%Y")

            # Convert device list into a dictionary (map)
            device_map = {}
            for item in self.Devices:
                Device, Qty = item.split()
                device_map[Device] = int(Qty)  # Store as integer

            data = {
                "TechName": self.NameOfTec,
                "DateCompleted": date_obj,
                "Skids": self.NumberOfSkids,
                "Waybill": self.WaybillNumber,
                "Weight": self.TotalWeight,
                "Boxes": self.NumberOfBoxes,
                "Location": self.Destination,
                "Devices": device_map,  # Now stored as a dictionary
                "OrderID": self.OrderID
            }

            ref.set(data)
            print(f"Pushed: {self.NameOfTec} - {self.OrderID} - {self.WaybillNumber}")

        except Exception as e:
            print(f"Failed to push {self.WaybillNumber} to Firebase: {e}")


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
def ProcessFile(path):
    try:
        DataList = (GetDataList(path))  
        date = (GetDate(DataList))
        name, location = (GetNameAndLocation(DataList))
        waybill = (GetWaybill(path))
        DeviceList, orderID = (ParseDeviceData(DataList))
        boxes, weight = EstimateBoxesAndWeight(DeviceList)
        ThisOrder = Order(name, location, date, waybill, boxes, weight, DeviceList, orderID)
        ThisOrder.PushToFirebase()

    except Exception as e:
        print(f"Error processing {path}: {e}")

if __name__ == "__main__":
    SelectAndProcessFiles()