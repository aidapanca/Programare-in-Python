from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/')
def pagina_principala():
    return jsonify({
        "mesaj": "PAGINA PRINCIPALA A ACESTUI API local! RUTE DISPONIBILE:",
        "rute": {
            "GET /date": "OBTINE date de la server",
            "POST /date": "TRIMITE date noi catre server pentru a fi create",
            "PUT /date": "ACTUALIZEAZA date existente sau le CREEAZA daca nu exista",
            "DELETE /date": "STERGE date de pe server"
        }
    })

if __name__ == '__main__':
    app.run(debug=True)