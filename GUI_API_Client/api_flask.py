from flask import Flask, request, jsonify
import xml.etree.ElementTree as ET  #pt a parsa fisiere XML

#definesc constante pentru tipurile de date acceptate
TIP_DATE_JSON = 'application/json'
TIP_DATE_XML = 'application/xml'
TIP_DATE_TEXT_SIMPLU = 'text/plain'

app = Flask(__name__)

#simulez o baza de date, ca sa stochez aici datele primite
lista_de_date_stocate = []

#obtin datele din cerere ca JSON
def proceseaza_date_json(cerere):
    try:
        date_json = cerere.get_json()
        if "cheie" not in date_json:
            return None, "EROARE: In JSON trebuie sa introduci campul 'cheie'!!"
        return date_json, None
    except Exception as eroare:
        return None, f"EROARE la parsarea JSON: {str(eroare)}"

#parsez payload ul ca XML, extrag elementele si le pun intr un dictionar
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

#parsez datele trimise ca text simplu (o sa aiba forma "cheie=123, nume=Aida")
def proceseaza_date_text_simplu(cerere):
    try:
        text_brut = cerere.data.decode('utf-8').strip()
        parti = text_brut.split(',') #impart dupa virgula si apoi fiecare pereche dupa =
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

#determin tipul de date primite si apelez functiile corespunzatoare
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

#returnez toate datele stocate, sub forma de JSON
def returneaza_toate_datele():
    return jsonify({
        "mesaj": "Cerere GET realizata cu succes!",
        "istoric_date": lista_de_date_stocate
    })

def adauga_date_noi(date_primite):
    for resursa in lista_de_date_stocate:
        if resursa["date"].get("cheie") == date_primite.get("cheie"):
            return jsonify({"mesaj": f"Cheia '{date_primite['cheie']}' exista deja, alegeti alta cheie!"}), 400

    lista_de_date_stocate.append({"metoda": "POST", "date": date_primite})
    return jsonify({"mesaj": "Date adaugate cu succes!", "date_adaugate": date_primite}), 201

def actualizeaza_sau_creeaza(date_primite):
    resursa_gasita = False
    for resursa in lista_de_date_stocate:
        if resursa["date"].get("cheie") == date_primite.get("cheie"):
            resursa["date"] = date_primite
            resursa_gasita = True
            break

    if resursa_gasita:
        return jsonify({"mesaj": "Date actualizate cu succes!", "date_actualizate": date_primite}), 200
    else:
        lista_de_date_stocate.append({"metoda": "PUT", "date": date_primite})
        return jsonify({"mesaj": "Cheia nu exista, resursa noua a fost creata!", "date_adaugate": date_primite}), 201

#sterg toate datele din lista
def sterge_toate_datele():
    lista_de_date_stocate.clear()
    return jsonify({"mesaj": "Toate datele au fost sterse cu succes!"}), 200

#rutele API
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

@app.route('/date', methods=['GET'])
def ruta_get_date():
    return returneaza_toate_datele()

@app.route('/date', methods=['POST'])
def ruta_post_date():
    date_primite, eroare = proceseaza_payload_in_functie_de_tip(request)
    if eroare:
        return jsonify({"mesaj": eroare}), 400
    if not date_primite:
        return jsonify({"mesaj": "EROARE: pentru POST, payload-ul este obligatoriu!!"}), 400

    if "cheie" not in date_primite:
        return jsonify({"mesaj": "EROARE: Trebuie introdus campul 'cheie' in payload!!"}), 400

    #verific cheie unica (fac in functie)
    return adauga_date_noi(date_primite)

@app.route('/date', methods=['PUT'])
def ruta_put_date():
    date_primite, eroare = proceseaza_payload_in_functie_de_tip(request)
    if eroare:
        return jsonify({"mesaj": eroare}), 400
    if not date_primite:
        return jsonify({"mesaj": "EROARE: pentru PUT, payload-ul este obligatoriu!!"}), 400

    if "cheie" not in date_primite:
        return jsonify({"mesaj": "EROARE: Trebuie introdus campul 'cheie' in payload pentru PUT!!"}), 400

    return actualizeaza_sau_creeaza(date_primite)

@app.route('/date', methods=['DELETE'])
def ruta_delete_date():
    return sterge_toate_datele()

if __name__ == '__main__':
    app.run(debug=True)
