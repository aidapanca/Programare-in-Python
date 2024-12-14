import tkinter as tk
from tkinter import ttk, messagebox
from gui_client import incarca_istoric_din_fisier

CULOARE_FUNDAL = "#282c34"
CULOARE_FUNDAL_INPUT = "#3c3f41"
CULOARE_TEXT = "#ffffff"
CULOARE_BUTON = "#61afef"
FONT_TITLU = ("Verdana", 12, "bold")
FONT_CONTINUT = ("Courier", 10)

istoric_cereri = []

def initializeaza_fereastra():
    fereastra = tk.Tk()
    fereastra.title("Client GUI API")
    fereastra.geometry("850x700")
    fereastra.configure(bg=CULOARE_FUNDAL)
    return fereastra

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

def creeaza_buton_trimite(sectiune, comanda):
    buton = tk.Button(sectiune, text="TRIMITE", command=comanda, bg=CULOARE_BUTON, fg=CULOARE_TEXT, font=("Verdana", 10, "bold"))
    buton.grid(row=0, column=2, rowspan=4, padx=10, pady=10, sticky="nsew")
    return buton

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

def main():
    global optiune_metoda, camp_url, format_var, camp_payload, lista_istoric, zona_raspuns, selector_format_headers

    fereastra = initializeaza_fereastra()
    sectiune_cerere = creeaza_sectiune_cerere(fereastra)

    tk.Label(sectiune_cerere, text="Metoda HTTP:", bg=CULOARE_FUNDAL, fg=CULOARE_TEXT).grid(row=0, column=0, padx=10, pady=5, sticky="w")
    optiune_metoda = tk.StringVar(value="GET")
    ttk.Combobox(sectiune_cerere, textvariable=optiune_metoda, values=["GET", "POST", "PUT", "DELETE"], state="readonly").grid(row=0, column=1, padx=10, pady=5, sticky="w")

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

    creeaza_buton_trimite(sectiune_cerere, None)

    _, zona_raspuns = creeaza_sectiune_raspuns(fereastra)

    fereastra.mainloop()

if __name__ == "__main__":
    main()
