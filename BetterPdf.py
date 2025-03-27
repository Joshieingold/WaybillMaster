from pypdf import PdfReader
import math
from pathlib import Path
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
    for i in Data:
        if DeviceTime == True:
            device_lst.append(Data[i])
        if Data[i] == "Item Description":
            DeviceTime = True
def ParseDeviceData(Data):
    UnfilteredList = GetDeviceChunks(Data)
    OrderID = UnfilteredList[0]
    DeviceList = []
    for i in range(len(UnfilteredList)):
        if UnfilteredList[i] == OrderID:
            pass
        elif "UNITS" in UnfilteredList[i]:
            
            
        

path = "C:\\Users\\josh.lynch\\Videos\\WaybillMaster\\Landry - 397054 - 335308402270.pdf"
DataList = (GetDataList(path))  
date = (GetDate(DataList))
name, location = (GetNameAndLocation(DataList))
Waybill = (GetWaybill(path))
print(DataList)
class Order:
    def __init__(self, Name, Location, Date, Waybill, Boxes, Weight):
        self.NameOfTec = Name
        self.Destination = Location
        self.TimeOfCompletion = Date
        self.WaybillNumber = Waybill
        self.NumberOfBoxes = math.ceil(Boxes)
        self.TotalWeight = math.ceil(Weight)
        self.NumberOfSkids = math.ceil(self.NumberOfBoxes / 24)
