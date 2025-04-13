# Imports
from pypdf import PdfReader
import math
from pathlib import Path
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime
import tkinter as tk
from tkinter import filedialog

# Get Credentials Will need to be general someday
cred = credentials.Certificate("C:\\Users\\user\\Documents\\Repositories\\WaybillMaster\\bomwipstore-firebase-adminsdk-jhqev-c316244037.json")
firebase_admin.initialize_app(cred)

# Gets all data from a pdf 
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
print(GetDataList("C:\\Users\\user\\Documents\\Repositories\\WaybillMaster\\Spinney - 395007 - STJ6047100.pdf"))