from flask import Flask, request, render_template, send_file
import os
import pandas as pd
from extract_with_gemini import extract_structured_data

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        file = request.files['file']
        if file:
            filepath = os.path.join(UPLOAD_FOLDER, file.filename)
            file.save(filepath)

            
            #if not data:
               # return "❌ Gemini could not extract structured data. Try a clearer document."
            
            # Save to Excel
            output_path = os.path.join(UPLOAD_FOLDER, 'result.xlsx')
            return send_file(output_path, as_attachment=True)

    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='192.168.105.203', port=5000, debug=True)
