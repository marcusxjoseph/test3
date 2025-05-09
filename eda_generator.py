import json
import xml.etree.ElementTree as ET
from datetime import datetime
import uuid
import lxml.etree as LET

def generate_eda_xml(data):
    ns = "http://www.egvp.de/Nachrichtentypen/EDA/1.4"
    ET.register_namespace('', ns)

    root = ET.Element(f"{{{ns}}}Mahnantrag", {
        "verfahrensart": "Mahn",
        "version": "1.4",
        "dateiID": str(uuid.uuid4()),
        "erstellungszeitpunkt": datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    })

    header = ET.SubElement(root, f"{{{ns}}}Header")
    ET.SubElement(header, f"{{{ns}}}Absender").text = data['glaeubiger']['name']
    ET.SubElement(header, f"{{{ns}}}Empfaenger").text = data.get('mahngericht', 'Zentrales Mahngericht')

    parteien = ET.SubElement(root, f"{{{ns}}}Parteien")
    g = ET.SubElement(parteien, f"{{{ns}}}Partei", parteiTyp="Antragsteller", parteiNr="G1")
    ET.SubElement(g, f"{{{ns}}}Name").text = data['glaeubiger']['name']
    a = ET.SubElement(g, f"{{{ns}}}Anschrift")
    ET.SubElement(a, f"{{{ns}}}Strasse").text = data['glaeubiger']['strasse']
    ET.SubElement(a, f"{{{ns}}}Hausnummer").text = data['glaeubiger']['hausnummer']
    ET.SubElement(a, f"{{{ns}}}Postleitzahl").text = data['glaeubiger']['plz']
    ET.SubElement(a, f"{{{ns}}}Ort").text = data['glaeubiger']['ort']

    s = ET.SubElement(parteien, f"{{{ns}}}Partei", parteiTyp="Antragsgegner", parteiNr="S1")
    ET.SubElement(s, f"{{{ns}}}Name").text = data['schuldner']['name']
    sa = ET.SubElement(s, f"{{{ns}}}Anschrift")
    ET.SubElement(sa, f"{{{ns}}}Strasse").text = data['schuldner']['strasse']
    ET.SubElement(sa, f"{{{ns}}}Hausnummer").text = data['schuldner']['hausnummer']
    ET.SubElement(sa, f"{{{ns}}}Postleitzahl").text = data['schuldner']['plz']
    ET.SubElement(sa, f"{{{ns}}}Ort").text = data['schuldner']['ort']

    forderungen = ET.SubElement(root, f"{{{ns}}}Forderungen")
    hf = ET.SubElement(forderungen, f"{{{ns}}}Forderung", forderungstyp="Hauptforderung", forderungID="F1")
    ET.SubElement(hf, f"{{{ns}}}GlaeubigerRef").text = "G1"
    ET.SubElement(hf, f"{{{ns}}}SchuldnerRef").text = "S1"
    ET.SubElement(hf, f"{{{ns}}}Betrag", waehrung="EUR").text = str(data['forderung']['hauptforderung'])
    ET.SubElement(hf, f"{{{ns}}}Gegenstand").text = data['forderung'].get('gegenstand', 'Forderung aus Vertrag')

    verfahren = ET.SubElement(root, f"{{{ns}}}Verfahren")
    ET.SubElement(verfahren, f"{{{ns}}}Amtsgericht").text = data.get('amtsgericht', 'Zentrales Mahngericht')
    ET.SubElement(verfahren, f"{{{ns}}}Verfahrensgegenstand").text = "Mahnverfahren"
    ET.SubElement(verfahren, f"{{{ns}}}Verfahrensart").text = "Antrag auf Erlass eines Mahnbescheids"
    ET.SubElement(verfahren, f"{{{ns}}}Antragstyp").text = "NormalerMahnantrag"

    return ET.ElementTree(root)

def parse_input(file_path):
    import csv
    with open(file_path, newline='', encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        row = next(reader)
        return {
            "glaeubiger": {
                "name": row['glaeubiger_name'],
                "strasse": row['glaeubiger_strasse'],
                "hausnummer": row['glaeubiger_hausnummer'],
                "plz": row['glaeubiger_plz'],
                "ort": row['glaeubiger_ort'],
            },
            "schuldner": {
                "name": row['schuldner_name'],
                "strasse": row['schuldner_strasse'],
                "hausnummer": row['schuldner_hausnummer'],
                "plz": row['schuldner_plz'],
                "ort": row['schuldner_ort'],
            },
            "forderung": {
                "hauptforderung": row['hauptforderung'],
                "gegenstand": row['gegenstand']
            },
            "amtsgericht": row['amtsgericht']
        }

def create_eda_zip(tree, name):
    from zipfile import ZipFile
    xml_path = f"/tmp/{name}.xml"
    manifest_path = f"/tmp/manifest.xml"
    zip_path = f"/tmp/{name}.zip"

    tree.write(xml_path, encoding='utf-8', xml_declaration=True)

    with open(manifest_path, 'w') as m:
        m.write("Manifest-Version: 1.0n")
")
        m.write(f"Datei: {name}.xml
")

    with ZipFile(zip_path, 'w') as zipf:
        zipf.write(xml_path, arcname=f"{name}.xml")
        zipf.write(manifest_path, arcname="manifest.xml")
    return zip_path
