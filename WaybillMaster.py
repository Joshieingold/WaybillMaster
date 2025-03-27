from pypdf import PdfReader
from pathlib import Path
#path = "C:\\Users\\josh.lynch\\Videos\\WaybillMaster\\Spinney - 395007 - STJ6047100.pdf"
#path = "C:\\Users\\josh.lynch\\Videos\\WaybillMaster\\Lane - 396036 - PickupSJ.pdf"
path = "C:\\Users\\josh.lynch\\Videos\\WaybillMaster\\NF1 - 396041 - 335306377169.pdf"
def GetDataList(pathName):
    reader = PdfReader(pathName)
    print(len(reader.pages))
    page = reader.pages[0]
    data_lst = (page.extract_text()).split("\n")
    best_lst = []
    #print(data_lst)
    for i in data_lst:
        if i == " ":
            pass
        else: best_lst.append(i)
    return best_lst
def GetDate(lst):
    answer = ""
    for i in range(len(lst)):
        if lst[i] == "Date:":
            answer = lst[i+1] + " " + lst[i+2]
    return answer
def GetName(mydata):
    name = ""
    for i in range(len(mydata)):
        if mydata[i] == "Saint John,NB,E2R 1A6,Canada":
            name, location = (mydata[i + 1]).split(",")
            return (f'Name: {name} \nLocation: {location}')
            
    print(name)
class Device:
    def __init__(self, DeviceName, Quantity, ordrNum):
        self.Device = DeviceName
        self.Qty = Quantity
        self.OrderNumber = ordrNum
    def PrintDevice(self):
        print(f'Order Number: {self.OrderNumber}')
        print(f'Model: {self.Device}')
        print(f'Quantity: {self.Qty}')
    def DetermineBoxes(self):
        full_box = 0
        EightPer = ["CGM4981COM", "CGM4331COM", "TG4482A"]
        TenPer = ["SCXI11BEI", "IPTVARXI6HD", "IPTVTCXI6HD", "SCXI11BEI-ENTOS"]
        if self.Device in EightPer:
            full_box = 8
        elif self.Device in TenPer:
            full_box = 10
        elif self.Device == "XS010XQ":
            full_box = 12
        elif self.Device == "XE2SGROG1":
            full_box = 24
        elif self.Device == "CODA5810":
            full_box = 5
        else:
            full_box = 10
        return self.Qty / full_box
    def DetermineWeight(self):
        if self.Device == "CGM4981COM":
            return 4.16 * self.Qty
        elif self.Device == "CGM4331COM" or self.Device == "TG4482A":
            return 3.64 * self.Qty
        elif self.Device == "SCXI11BEI" or self.Device == "SCXI11BEI-ENTOS":
            return 1.4 * self.Qty
        elif self.Device == "IPTVARXI6HD" or self.Device == "IPTVTCXI6HD":
            return 1.8 * self.Qty
        elif self.Device == "XE2SGROG1":
            return 0.86 * self.Qty
        elif self.Device == "CODA5810":
            return 3.15 * self.Qty
        elif self.Device == "SCHB1AEW" or self.Device == "SCHC2AEW" or self.Device == "SCHC3AE0":
            return 2.3 * self.Qty
        elif self.Device == "XS010XQ" or self.Device == "XS010XB" or self.Device == "XS020XONT" or self.Device == "XS505M":
            return 1.38 * self.Qty
        else: 
            return 2.33 * self.Qty
        


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
    thisPath = Path(path)
    file_name =  thisPath.name
    split_info = file_name.split(" - ")
    waybill = split_info[2].removesuffix(".pdf")
    return waybill

lst = GetDataList(path)
print(GetName(lst))  
GetWaybill(path) 
print(f'Date: {GetDate(lst)}')
print(f'Waybill: {GetWaybill(path)}')
devices = GetDevices(lst)
total_box = 0
total_weight = 0
for i in devices:
    total_box += i.DetermineBoxes()
    total_weight += i.DetermineWeight()
print(f'Total Boxes: {total_box}')
print(f'Total Weight: {total_weight}')