from flask import Flask, request, jsonify
import xml.etree.ElementTree as ET  #pt a parsa fisiere XML

#definesc constante pentru tipurile de date acceptate
TIP_DATE_JSON = 'application/json'
TIP_DATE_XML = 'application/xml'
TIP_DATE_TEXT_SIMPLU = 'text/plain'

app = Flask(__name__)

lista_de_date_stocate = []

def proceseaza_date_json(cerere):
    try:
        date_json = cerere.get_json()
        if "cheie" not in date_json:
            return None, "EROARE: In JSON trebuie sa introduci campul 'cheie'!!"
        return date_json, None
    except Exception as eroare:
        return None, f"EROARE la parsarea JSON: {str(eroare)}"

def proceseaza_date_xml(cerere):
    try:
        radacina = ET.fromstring(cerere.data.decode('utf-8'))
        date_dict = {}
        for element in radacina:
            date_dict[element.tag] = element.text
        if "cheie" not in date_dict:
            return None, "EROARE: In XML trebuie sa introduci elementul <cheie>!!"
        return date_dict, None
    except ET.ParseError as eroare_xml:
        return None, f"EROARE la parsarea XML: {str(eroare_xml)}"

def proceseaza_date_text_simplu(cerere):
    try:
        text_brut = cerere.data.decode('utf-8').strip()
        parti = text_brut.split(',')
        date_text = {}
        for p in parti:
            p_curat = p.strip()
            if '=' in p_curat:
                nume_camp, valoare_camp = p_curat.split('=', 1)
                nume_camp = nume_camp.strip()
                valoare_camp = valoare_camp.strip()
                date_text[nume_camp] = valoare_camp
        if "cheie" not in date_text:
            return None, "EROARE: In text trebuie sa existe 'cheie=valoare'."
        return date_text, None
    except Exception as e:
        return None, f"EROARE la procesarea textului: {str(e)}"

def proceseaza_payload_in_functie_de_tip(cerere):
    tip_date_input = cerere.headers.get('Content-Type', '').lower()

    if tip_date_input == TIP_DATE_JSON:
        return proceseaza_date_json(cerere)
    elif tip_date_input == TIP_DATE_XML:
        return proceseaza_date_xml(cerere)
    elif tip_date_input == TIP_DATE_TEXT_SIMPLU:
        return proceseaza_date_text_simplu(cerere)
    else:
        return None, f"EROARE: Tip de date necunoscut {tip_date_input}"

@app.route('/')
def pagina_principala():
    return jsonify({
        "mesaj": "API local",
        "instructiuni": {
            "descriere": "Puteti trimite date in JSON, XML sau text simplu.",
            "detalii": [
                "Pentru POST si PUT, trebuie neaparat campul 'cheie' in payload.",
                "Exemple payload valide:",
                "- JSON: {\"cheie\": \"123\", \"nume\": \"Aida\"}",
                "- XML: <root><cheie>123</cheie><nume>Aida</nume></root>",
                "- Text: cheie=123, nume=Aida"
            ]
        },
        "rute disponibile": {
            "GET /date": "Obtine toate datele",
            "POST /date": "Adauga date noi",
            "PUT /date": "Actualizeaza sau creeaza date",
            "DELETE /date": "Sterge toate datele"
        }
    })

if __name__ == '__main__':
    app.run(debug=True)
