import requests
import json
import re
import xml.etree.ElementTree as ET

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