from flask import Flask, request, render_template, send_file
import google.generativeai as genai
import mimetypes
import os
import pandas as pd

PROMPT = """
Extract information for each person in the uploaded document in the following format.

Repeat this block for each person. If a field is missing, leave it empty.
process all the file 

Add SIC Reference from the arabic word :الرقم in the first page of the document
Add the SIC Date from the date in the left top of the first page 

Remove the quotes from names 

do not add any phrase to the output file , only the data
number:
Name (Arabic): 
Name (English):
Nickname : 
Passport number:
Nationality: 
Birth Year: 
Mother: 
Father's Name: 
Register Number: 
Register Place: 
SIC Reference: 
SIC Date: 
Comments:
"""

API_KEY = "AIzaSyD0ZQiR56gas1Kxnq_fEwv3Ku9M_KH4Zo8"  # Replace with your actual key

genai.configure(api_key=API_KEY)

# Predefined consistent headers
EXPECTED_FIELDS = [
    "Name (Arabic)",
    "Name (English)",
    "Nickname", 
    "Passport number",
    "Nationality",
    "Birth Year",
    "Mother",
    "Father's Name",
    "Register Number",
    "Register Place",
    "SIC Reference",
    "SIC Date",
    "Comments"
]

def extract_structured_data(file_path):
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return None

    mime_type, _ = mimetypes.guess_type(file_path)
    if not mime_type:
        mime_type = 'application/octet-stream'

    with open(file_path, 'rb') as f:
        file_data = f.read()

    model = genai.GenerativeModel('gemini-1.5-flash')
    vision_input = [
        PROMPT,
        {
            "mime_type": mime_type,
            "data": file_data
        }
    ]

    response = model.generate_content(vision_input)
    response_text = response.text.strip()

    # Save raw text
    os.makedirs('uploads', exist_ok=True)
    txt_path = os.path.join('uploads', 'response_output.txt')
    with open(txt_path, 'w', encoding='utf-8') as f:
        f.write(response_text)

    # Parse records
    entries = response_text.split("\n\n")
    records = []

    for entry in entries:
        lines = entry.strip().split("\n")
        record = {field: "" for field in EXPECTED_FIELDS}
        for line in lines:
            if ':' in line:
                key, value = line.split(":", 1)
                key = key.strip()
                if key in EXPECTED_FIELDS:
                    record[key] = value.strip()
        if any(value != "" for value in record.values()):
            records.append(record)

    if not records:
        print("❌ No valid records parsed.")
        return None


    
