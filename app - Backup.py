from flask import Flask, request, render_template, send_file
import os
import pandas as pd
import mimetypes
import google.generativeai as genai

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

API_KEY = "AIzaSyD0ZQiR56gas1Kxnq_fEwv3Ku9M_KH4Zo8"  # Replace with your key
genai.configure(api_key=API_KEY)

PROMPT = """
Extract information for each person in the uploaded document in the following format.

Repeat this block for each person. If a field is missing, leave it empty.
process all the file 

-Add SIC Reference from  (:الرقم) it is always located at the top right of the document and translate it to eglish, everything in this format (####/###/###)should be in english 
-Add the SIC Date from the date in the left top of the first page translate this date to english
-only Name (Arabic) and mother name and father name should be in arabic ,keep comments in arabic
-if no Arabic name ,translte the english name to arabic and add as Name (Arabic)
-If birth year not available , there should be the age instead 
-Remove the quotes from names
-do not add any phrase to the output file , only the data
-Nickname is the a.k.a
-If birth date is not available Insert NA
-get full date of birth if available
-get date of birth in dd/mm/yyyy format , the country name after that date is the place of birth ,add this field 
 

number:
Name (Arabic): 
Name (English):
Nickname : 
Passport number:
Nationality: 
Birth date: 
place of birth:
Mother: 
Father's Name: 
Register Number: 
Register Place: 
SIC Reference: 
SIC Date: 
Comments:
"""

EXPECTED_FIELDS = [
    "number",
    "Name (Arabic)",
    "Name (English)",
    "Nickname", 
    "Passport number",
    "Nationality",
    "Birth date",
    "place of birth",
    "Mother",
    "Father's Name",
    "Register Number",
    "Register Place",
    "SIC Reference",
    "SIC Date",
    "Comments"
]

def extract_structured_data(file_path, output_excel_name):
    mime_type, _ = mimetypes.guess_type(file_path)
    if not mime_type:
        mime_type = 'application/octet-stream'

    with open(file_path, 'rb') as f:
        file_data = f.read()

    model = genai.GenerativeModel('gemini-1.5-flash')
    vision_input = [PROMPT, {"mime_type": mime_type, "data": file_data}]
    response = model.generate_content(vision_input)
    response_text = response.text.strip()

    txt_path = os.path.join(UPLOAD_FOLDER, 'response_output.txt')
    with open(txt_path, 'w', encoding='utf-8') as f:
        f.write(response_text)

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
        return None

    df = pd.DataFrame(records)
    excel_path = os.path.join(UPLOAD_FOLDER, output_excel_name)
    df.to_excel(excel_path, index=False)
    return excel_path

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        file = request.files.get('file')
        if file:
            pdf_filename = file.filename
            if not pdf_filename.lower().endswith('.pdf'):
                return "❌ Please upload a PDF file."

            pdf_path = os.path.join(UPLOAD_FOLDER, pdf_filename)
            file.save(pdf_path)

            base_name = os.path.splitext(pdf_filename)[0]
            excel_filename = f"{base_name}.xlsx"

            result_path = extract_structured_data(pdf_path, excel_filename)
            if result_path:
                return send_file(result_path, as_attachment=True)
            else:
                return "❌ Could not extract structured data."

    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=443, debug=True)
