import firebase_admin
from firebase_admin import credentials, firestore
def GenerateTechSeaside(data_string):
    name_lst = data_string.split(" ")
    name = name_lst[0] + " " + name_lst[1]
    location = (data_string.split(" - "))[-1]
    return (f'{name} - {location} - Purolator')
def GenerateGeneralTech(data_string):
    name_lst = data_string.split(" ")
    name = name_lst[0] + " " + name_lst[1]
    location = " ".join(name_lst[3::])
    send_type = ""
    if "55 Expansion Avenue, Saint John, E2R 1A6" in location:
        send_type = "PickupSJ"
    elif "377 York Street, Fredericton E3B 3P6" in location:
        send_type = "Day&Ross"
    elif "70 Assomption Boulevard, Moncton, E1C 1A1" in location:
        send_type = "Day&Ross"
    else:
        send_type = "Purolator"
    return (f'{name} - {location} - {send_type}')
def Run():
    seaside = True
    normal = True
    data_lst = []
    while seaside:
        data = input()
        if data != "stop":
            data_lst.append(GenerateTechSeaside(data))
        else:
            seaside = False
            break
    while normal:
        data = input()
        if data != "stop":
            data_lst.append(GenerateGeneralTech(data))
        else:
            normal = False
            break
    for i in data_lst:
        print(i)
    
cred = credentials.Certificate("C:\\Users\\josh.lynch\\Videos\\WaybillMaster\\bomwipstore-firebase-adminsdk-jhqev-c316244037.json")
firebase_admin.initialize_app(cred)
def RunPush():
    go = True
    while go:
        data = input()
        if data != "stop":
            try:
                name, location, sendMethod = data.split(" - ")


                db = firestore.client()
                ref = db.collection("TechDatabase").document(f'{name}')
                data = {
                "Name": name,
                "Location": location,
                "SendingMethod": sendMethod,

                }
                ref.set(data)
                print(f'{name} Sucessfully Pushed')
            except:
                print("Push Failed")
RunPush()