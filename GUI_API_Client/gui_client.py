import requests
import json
import re
import xml.etree.ElementTree as ET

#definesc tipurile de continut pe care le pot trimite
TIPURI_CONTINUT = {
    "json": "application/json",
    "xml": "application/xml",
    "text": "text/plain"
}

#vad daca adresa URL are un format corect, daca incepe cu http:// sau https://
def verifica_format_ulr(adresa_url):
    model_url = re.compile(
        r"^(http|https)://"
        r"(([\w-]+\.)?[\w-]+|"
        r"(\d{1,3}\.){3}\d{1,3})"
        r"(:\d+)?(/.*)?$"
    )
    return bool(model_url.match(adresa_url))

#folosesc o cerere HEAD sa vad daca site ul raspunde cu un cod de status mai mic decat 400
#daca da, e accesibil
def verifica_accesibilitate_url(adresa_url):
    try:
        raspuns = requests.head(adresa_url, timeout=5)
        return raspuns.status_code < 400
    except requests.RequestException:
        return False

def proceseaza_antet_json(antet):
    try:
        return json.loads(antet) if antet else {}
    except json.JSONDecodeError:
        raise ValueError("Header JSON invalid")

def valideaza_payload_in_functie_de_tip(payload, tip_continut):
    if not payload.strip():
        return None

    if tip_continut == TIPURI_CONTINUT["json"]:
        try:
            obj_json = json.loads(payload)
            return obj_json
        except json.JSONDecodeError:
            raise ValueError("Payload JSON NU este valid!!")
    elif tip_continut == TIPURI_CONTINUT["xml"]:
        try:
            ET.fromstring(payload)
            return payload
        except ET.ParseError:
            raise ValueError("Payload XML NU este valid!!")
    else:
        return payload.strip()

def construieste_header_pentru_format(tip_format):
    if tip_format == "JSON":
        return {"Content-Type": "application/json"}
    elif tip_format == "XML":
        return {"Content-Type": "application/xml"}
    elif tip_format == "text/plain":
        return {"Content-Type": "text/plain"}
    else:
        raise ValueError(f"Format necunoscut: {tip_format}")

def trimite_cerere_get(adresa_url, antet):
    return requests.get(adresa_url, headers=antet)

def trimite_cerere_post(adresa_url, antet, payload):
    if antet.get("Content-Type") == TIPURI_CONTINUT["json"]:
        return requests.post(adresa_url, headers=antet, json=payload)
    else:
        return requests.post(adresa_url, headers=antet, data=payload)

def trimite_cerere_put(adresa_url, antet, payload):
    if antet.get("Content-Type") == TIPURI_CONTINUT["json"]:
        return requests.put(adresa_url, headers=antet, json=payload)
    else:
        return requests.put(adresa_url, headers=antet, data=payload)

def trimite_cerere_delete(adresa_url, antet):
    return requests.delete(adresa_url, headers=antet)

def trimite_cerere_la_server(metoda_http, adresa_url, antet, payload):
    try:
        if metoda_http == "GET":
            raspuns = trimite_cerere_get(adresa_url, antet)
            print(f"Raspuns GET: {raspuns.status_code}, {raspuns.text}")
            return None, raspuns
        elif metoda_http == "DELETE":
            raspuns = trimite_cerere_delete(adresa_url, antet)
            print(f"Raspuns DELETE: {raspuns.status_code}, {raspuns.text}")
            return None, raspuns
        elif metoda_http == "POST":
            if not payload:
                return "EROARE: Pentru POST, payload-ul este obligatoriu!!", None
            raspuns = trimite_cerere_post(adresa_url, antet, payload)
            print(f"Raspuns POST: {raspuns.status_code}, {raspuns.text}")
            return None, raspuns
        elif metoda_http == "PUT":
            if not payload:
                return "EROARE: Pentru PUT, payload-ul este obligatoriu!!", None
            raspuns = trimite_cerere_put(adresa_url, antet, payload)
            print(f"Raspuns PUT: {raspuns.status_code}, {raspuns.text}")
            return None, raspuns
        else:
            return "EROARE: Metoda HTTP NU este valida!!", None
    except requests.exceptions.RequestException as e:
        return f"EROARE la trimiterea cererii: {str(e)}", None
