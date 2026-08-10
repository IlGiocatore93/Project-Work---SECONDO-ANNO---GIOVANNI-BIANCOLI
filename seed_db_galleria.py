"""
seed_db_galleria.py — Popola MongoDB con metadata dei film.

Esegui con:
  python seed_db_galleria.py                        ← localhost (sviluppo)
  docker compose exec auth_api python seed_db_galleria.py   ← dentro Docker

Il campo `created_at` viene aggiunto automaticamente a ogni documento:
registra data e ora esatta di inserimento nel formato ISO 8601 (UTC).
"""

import os
import sys
import uuid
from datetime import datetime
try:
    from zoneinfo import ZoneInfo
    _TZ_IT = ZoneInfo("Europe/Rome")
except Exception:
    _TZ_IT = None
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError


_app_name  = f"myapp-seed-{uuid.uuid4().hex[:8]}"  
_mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017/")


if "?" in _mongo_uri:
    _mongo_uri_named = f"{_mongo_uri}&appName={_app_name}"
else:
    _mongo_uri_named = f"{_mongo_uri}?appName={_app_name}"

print(f"🔌 Connessione a: {_mongo_uri}  [appName={_app_name}]")

try:
    client = MongoClient(_mongo_uri_named, serverSelectionTimeoutMS=5000)
    client.admin.command("ping")         
    print("✅ Connessione MongoDB riuscita")
except (ConnectionFailure, ServerSelectionTimeoutError) as e:
    print(f"❌ Impossibile connettersi a MongoDB → {e}")
    print("   Assicurati che il container mongo sia attivo (docker compose up mongo)")
    sys.exit(1)

db     = client["myapp"]
images = db["images"]


images.delete_many({})
print("🗑️  Collection 'images' svuotata")


_seed_timestamp = datetime.now(_TZ_IT) if _TZ_IT else datetime.now()
_seed_str       = _seed_timestamp.strftime("%Y-%m-%d %H:%M:%S (ora italiana)")
print(f"🕐 Timestamp seed: {_seed_str}")


metadata = [

    {"filename": "aereo1.png","tipo": "aereo",
     "modello": "Lockheed Martin F-22 Raptor","descrizione": "Caccia stealth da superiorità aerea in virata"},
    {"filename": "aereo2.png","tipo": "aereo",
     "modello": "Airbus A300-600ST Beluga","descrizione": "Aereo cargo super trasporto"},
    {"filename": "aereo3.png","tipo": "aereo",
     "modello": "Boeing 747-8 Intercontinental","descrizione": "Jumbo wide-body quadrimotore"},
    {"filename": "aereo4.png","tipo": "aereo",
     "modello": "Lockheed Martin F-117 Nighthawk","descrizione": "Cacciabombardiere stealth"},
    {"filename": "aereo5.png","tipo": "aereo",
     "modello": "Aérospatiale-BAC Concorde","descrizione": "Aereo di linea supersonico"},


    {"filename": "treno1.png","tipo": "treno",
     "annoProduzione": 1995,"descrizione": "Convoglio ferroviario in stazione"},
    {"filename": "treno2.png","tipo": "treno",
     "annoProduzione": 2018,"descrizione": "Treno ad alta velocità"},
    {"filename": "treno3.png","tipo": "treno",
     "annoProduzione": 1980,"descrizione": "Locomotiva su binario"},
    {"filename": "treno4.png","tipo": "treno",
     "annoProduzione": 2005,"descrizione": "Treno regionale in transito"},
    {"filename": "treno5.png","tipo": "treno",
     "annoProduzione": 1972,"descrizione": "Treno merci in movimento"},


    {"filename": "auto1.png","tipo": "auto",
     "marca": "Lexus", "modello": "RX","descrizione": "SUV crossover di lusso"},
    {"filename": "auto2.png","tipo": "auto",
     "marca": "Ford", "modello": "Mustang Shelby GT350","descrizione": "Muscle car sportiva con strisce blu"},
    {"filename": "auto3.png","tipo": "auto",
     "marca": "Volkswagen", "modello": "Golf","descrizione": "Auto in città"},
    {"filename": "auto4.png","tipo": "auto",
     "marca": "BMW", "modello": "Serie 3","descrizione": "Macchina parcheggiata"},
    {"filename": "auto5.png","tipo": "auto",
     "marca": "Audi", "modello": "Q5","descrizione": "Automobile in autostrada"},


    {"filename": "persona1.png","tipo": "persona",
     "genere": "M","descrizione": "Ritratto di una persona"},
    {"filename": "persona2.png","tipo": "persona",
     "genere": "F","descrizione": "Persona in primo piano"},
    {"filename": "persone1.png","tipo": "persona",
     "genere": "Altro","descrizione": "Gruppo di persone insieme"},
    {"filename": "persone2.png","tipo": "persona",
     "genere": "Altro","descrizione": "Persone in un evento"},
    {"filename": "persone3.png","tipo": "persona",
     "genere": "Altro","descrizione": "Folla di persone"},


    {"filename": "altro1.png","tipo": "altro","descrizione": "Papavero arancione doppio in primo piano"},
    {"filename": "altro2.png","tipo": "altro","descrizione": "Rosa rossa in piena fioritura"},
    {"filename": "altro3.png","tipo": "altro","descrizione": "Giglio arancione tra il fogliame"},
    {"filename": "altro4.png","tipo": "altro","descrizione": "Fior di loto rosa con gocce d'acqua"},
    {"filename": "altro5.png","tipo": "altro","descrizione": "Girasole giallo in primo piano"},
]


for doc in metadata:
    doc["created_at"] = _seed_str     


result = images.insert_many(metadata)
print(f"\n✅ Inseriti {len(result.inserted_ids)} documenti in myapp.images")


print("\n📋 Documenti presenti (con timestamp):")
for doc in images.find({}, {"_id": 1, "filename": 1, "tipo": 1, "created_at": 1}):
    ts = doc.get("created_at", "—")
    tipo = doc.get("tipo", "—")
    print(f"  [{doc['_id']}]  {doc['filename']:<25}  tipo: {tipo:<10}  🕐 {ts}")

print(f"\n🎉 Seed completato — {len(result.inserted_ids)} immagini caricate in myapp.images")


import subprocess
import shutil
import glob
import platform


_compass_uri = "mongodb://localhost:27017/myapp"

def _trova_compass():
    sistema = platform.system()


    if sistema == "Windows":

        if shutil.which("MongoDBCompass"):
            return shutil.which("MongoDBCompass")


        radici = [
            os.environ.get("LOCALAPPDATA", ""),   
            os.environ.get("APPDATA", ""),         
            os.environ.get("PROGRAMFILES", ""),    
            os.environ.get("PROGRAMFILES(X86)", ""), 
        ]
        pattern = "MongoDBCompass.exe"
        for radice in radici:
            if not radice:
                continue

            risultati = glob.glob(os.path.join(radice, "**", pattern), recursive=True)
            if risultati:
                return risultati[0]


    elif sistema == "Darwin":
        percorsi_mac = [
            "/Applications/MongoDB Compass.app/Contents/MacOS/MongoDBCompass",
            os.path.expanduser("~/Applications/MongoDB Compass.app/Contents/MacOS/MongoDBCompass"),
        ]
        for p in percorsi_mac:
            if os.path.exists(p):
                return p
        if shutil.which("mongodb-compass"):
            return shutil.which("mongodb-compass")


    elif sistema == "Linux":
        for cmd in ["mongodb-compass", "MongoDBCompass"]:
            if shutil.which(cmd):
                return shutil.which(cmd)

    return None  

def _apri_compass():
    percorso = _trova_compass()
    if percorso:
        print(f"\n🧭 Apertura MongoDB Compass → {_compass_uri}")
        print(f"   Eseguibile: {percorso}")
        subprocess.Popen([percorso, _compass_uri])
    else:
        print("\n⚠️  MongoDB Compass non trovato sul sistema.")
        print("   Scaricalo da: https://www.mongodb.com/try/download/compass")
        print(f"   Connettiti manualmente a: {_compass_uri}")

_apri_compass()
