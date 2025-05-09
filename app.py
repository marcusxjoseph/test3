# -*- coding: utf-8 -*-
from flask import Flask, render_template, request, send_file
import os
import uuid
import csv
from pathlib import Path
from eda_generator import parse_input, generate_eda_xml, create_eda_zip
from utils import extract_invoice_data

app = Flask(__name__)
UPLOAD_FOLDER = "/tmp"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        f = request.files['file']
        ext = f.filename.split('.')[-1].lower()
        if ext not in ['csv', 'json']:
            return "Nur CSV oder JSON erlaubt.", 400
        unique_name = str(uuid.uuid4())
        input_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{unique_name}.{ext}")
        f.save(input_path)
        data = parse_input(input_path)
        tree = generate_eda_xml(data)
        zip_path = create_eda_zip(tree, unique_name)
        return send_file(zip_path, as_attachment=True)
    return render_template('index.html')

@app.route('/upload-pdf', methods=['POST'])
def upload_pdf():
    f = request.files['pdf']
    if not f or not f.filename.endswith('.pdf'):
        return "Ungültige Datei", 400

    unique_name = str(uuid.uuid4())
    pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{unique_name}.pdf")
    f.save(pdf_path)

    extracted = extract_invoice_data(pdf_path)

    csv_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{unique_name}.csv")
    with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['glaeubiger_name', 'glaeubiger_strasse', 'glaeubiger_hausnummer',
                      'glaeubiger_plz', 'glaeubiger_ort', 'schuldner_name', 'schuldner_strasse',
                      'schuldner_hausnummer', 'schuldner_plz', 'schuldner_ort',
                      'hauptforderung', 'gegenstand', 'amtsgericht']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerow(extracted)

    data = parse_input(csv_path)
    tree = generate_eda_xml(data)
    zip_path = create_eda_zip(tree, unique_name)
    return send_file(zip_path, as_attachment=True)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
