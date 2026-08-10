from flask import Flask, request, jsonify
import jwt
import os
from db.mongo import images, db

app = Flask(__name__)

SECRET_KEY = "supersecret"
BASE_PATH = "images"


def extract_token():
    auth_header = request.headers.get("Authorization")

    if not auth_header:
        return None

    if auth_header.startswith("Bearer "):
        return auth_header.split(" ", 1)[1]

    return auth_header


def verify_token(token):
    if not token:
        return None

    try:
        decoded = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return decoded
    except Exception:
        return None


@app.route("/images", methods=["POST"])
def get_images():
    try:
        token = extract_token()
        decoded = verify_token(token)

        if not decoded:
            return jsonify({"error": "Token non valido o mancante"}), 403

        data = request.get_json()

        if not data:
            return jsonify({"error": "JSON mancante"}), 400

        tipo = data.get("tipoImmagine")

        if not tipo:
            return jsonify({"error": "tipoImmagine mancante"}), 400

        
        _api_dir = os.path.dirname(os.path.abspath(__file__))
        possibili = [
            os.path.join("/app/images", tipo),                                  
            os.path.join(_api_dir, "..", "images", tipo),                       
            os.path.join(os.path.abspath(BASE_PATH), tipo),                     
        ]

        for path in possibili:
            path = os.path.abspath(path)
            if os.path.isdir(path):
                files = [f for f in os.listdir(path)
                         if os.path.isfile(os.path.join(path, f))]
                print(f"✅ /images POST: trovata cartella {path} ({len(files)} file)")
                return jsonify({"images": files}), 200

        print(f"⚠️  /images POST: cartella '{tipo}' non trovata in nessun percorso")
        return jsonify({"images": []}), 200

    except Exception as e:
        print("ERRORE /images:", e)
        return jsonify({"error": str(e)}), 500


@app.route("/metadata", methods=["POST"])
def get_metadata():
    try:
        token = extract_token()
        decoded = verify_token(token)

        if not decoded:
            return jsonify({"error": "Token non valido o mancante"}), 403

        data = request.get_json()

        if not data:
            return jsonify({"error": "JSON mancante"}), 400

        filename = data.get("filename")

        if not filename:
            return jsonify({"error": "filename mancante"}), 400

        
        meta = images.find_one({"filename": filename}, {"_id": 0})

        if not meta:
            nuovi_dati = db["nuovi_dati"]
            meta = nuovi_dati.find_one({"filename": filename}, {"_id": 0})

        if not meta:
            return jsonify({"error": "Metadata non trovato"}), 404

        return jsonify(meta), 200

    except Exception as e:
        print("ERRORE /metadata:", e)
        return jsonify({"error": str(e)}), 500



@app.route("/nuovi-dati", methods=["POST"])
def salva_nuovi_dati():
    try:
        token = extract_token()
        decoded = verify_token(token)

        if not decoded:
            return jsonify({"error": "Token non valido o mancante"}), 403

        data = request.get_json()
        if not data:
            return jsonify({"error": "JSON mancante"}), 400

        nuovi_dati = db["nuovi_dati"]

        
        nuovi_dati.update_one(
            {"filename": data.get("filename")},
            {"$set": data},
            upsert=True
        )

        return jsonify({"ok": True, "filename": data.get("filename")}), 200

    except Exception as e:
        print("ERRORE /nuovi-dati:", e)
        return jsonify({"error": str(e)}), 500



@app.route("/simili", methods=["POST"])
def trova_simili():
    try:
        token = extract_token()
        decoded = verify_token(token)

        if not decoded:
            return jsonify({"error": "Token non valido o mancante"}), 403

        data = request.get_json()
        if not data:
            return jsonify({"error": "JSON mancante"}), 400

        tipologia = data.get("tipologia", "altro")

        
        _mappa = {
            "persone": ["persone"],
            "auto":    ["auto"],
            "treni":   ["treni"],
            "aerei":   ["aerei"],
            "altro":   []
        }

        simili = []

        
        nuovi_dati = db["nuovi_dati"]
        if tipologia == "persone":
            query = {"persone": {"$gt": 0}}
        elif tipologia == "auto":
            query = {"$or": [{"dettaglio.car": {"$exists": True}},
                             {"dettaglio.truck": {"$exists": True}},
                             {"dettaglio.bus": {"$exists": True}},
                             {"dettaglio.motorcycle": {"$exists": True}}]}
        elif tipologia == "treni":
            query = {"dettaglio.train": {"$exists": True}}
        elif tipologia == "aerei":
            query = {"$or": [{"dettaglio.airplane": {"$exists": True}},
                             {"dettaglio.aircraft": {"$exists": True}}]}
        elif tipologia == "oggetti":
            query = {"oggetti": {"$gt": 0}}
        elif tipologia == "altro":
            
            query = {
                "persone": 0,
                "dettaglio.car": {"$exists": False},
                "dettaglio.truck": {"$exists": False},
                "dettaglio.bus": {"$exists": False},
                "dettaglio.motorcycle": {"$exists": False},
                "dettaglio.train": {"$exists": False},
                "dettaglio.airplane": {"$exists": False},
            }
        else:
            query = {}

        for doc in nuovi_dati.find(query, {"_id": 0, "filename": 1, "descrizione": 1}):
            doc["fonte"] = "nuovi_dati"
            simili.append(doc)

        
        tipo_map = {
            "persone": "persona",
            "auto":    "auto",
            "treni":   "treno",
            "aerei":   "aereo",
            "altro":   "altro",
            "oggetti": "altro",
        }
        tipo_singolare = tipo_map.get(tipologia)
        if tipo_singolare:
            
            for doc in images.find(
                {"tipo": tipo_singolare},
                {"_id": 0, "filename": 1}
            ):
                doc["fonte"] = "images"
                simili.append(doc)

        return jsonify({"tipologia": tipologia, "simili": simili}), 200

    except Exception as e:
        print("ERRORE /simili:", e)
        return jsonify({"error": str(e)}), 500


@app.route("/nuovi-dati/lista", methods=["GET"])
def lista_nuovi_dati():
    """Ritorna la lista di tutti i filename presenti in nuovi_dati."""
    try:
        token = extract_token()
        if not verify_token(token):
            return jsonify({"error": "Token non valido o mancante"}), 403
        nuovi_dati = db["nuovi_dati"]
        filenames = [d["filename"] for d in nuovi_dati.find({}, {"_id": 0, "filename": 1})]
        return jsonify({"ok": True, "filenames": filenames}), 200
    except Exception as e:
        print("ERRORE /nuovi-dati/lista:", e)
        return jsonify({"error": str(e)}), 500


@app.route("/nuovi-dati/elimina", methods=["POST"])
def elimina_nuovi_dati():
    """Rimuove un singolo documento da nuovi_dati dato il filename."""
    try:
        token = extract_token()
        if not verify_token(token):
            return jsonify({"error": "Token non valido o mancante"}), 403
        data = request.get_json()
        if not data or not data.get("filename"):
            return jsonify({"error": "filename mancante"}), 400
        nuovi_dati = db["nuovi_dati"]
        risultato = nuovi_dati.delete_one({"filename": data["filename"]})
        if risultato.deleted_count > 0:
            return jsonify({"ok": True, "eliminato": data["filename"]}), 200
        return jsonify({"ok": False, "messaggio": "Documento non trovato"}), 404
    except Exception as e:
        print("ERRORE /nuovi-dati/elimina:", e)
        return jsonify({"error": str(e)}), 500


@app.route("/nuovi-dati/elimina-batch", methods=["POST"])
def elimina_batch_nuovi_dati():
    """Rimuove più documenti da nuovi_dati dati una lista di filenames."""
    try:
        token = extract_token()
        if not verify_token(token):
            return jsonify({"error": "Token non valido o mancante"}), 403
        data = request.get_json()
        if not data or "filenames" not in data:
            return jsonify({"error": "Lista filenames mancante"}), 400
        filenames = data["filenames"]
        if not isinstance(filenames, list) or len(filenames) == 0:
            return jsonify({"ok": True, "eliminati": 0}), 200
        nuovi_dati = db["nuovi_dati"]
        risultato = nuovi_dati.delete_many({"filename": {"$in": filenames}})
        print(f"🗑️  elimina-batch: rimossi {risultato.deleted_count} doc da nuovi_dati")
        return jsonify({"ok": True, "eliminati": risultato.deleted_count}), 200
    except Exception as e:
        print("ERRORE /nuovi-dati/elimina-batch:", e)
        return jsonify({"error": str(e)}), 500


@app.route("/images/<filename>", methods=["GET"])
def serve_image(filename):
    """
    Restituisce il file binario cercandolo ricorsivamente in images/ e downloads/.
    Usato da 'Scarica Simili' e 'Scarica tutte dal server'.
    """
    from flask import send_file, abort

    try:
        
        if "/" in filename or "\\" in filename or ".." in filename:
            abort(400)

        _api_dir = os.path.dirname(os.path.abspath(__file__))

        
        radici = [
            "/app/images",
            "/app/downloads",
            os.path.join(_api_dir, "..", "images"),
            os.path.join(_api_dir, "..", "downloads"),
            os.path.abspath(BASE_PATH),
            os.path.abspath("downloads"),
        ]

        
        for radice in radici:
            radice = os.path.abspath(radice)
            if not os.path.isdir(radice):
                continue
            for dirpath, _, files in os.walk(radice):
                if filename in files:
                    trovato = os.path.join(dirpath, filename)
                    print(f"✅ Trovato: {trovato}")
                    return send_file(trovato)

        print(f"❌ NOT FOUND: {filename}")
        abort(404)

    except Exception as e:
        print(f"ERRORE /images/{filename}:", e)
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="::", port=5001, debug=True)