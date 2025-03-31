from flask import Flask, request, jsonify
from pypdf import PdfReader
import math
from pathlib import Path
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime
import os

# Initialize Flask app
app = Flask(__name__)

# Get Credentials
cred = credentials.Certificate("C:\\Users\\josh.lynch\\Videos\\WaybillMaster\\bomwipstore-firebase-adminsdk-jhqev-c316244037.json")
firebase_admin.initialize_app(cred)

def GetDataList(pathName):
    reader = PdfReader(pathName)  # Open the PDF
    full_data = []
    for page in reader.pages:
        data_lst = page.extract_text().split("\n")
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
    
    for i in range(len(Data)):
        if Data[i] == "Saint John,NB,E2R 1A6,Canada":
            username = Data[i+1]
            if "," in username:
                temp = username.split(",")
                for j in range(len(temp)):
                    if j == 0:
                        username = temp[j]
                    else:
                        location_lst.append(temp[j])
            break

    for i in range(len(Data)):
        if username in Data[i]:
            LocationBurr = True
            continue
        if LocationBurr:
            while i < len(Data) and Data[i] != "Load Number:":
                location_lst.append(Data[i])
                i += 1
            break
    
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
        if DeviceTime:
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
        if DeviceNameScanner:
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

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    # Save the file temporarily
    file_path = os.path.join("uploads", file.filename)
    file.save(file_path)

    try:
        DataList = GetDataList(file_path)  
        date = GetDate(DataList)
        name, location = GetNameAndLocation(DataList)
        waybill = GetWaybill(file_path)
        DeviceList, orderID = ParseDeviceData(DataList)
        boxes, weight = EstimateBoxesAndWeight(DeviceList)

        order_data = {
            "NameOfTec": name,
            "Destination": location,
            "TimeOfCompletion": date,
            "WaybillNumber": waybill,
            "NumberOfBoxes": round(boxes),
            "TotalWeight": math.ceil(weight),
            "NumberOfSkids": round(boxes / 24),
            "Devices": DeviceList,
            "OrderID": orderID
        }

        return jsonify(order_data)

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        # Clean up the uploaded file
        if os.path.exists(file_path):
            os.remove(file_path)

if __name__ == '__main__':
    app.run(debug=True)