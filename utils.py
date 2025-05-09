import pytesseract
from pdf2image import convert_from_path
import re

def extract_invoice_data(pdf_path):
    images = convert_from_path(pdf_path)
    text = "\n".join(pytesseract.image_to_string(img) for img in images)

    def extract(pattern, default=""):
        match = re.search(pattern, text, re.IGNORECASE)
        return match.group(1).strip() if match else default

    return {
        'glaeubiger_name': extract(r'Rechnungssteller[:\s]+(.+)'),
        'glaeubiger_strasse': extract(r'Adresse[:\s]+(.+?)\s\d+'),
        'glaeubiger_hausnummer': extract(r'Adresse[:\s]+.+?\s(\d+)'),
        'glaeubiger_plz': extract(r'PLZ[:\s]+(\d{5})'),
        'glaeubiger_ort': extract(r'Ort[:\s]+(.+)'),
        'schuldner_name': extract(r'Schuldner[:\s]+(.+)'),
        'schuldner_strasse': extract(r'Schuldneradresse[:\s]+(.+?)\s\d+'),
        'schuldner_hausnummer': extract(r'Schuldneradresse[:\s]+.+?\s(\d+)'),
        'schuldner_plz': extract(r'Schuldner-PLZ[:\s]+(\d{5})'),
        'schuldner_ort': extract(r'Schuldner-Ort[:\s]+(.+)'),
        'hauptforderung': extract(r'Betrag[:\s]+([\d,\.]+)', '0').replace(',', '.'),
        'gegenstand': extract(r'Leistung[:\s]+(.+)', 'Forderung aus Lieferung'),
        'amtsgericht': extract(r'Amtsgericht[:\s]+(.+)', 'Zentrales Mahngericht'),
    }
