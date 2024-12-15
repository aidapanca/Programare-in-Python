import tkinter as tk
from tkinter import ttk, messagebox
from gui_client import trimite_cerere_la_server, scrie_istoric_in_fisier, incarca_istoric_din_fisier
import xml.etree.ElementTree as ET
import json

CULOARE_FUNDAL = "#282c34"
CULOARE_FUNDAL_INPUT = "#3c3f41"
CULOARE_TEXT = "#ffffff"
CULOARE_BUTON = "#61afef"
FONT_TITLU = ("Verdana", 12, "bold")
FONT_CONTINUT = ("Courier", 10)

istoric_cereri = []

#fereastra principala
def initializeaza_fereastra():
    fereastra = tk.Tk()
    fereastra.title("Client GUI API") #titlu
    fereastra.geometry("850x700") #dimensiune
    fereastra.configure(bg=CULOARE_FUNDAL) #culoare fundal
    return fereastra

#sectiune pt CERERE - metoda, URL, header, payload
def creeaza_sectiune_cerere(fereastra):
    sectiune = tk.LabelFrame(fereastra, text="CERERE", bg=CULOARE_FUNDAL, fg=CULOARE_TEXT, font=FONT_TITLU)
    sectiune.pack(pady=15, padx=20, fill=tk.X)
    return sectiune

def creeaza_sectiune_raspuns(fereastra):
    sectiune = tk.LabelFrame(fereastra, text="RASPUNS", bg=CULOARE_FUNDAL, fg=CULOARE_TEXT, font=FONT_TITLU)
    sectiune.pack(pady=10, padx=20, fill=tk.BOTH, expand=True)

    zona = tk.Text(sectiune, height=12, width=80, bg=CULOARE_FUNDAL_INPUT, fg=CULOARE_TEXT, font=FONT_CONTINUT)
    zona.pack(fill=tk.BOTH, expand=True)
    return sectiune, zona

def creeaza_sectiune_istoric(fereastra):
    sectiune = tk.LabelFrame(fereastra, text="ISTORIC", bg=CULOARE_FUNDAL, fg=CULOARE_TEXT, font=FONT_TITLU)
    sectiune.pack(pady=10, padx=20, fill=tk.BOTH, expand=True)

    frame_lista = tk.Frame(sectiune, bg=CULOARE_FUNDAL)
    frame_lista.pack(fill=tk.BOTH, expand=True)

    lista = tk.Listbox(frame_lista, width=80, height=8, bg=CULOARE_FUNDAL_INPUT, fg=CULOARE_TEXT, font=FONT_CONTINUT)
    lista.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    scrollbar = tk.Scrollbar(frame_lista)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    lista.config(yscrollcommand=scrollbar.set)
    scrollbar.config(command=lista.yview)

    frame_buton = tk.Frame(sectiune, bg=CULOARE_FUNDAL)
    frame_buton.pack(fill=tk.X)

    buton_vizualizeaza = tk.Button(frame_buton, text="VEZI RASPUNS ISTORIC", command=vizualizeaza_raspuns_istoric, bg=CULOARE_BUTON, fg=CULOARE_TEXT)
    buton_vizualizeaza.pack(pady=5, anchor="e")

    return sectiune, lista

def creeaza_buton_trimite(sectiune, comanda):
    buton = tk.Button(sectiune, text="TRIMITE", command=comanda, bg=CULOARE_BUTON, fg=CULOARE_TEXT, font=("Verdana", 10, "bold"))
    buton.grid(row=0, column=2, rowspan=4, padx=10, pady=10, sticky="nsew")
    return buton

def construieste_header(tip_format):
    if tip_format == "JSON":
        return {"Content-Type": "application/json"}
    elif tip_format == "XML":
        return {"Content-Type": "application/xml"}
    return {"Content-Type": "text/plain"}

def actualizeaza_istoric_fara_raspuns(metoda, url, mesaj_eroare):
    cerere = {
        "method": metoda,
        "url": url,
        "status_code": None,
        "response_text": mesaj_eroare
    }
    istoric_cereri.append(cerere)

    intrare_istoric = f"{metoda} {url} -> EROARE"
    lista_istoric.insert(tk.END, intrare_istoric)

    intrari = lista_istoric.get(0, tk.END)
    MAX_ISTORIC = 1000
    if len(intrari) > MAX_ISTORIC:
        istoric_cereri[:] = istoric_cereri[-MAX_ISTORIC:]
        intrari = intrari[-MAX_ISTORIC:]
        lista_istoric.delete(0, tk.END)
        for intrare in intrari:
            lista_istoric.insert(tk.END, intrare)

    scrie_istoric_in_fisier(istoric_cereri)

def gestioneaza_cerere():
    metoda_http = optiune_metoda.get()
    adresa_url = camp_url.get()
    tip_format = format_var.get()
    payload = camp_payload.get()

    zona_raspuns.delete(1.0, tk.END)

    if metoda_http in ["GET", "DELETE"]:
        header = construieste_header(tip_format)
        mesaj_eroare, raspuns = trimite_cerere_la_server(metoda_http, adresa_url, header, None)

        if mesaj_eroare:
            zona_raspuns.configure(bg="#8B0000")
            zona_raspuns.insert(tk.END, f"EROARE: {mesaj_eroare}\n")
            if raspuns is None:
                actualizeaza_istoric_fara_raspuns(metoda_http, adresa_url, mesaj_eroare)
            return
        elif raspuns:
            if raspuns.status_code >= 400:
                zona_raspuns.configure(bg="#8B0000")
                try:
                    eroare_mesaj = raspuns.json().get("mesaj", "EROARE")
                    zona_raspuns.insert(tk.END,f"STATUS: {raspuns.status_code} {raspuns.reason}\nMESAJ: {eroare_mesaj}\n")
                except Exception:
                    zona_raspuns.insert(tk.END, f"STATUS: {raspuns.status_code} {raspuns.reason}\n{raspuns.text}\n")
            else:
                zona_raspuns.configure(bg="#006400")
                try:
                    if "application/json" in raspuns.headers.get("Content-Type", ""):
                        raspuns_text = json.dumps(raspuns.json(), indent=2)
                    else:
                        raspuns_text = raspuns.text
                    zona_raspuns.insert(tk.END, f"STATUS: {raspuns.status_code} {raspuns.reason}\n{raspuns_text}\n")
                except Exception:
                    zona_raspuns.insert(tk.END, f"STATUS: {raspuns.status_code} {raspuns.reason}\n{raspuns.text}\n")

            actualizeaza_istoric(metoda_http, adresa_url, raspuns)
        else:
            zona_raspuns.configure(bg="#8B0000")
            zona_raspuns.insert(tk.END, "EROARE!\n")
            actualizeaza_istoric_fara_raspuns(metoda_http, adresa_url, "EROARE")
        return

    if metoda_http in ["POST", "PUT"] and not payload.strip():
        zona_raspuns.configure(bg="#8B0000")
        zona_raspuns.insert(tk.END, f"EROARE: Pentru {metoda_http}, payload este obligatoriu!!!\n")
        actualizeaza_istoric_fara_raspuns(metoda_http, adresa_url, "Lipseste payload pentru POST/PUT")
        return

    #validare locala pentru POST/PUT in functie de formatul selectat
    #ca si inainte, doar afisez erorile. Daca e eroare, nu trimit cererea mai departe
    if metoda_http in ["POST", "PUT"]:
        if tip_format == "JSON":
            try:
                obj = json.loads(payload)
                if "cheie" not in obj:
                    zona_raspuns.configure(bg="#8B0000")
                    zona_raspuns.insert(tk.END, "JSON INVALID: trebuie introdus campul 'cheie'!!\n")
                    actualizeaza_istoric_fara_raspuns(metoda_http, adresa_url, "JSON invalid: lipseste 'cheie'")
                    return
            except json.JSONDecodeError:
                zona_raspuns.configure(bg="#8B0000")
                zona_raspuns.insert(tk.END, "Payload JSON NU este valid!!\n")
                actualizeaza_istoric_fara_raspuns(metoda_http, adresa_url, "JSON invalid (eroare locala)")
                return
        elif tip_format == "XML":
            try:
                radacina = ET.fromstring(payload)
                cheie_element = radacina.find("cheie")
                if cheie_element is None or not cheie_element.text.strip():
                    zona_raspuns.configure(bg="#8B0000")
                    zona_raspuns.insert(tk.END, "XML INVALID: trebuie elementul <cheie>!!\n")
                    actualizeaza_istoric_fara_raspuns(metoda_http, adresa_url, "XML invalid: lipseste <cheie>")
                    return
            except ET.ParseError:
                zona_raspuns.configure(bg="#8B0000")
                zona_raspuns.insert(tk.END, "Payload XML NU este valid!!\n")
                actualizeaza_istoric_fara_raspuns(metoda_http, adresa_url, "XML invalid (eroare locala)")
                return
        else:
            if "cheie=" not in payload:
                zona_raspuns.configure(bg="#8B0000")
                zona_raspuns.insert(tk.END, "TEXT INVALID: trebuie 'cheie=valoare'.\n")
                actualizeaza_istoric_fara_raspuns(metoda_http, adresa_url, "Text invalid: lipseste 'cheie='")
                return

    #daca am ajuns aici, payload ul e valid local. trimit cererea la server
    header = construieste_header(tip_format)
    #daca e JSON, transform payload ul in obiect python inainte de trimitere
    if tip_format == "JSON":
        payload = json.loads(payload)

    mesaj_eroare, raspuns = trimite_cerere_la_server(metoda_http, adresa_url, header, payload)
    zona_raspuns.delete(1.0, tk.END)

    if mesaj_eroare:
        zona_raspuns.configure(bg="#8B0000")
        zona_raspuns.insert(tk.END, f"EROARE: {mesaj_eroare}\n")
        if raspuns is None:
            actualizeaza_istoric_fara_raspuns(metoda_http, adresa_url, mesaj_eroare)
        return
    elif raspuns:
        if raspuns.status_code >= 400:
            zona_raspuns.configure(bg="#8B0000")
            try:
                eroare_mesaj = raspuns.json().get("mesaj", "EROARE")
                zona_raspuns.insert(tk.END, f"STATUS: {raspuns.status_code} {raspuns.reason}\nMESAJ: {eroare_mesaj}\n")
            except Exception:
                zona_raspuns.insert(tk.END, f"STATUS: {raspuns.status_code} {raspuns.reason}\n{raspuns.text}\n")
        else:
            zona_raspuns.configure(bg="#006400")
            try:
                if "application/json" in raspuns.headers.get("Content-Type", ""):
                    raspuns_text = json.dumps(raspuns.json(), indent=2)
                else:
                    raspuns_text = raspuns.text
                zona_raspuns.insert(tk.END, f"STATUS: {raspuns.status_code} {raspuns.reason}\n{raspuns_text}\n")
            except Exception:
                zona_raspuns.insert(tk.END, f"STATUS: {raspuns.status_code} {raspuns.reason}\n{raspuns.text}\n")

        actualizeaza_istoric(metoda_http, adresa_url, raspuns)
    else:
        zona_raspuns.configure(bg="#8B0000")
        zona_raspuns.insert(tk.END, "EROARE\n")
        actualizeaza_istoric_fara_raspuns(metoda_http, adresa_url, "EROARE")


def actualizeaza_istoric(metoda, url, raspuns):
    continut_raspuns = raspuns.text
    status_code = raspuns.status_code
    cerere = {
        "method": metoda,
        "url": url,
        "status_code": status_code,
        "response_text": continut_raspuns
    }

    istoric_cereri.append(cerere)
    intrare_istoric = f"{metoda} {url} -> {status_code}"
    lista_istoric.insert(tk.END, intrare_istoric)

    intrari = lista_istoric.get(0, tk.END)
    MAX_ISTORIC = 1000
    if len(intrari) > MAX_ISTORIC:
        istoric_cereri[:] = istoric_cereri[-MAX_ISTORIC:]
        intrari = intrari[-MAX_ISTORIC:]
        lista_istoric.delete(0, tk.END)
        for intrare in intrari:
            lista_istoric.insert(tk.END, intrare)

    scrie_istoric_in_fisier(istoric_cereri)

def incarca_istoric_in_interfata():
    global istoric_cereri
    cereri = incarca_istoric_din_fisier()
    if cereri:
        istoric_cereri = cereri
        for cerere in cereri:
            intrare_istoric = f"{cerere['method']} {cerere['url']} -> {cerere['status_code']}"
            lista_istoric.insert(tk.END, intrare_istoric)
    else:
        istoric_cereri = []

def vizualizeaza_raspuns_istoric():
    #fct apelata cand utilizatorul vrea sa vada raspunsul unei cereri din istoric
    sel = lista_istoric.curselection()
    if not sel:
        messagebox.showinfo("Info", "Trebuie sa selectezi o cerere din istoric!")
        return
    index = sel[0]
    cerere = istoric_cereri[index]
    #afisez raspunsul in zona de raspuns
    zona_raspuns.delete(1.0, tk.END)

    #verific statusul
    cod_status = cerere['status_code']
    if cod_status is None or (isinstance(cod_status, int) and cod_status >= 400):
        #eroare sau cod status mare, pun fundal rosu
        zona_raspuns.configure(bg="#8B0000")
    else:
        #cerere de succes
        zona_raspuns.configure(bg="#006400")

    zona_raspuns.insert(tk.END, f"STATUS: {cod_status}\n{cerere['response_text']}\n")

def actualizeaza_campuri(*args):
    metoda_http = optiune_metoda.get()
    if metoda_http in ["GET", "DELETE"]:
        camp_payload.configure(state="disabled")
        selector_format_headers.configure(state="disabled")
    else:
        camp_payload.configure(state="normal")
        selector_format_headers.configure(state="readonly")

def main():
    global optiune_metoda, camp_url, format_var, camp_payload, lista_istoric, zona_raspuns, selector_format_headers

    fereastra = initializeaza_fereastra()
    sectiune_cerere = creeaza_sectiune_cerere(fereastra)

    tk.Label(sectiune_cerere, text="Metoda HTTP:", bg=CULOARE_FUNDAL, fg=CULOARE_TEXT).grid(row=0, column=0, padx=10, pady=5, sticky="w")
    optiune_metoda = tk.StringVar(value="GET")
    ttk.Combobox(sectiune_cerere, textvariable=optiune_metoda, values=["GET", "POST", "PUT", "DELETE"], state="readonly").grid(row=0, column=1, padx=10, pady=5, sticky="w")
    optiune_metoda.trace("w", actualizeaza_campuri)

    tk.Label(sectiune_cerere, text="URL:", bg=CULOARE_FUNDAL, fg=CULOARE_TEXT).grid(row=1, column=0, padx=10, pady=5, sticky="w")
    camp_url = tk.Entry(sectiune_cerere, width=60)
    camp_url.grid(row=1, column=1, padx=10, pady=5, sticky="w")

    tk.Label(sectiune_cerere, text="Headers (format):", bg=CULOARE_FUNDAL, fg=CULOARE_TEXT).grid(row=2, column=0, padx=10, pady=5, sticky="w")
    format_var = tk.StringVar(value="JSON")
    selector_format_headers = ttk.Combobox(sectiune_cerere, textvariable=format_var, values=["JSON", "XML", "Text simplu"], state="readonly")
    selector_format_headers.grid(row=2, column=1, padx=10, pady=5, sticky="w")

    tk.Label(sectiune_cerere, text="Payload:", bg=CULOARE_FUNDAL, fg=CULOARE_TEXT).grid(row=3, column=0, padx=10, pady=5, sticky="w")
    camp_payload = tk.Entry(sectiune_cerere, width=60)
    camp_payload.grid(row=3, column=1, padx=10, pady=5, sticky="w")

    creeaza_buton_trimite(sectiune_cerere, gestioneaza_cerere)

    _, zona_raspuns = creeaza_sectiune_raspuns(fereastra)
    _, lista_istoric = creeaza_sectiune_istoric(fereastra)
    incarca_istoric_in_interfata()
    actualizeaza_campuri()

    fereastra.mainloop()

if __name__ == "__main__":
    main()
