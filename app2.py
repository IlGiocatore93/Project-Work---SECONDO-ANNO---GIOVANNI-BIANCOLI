from tkinter import *
from tkinter import ttk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import os
import datetime
import time
from zoneinfo import ZoneInfo

_TZ_IT = ZoneInfo("Europe/Rome")
import requests
import threading
from pymongo import MongoClient
import cv2
from ultralytics import YOLO

import os
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))


model = YOLO(os.path.join(PROJECT_DIR, "yolov8n.pt"))
face_cascade = cv2.CascadeClassifier(os.path.join(PROJECT_DIR, "haarcascade_frontalface_default.xml"))

if face_cascade.empty():
    print("Errore: haarcascade_frontalface_default.xml non caricato correttamente.")


debounce_id = None
jwt_token = None
_credenziali = {}   
_original_image_paths = []  

def rinnova_token():
    """Rinnova il JWT silenziosamente ogni 20 minuti"""
    global jwt_token
    if _credenziali.get("username") and _credenziali.get("password"):
        try:
            res = requests.post(API_LOGIN, json={
                "username": _credenziali["username"],
                "password": _credenziali["password"]
            })
            if res.status_code == 200:
                jwt_token = res.json()["token"]
                print("🔄 Token JWT rinnovato automaticamente")  
        except Exception as e:
            print(f"⚠️ Rinnovo token fallito: {e}")
    root.after(8 * 60 * 1000, rinnova_token)  
current_genere = None

API_LOGIN    = "http://127.0.0.1:5000/login"
API_IMAGES   = "http://127.0.0.1:5001/images"
API_METADATA = "http://127.0.0.1:5001/metadata"
API_NUOVI_DATI    = "http://127.0.0.1:5001/nuovi-dati"
API_LISTA_NUOVI   = "http://127.0.0.1:5001/nuovi-dati/lista"
API_ELIMINA_NUOVI = "http://127.0.0.1:5001/nuovi-dati/elimina"
API_ELIMINA_BATCH = "http://127.0.0.1:5001/nuovi-dati/elimina-batch"
API_SIMILI        = "http://127.0.0.1:5001/simili"

try:
    _mongo_client    = MongoClient(os.getenv("MONGO_URI", "mongodb://localhost:27017/"),
                                   serverSelectionTimeoutMS=3000)
    _mongo_client.admin.command("ping")
    _nuovi_dati_coll = _mongo_client["myapp"]["nuovi_dati"]
    print("✅ Connessione diretta a MongoDB nuovi_dati attiva")
except Exception as _e:
    _nuovi_dati_coll = None
    print(f"⚠️  Impossibile connettersi direttamente a MongoDB: {_e}")


DOWNLOADS_DIR = os.path.join(PROJECT_DIR, "downloads")
os.makedirs(DOWNLOADS_DIR, exist_ok=True)

ANIMAL_LABELS = {
    "bird", "cat", "dog", "horse", "sheep", "cow", "elephant",
    "bear", "zebra", "giraffe"
}
PERSON_LABEL = "person"


def mostra_login():
    """Mostra il login prima della GUI principale."""
    login_win = Tk()
    login_win.title("Login — Galleria Tipologie")
    login_win.geometry("340x270")
    login_win.configure(bg="#1e1a2e")
    login_win.resizable(False, False)
    try:
        login_win.iconbitmap(os.path.join(PROJECT_DIR, 'slide.ico'))
    except:
        pass

    _tentativi_chiusura = [0]   
    _MAX_TENTATIVI     = 3      

    def _blocca_campi():
        e_user.config(state="disabled")
        e_pass.config(state="disabled")
        btn.config(state="disabled")

    def _sblocca_campi():
        e_user.config(state="normal")
        e_pass.config(state="normal")
        btn.config(state="normal")
        lbl_timer.config(text="")
        lbl_err.config(text="")

    def _countdown(secondi):
        if secondi > 0:
            lbl_timer.config(text=f"⏳ Nuovo tentativo tra {secondi}s...", fg="#ffaa00")
            login_win.after(1000, lambda: _countdown(secondi - 1))
        else:
            _sblocca_campi()

    def _on_close():
        _tentativi_chiusura[0] += 1
        if _tentativi_chiusura[0] < _MAX_TENTATIVI:
            rimasti = _MAX_TENTATIVI - _tentativi_chiusura[0]
            lbl_err.config(text=f"⚠️ Devi autenticarti! ({rimasti} avvisi rimasti)")
            _blocca_campi()
            _countdown(3)
        else:
            login_win.destroy()

    login_win.protocol("WM_DELETE_WINDOW", _on_close)

    Label(login_win, text="📂Galleria Tipologie📂", bg="#1e1a2e", fg="white",
          font=("Helvetica", 13, "bold")).pack(pady=(20, 4))
    Label(login_win, text="Accedi per continuare", bg="#1e1a2e", fg="#aaaaaa",
          font=("Arial", 9)).pack(pady=(0, 16))

    frame_form = Frame(login_win, bg="#1e1a2e")
    frame_form.pack()

    Label(frame_form, text="Username:", bg="#1e1a2e", fg="white", font=("Arial", 10)).grid(row=0, column=0, sticky="e", padx=8, pady=5)
    e_user = Entry(frame_form, width=20, font=("Arial", 10))
    e_user.grid(row=0, column=1, pady=5)
    e_user.focus()

    Label(frame_form, text="Password:", bg="#1e1a2e", fg="white", font=("Arial", 10)).grid(row=1, column=0, sticky="e", padx=8, pady=5)
    e_pass = Entry(frame_form, show="*", width=20, font=("Arial", 10))
    e_pass.grid(row=1, column=1, pady=5)

    lbl_err = Label(login_win, text="", bg="#1e1a2e", fg="#ff4444", font=("Arial", 9))
    lbl_err.pack(pady=2)

    lbl_timer = Label(login_win, text="", bg="#1e1a2e", fg="#ffaa00", font=("Arial", 8))
    lbl_timer.pack(side=BOTTOM, anchor="e", padx=10, pady=4)

    def tenta_login(event=None):
        global jwt_token
        username = e_user.get().strip()
        password = e_pass.get().strip()
        if not username or not password:
            lbl_err.config(text="Inserisci username e password")
            return
        btn.config(state="disabled", text="Connessione...")
        def worker():
            global jwt_token
            try:
                res = requests.post(API_LOGIN, json={"username": username, "password": password})
                if res.status_code == 200:
                    jwt_token = res.json()["token"]
                    _credenziali["username"] = username
                    _credenziali["password"] = password
                    login_win.after(0, login_win.destroy)
                else:
                    login_win.after(0, lambda: lbl_err.config(text="❌ Credenziali errate"))
                    login_win.after(0, lambda: btn.config(state="normal", text="Accedi"))
            except Exception as e:
                login_win.after(0, lambda: lbl_err.config(text=f"Errore: {e}"))
                login_win.after(0, lambda: btn.config(state="normal", text="Accedi"))
        threading.Thread(target=worker, daemon=True).start()

    btn = Button(login_win, text="Accedi", command=tenta_login,
                 bg="#4f8ef7", fg="white", font=("Arial", 10, "bold"),
                 relief=FLAT, padx=16, pady=5, cursor="hand2")
    btn.pack(pady=6)
    e_pass.bind("<Return>", tenta_login)
    e_user.bind("<Return>", lambda e: e_pass.focus())
    login_win.mainloop()

mostra_login()

root = Tk()
root.after(8 * 60 * 1000, rinnova_token)  
root.title('galleria Tipologie')
root.geometry('1000x700')  
root.configure(bg="#5a5e59")
root.minsize(800, 600)
#root.resizable(False, False)
try:
    root.iconbitmap(os.path.join(PROJECT_DIR, 'slide.ico'))
except:
    print("Icona non trovata o non compatibile su questo sistema.")

GENERI_CARTELLE = {
    "Aerei":    os.path.join(PROJECT_DIR, "images", "aerei"),
    "Treni":    os.path.join(PROJECT_DIR, "images", "treni"),
    "Auto":     os.path.join(PROJECT_DIR, "images", "auto"),
    "Persone":  os.path.join(PROJECT_DIR, "images", "persone"),
    "Altro":    os.path.join(PROJECT_DIR, "images", "altro"),
}

for genere, cartella in GENERI_CARTELLE.items():
    if not os.path.exists(cartella):
        os.makedirs(cartella)
        print(f"Creata cartella: {cartella}")

icon_images = {}
try:
    icon_images["info"] = ImageTk.PhotoImage(Image.open(os.path.join(PROJECT_DIR, "info.png")).resize((24, 24)))
    icon_images["success"] = ImageTk.PhotoImage(Image.open(os.path.join(PROJECT_DIR, "success.png")).resize((24, 24)))
    icon_images["error"] = ImageTk.PhotoImage(Image.open(os.path.join(PROJECT_DIR, "error.png")).resize((24, 24)))
    img = Image.open(os.path.join(PROJECT_DIR, "icon.png"))
except Exception as e:
    print("Errore caricamento icone barra stato:", e)


def carica_immagini_da_cartella(cartella, nome_genere):
    """Funzione helper per caricare immagini da una cartella"""
    if not os.path.exists(cartella):
        aggiorna_status(f"Cartella {nome_genere} non trovata", "error")
        messagebox.showerror("Errore", f"Cartella {nome_genere} non trovata!\nPercorso: {cartella}")
        return False
    
    try:
        global image_paths, current_image_index, current_genere
        estensioni_valide = (".jpg", ".jpeg", ".png", ".gif", ".bmp", ".ico")
        
        all_images = [
            os.path.join(cartella, f) 
            for f in os.listdir(cartella) 
            if f.lower().endswith(estensioni_valide)
        ]

        if not all_images:
            aggiorna_status(f"Nessuna immagine in {nome_genere}", "error")
            messagebox.showwarning("Attenzione", f"Nessuna immagine trovata in {nome_genere}!")
            return False
        
        genere_img_name = f"{nome_genere.lower()}.png"
        
        image_paths = []
        
        for img_path in all_images:
            if os.path.basename(img_path).lower() == genere_img_name:
                image_paths.append(img_path)
                break
        
        for img_path in all_images:
            if os.path.basename(img_path).lower() != genere_img_name:
                image_paths.append(img_path)
        
        if not image_paths:
            image_paths = all_images  
            
        current_image_index = 0
        current_genere = nome_genere
        global _original_image_paths
        _original_image_paths = image_paths.copy()
        try:
            if entry_ricerca.get():
                entry_ricerca.delete(0, END)
        except NameError:
            pass
        mostra_immagine()
        nomi_file = ", ".join(os.path.basename(p) for p in image_paths)
        aggiorna_status(f"Caricate {len(image_paths)} immagini {nome_genere} ({nomi_file})", "success")
        
        print(f"Ordine immagini {nome_genere}:")
        for i, path in enumerate(image_paths):
            print(f"{i+1}: {os.path.basename(path)}")
            
        return True
        
    except Exception as e:
        aggiorna_status(f"Errore caricamento {nome_genere}: {str(e)}", "error")
        messagebox.showerror("Errore", f"Si è verificato un errore:\n{str(e)}")
        return False



def carica_cartella_aerei():
    """Carica le immagini dalla cartella Aerei"""
    carica_immagini_da_cartella(GENERI_CARTELLE["Aerei"], "Aerei")

def carica_cartella_treni():
    """Carica le immagini dalla cartella Treni"""
    carica_immagini_da_cartella(GENERI_CARTELLE["Treni"], "Treni")

def carica_cartella_auto():
    """Carica le immagini dalla cartella Auto"""
    carica_immagini_da_cartella(GENERI_CARTELLE["Auto"], "Auto")

def carica_cartella_persone():
    """Carica le immagini dalla cartella Persone"""
    carica_immagini_da_cartella(GENERI_CARTELLE["Persone"], "Persone")

def carica_cartella_altro():
    """Carica le immagini dalla cartella Altro"""
    carica_immagini_da_cartella(GENERI_CARTELLE["Altro"], "Altro")



image_paths = []
current_image_index = 0
tk_img = None  

def carica_immagini():
    """Carica immagini da una cartella selezionata"""
    global image_paths, current_image_index, current_genere, _original_image_paths
    
    cartella = filedialog.askdirectory(title="Seleziona una cartella con immagini")
    if not cartella:
        aggiorna_status("Caricamento annullato", "info")
        return
    
    try:
        estensioni_valide = (".jpg", ".jpeg", ".png", ".gif", ".bmp", ".ico")
        image_paths = sorted([
            os.path.join(cartella, f) 
            for f in os.listdir(cartella) 
            if f.lower().endswith(estensioni_valide)
        ])

        if not image_paths:
            aggiorna_status("Nessuna immagine trovata", "error")
            messagebox.showwarning("Attenzione", "Nessuna immagine trovata nella cartella selezionata!")
            return
            
        current_image_index = 0
        _original_image_paths = image_paths.copy()   
        current_genere = "Personalizzato"
        try:
            entry_ricerca.delete(0, END)
        except NameError:
            pass
        mostra_immagine()
        aggiorna_status(f"Caricate {len(image_paths)} immagini dalla cartella — puoi cercarle con la barra in alto", "success")
        
        update_image_info(image_paths[current_image_index])
        
    except Exception as e:
        aggiorna_status(f"Errore caricamento immagini: {str(e)}", "error")
        messagebox.showerror("Errore", f"Si è verificato un errore:\n{str(e)}")
    
def mostra_immagine():
    global tk_img
    if not image_paths or current_image_index >= len(image_paths):
        print("Nessuna immagine da mostrare.")
        return

    img_path = image_paths[current_image_index]
    print(f"Mostrando immagine: {img_path}")
    img = Image.open(img_path)

    if img_path.lower().endswith(".ico"):
        try:
            sizes = img.ico.sizes() if hasattr(img, 'ico') else []
            if sizes:
                img.size = max(sizes)
        except Exception:
            pass
        img = img.convert("RGBA")

    label_width = image_label.winfo_width()
    label_height = image_label.winfo_height()

    if label_width < 10 or label_height < 10:
        label_width = 530
        label_height = 390

    img = img.resize((label_width, label_height), Image.Resampling.LANCZOS)
    tk_img = ImageTk.PhotoImage(img.copy())

    image_label.config(image=tk_img)

    file_name = os.path.basename(img_path)
    query = entry_ricerca.get().strip().lower()
    generi_files = ["aerei.png", "treni.png", "auto.png", "persone.png", "altro.png"]
    
    if not query and file_name.lower() in generi_files:
        aggiorna_status(f"Visualizzazione: {file_name} (immagine principale del genere {os.path.splitext(file_name)[0].capitalize()})")
    elif query and os.path.splitext(file_name)[0].lower().startswith(query):
        matching_count = sum(1 for p in image_paths if os.path.splitext(os.path.basename(p))[0].lower().startswith(query))
        aggiorna_status(f"Visualizzazione: {file_name} (match con '{query}', {matching_count} immagini trovate)")
    else:
        aggiorna_status(f"Visualizzazione: {file_name} ({current_image_index + 1} di {len(image_paths)})")
    
    update_image_info(img_path)


def update_image_info(img_path):
    """Aggiorna il pannello informativo con i dettagli dell'immagine"""
    global current_genere, search_results
    
    file_name = os.path.basename(img_path)
    file_size = os.path.getsize(img_path) / 1024  # KB
    file_ext = os.path.splitext(img_path)[1].upper().replace(".", "")
    creation_date = datetime.datetime.fromtimestamp(os.path.getctime(img_path), tz=_TZ_IT).strftime('%d/%m/%Y %H:%M')
    resolution = Image.open(img_path).size
    
    if len(image_paths) == 1:
        pos_text = "1 di 1 immagine"
    else:
        pos_text = f"{current_image_index + 1} di {len(image_paths)} immagini"
    
    info_text = (
        f"• Nome: {file_name}\n\n"
        f"• Genere: {current_genere if current_genere else 'Personalizzato'}\n\n"
        f"• Formato: {file_ext}\n\n"
        f"• Dimensione: {file_size:.1f} KB\n\n"
        f"• Risoluzione: {resolution[0]}×{resolution[1]} px\n\n"
        f"• Data creazione: {creation_date}\n\n"
        f"• Posizione: {pos_text}\n\n"
        f"• Percorso: {os.path.dirname(img_path)}"
    )
    
    info_label.config(text=info_text)

def _analizza_e_salva_nuovi_dati(img_path):
    """YOLO + face detect + upsert in MongoDB nuovi_dati. Riusato da Download e Sync."""
    try:
        img_cv = cv2.imread(img_path)
        if img_cv is None:
            print(f"⚠️  Impossibile leggere {img_path}"); return
        _raw = model(img_path, verbose=False)
        results = _raw[0] if isinstance(_raw, (list, tuple)) and len(_raw) > 0 else _raw
        if not hasattr(results, "boxes"):
            from ultralytics import YOLO as _YOLO
            globals()["model"] = _YOLO(os.path.join(PROJECT_DIR, "yolov8n.pt"))
            results = globals()["model"](img_path, verbose=False)[0]
        labels_count, persone, oggetti = {}, 0, 0
        for box in results.boxes:
            label = model.names[int(box.cls[0])]
            labels_count[label] = labels_count.get(label, 0) + 1
            cat = classify_label(label)
            if cat == "persone": persone += 1
            elif cat == "animali": pass  
            else: oggetti += 1
        gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
        facce = len(face_cascade.detectMultiScale(gray, 1.1, 5, minSize=(30, 30)))
        from datetime import datetime as _dt
        fn = os.path.basename(img_path)
        payload = {
            "filename": fn,
            "descrizione": f"Immagine caricata manualmente: {os.path.splitext(fn)[0].replace('_',' ').title()}",
            "persone": persone, "oggetti": oggetti,
            "facce": facce, "dettaglio": labels_count,
            "created_at": _dt.now(_TZ_IT).strftime("%d/%m/%Y %H:%M:%S (ora italiana)"),
        }
        headers = {"Authorization": jwt_token} if jwt_token else {}

        if _nuovi_dati_coll is not None:
            _nuovi_dati_coll.delete_one({"filename": fn})
        requests.post(API_NUOVI_DATI, json=payload, headers=headers, timeout=5)
        print(f"📦 Salvato in nuovi_dati: {fn}  [p={persone} o={oggetti} f={facce}]")
    except Exception as e:
        print(f"⚠️ Errore _analizza_e_salva_nuovi_dati: {e}")


def scarica_immagine():
    """Scarica l'immagine corrente in downloads/ + analisi YOLO in background."""
    if not image_paths:
        messagebox.showwarning("Attenzione", "Nessuna immagine da scaricare!"); return
    img_path = image_paths[current_image_index]
    filename = os.path.basename(img_path)
    dest = os.path.join(DOWNLOADS_DIR, filename)
    try:
        import shutil
        shutil.copy2(img_path, dest)
        aggiorna_status(f"✅ Salvata in downloads/{filename} — analisi in corso...", "success")
        messagebox.showinfo("Download completato", f"Immagine salvata in:\n{dest}")
        threading.Thread(target=_analizza_e_salva_nuovi_dati, args=(dest,), daemon=True).start()
    except Exception as e:
        aggiorna_status(f"Errore download: {e}", "error")
        messagebox.showerror("Errore", str(e))


def elimina_da_downloads():
    """Elimina l'immagine corrente da downloads/ e dal MongoDB nuovi_dati."""
    if not image_paths:
        messagebox.showwarning("Attenzione", "Nessuna immagine selezionata!"); return
    filename = os.path.basename(image_paths[current_image_index])
    dest = os.path.join(DOWNLOADS_DIR, filename)
    if not os.path.exists(dest):
        messagebox.showwarning("File non trovato",
            f"'{filename}' non è in downloads/.\nScaricala prima con ⬇ Download."); return
    if not messagebox.askyesno("Conferma", f"Eliminare '{filename}' da downloads/ e MongoDB?"):
        return
    try:
        os.remove(dest)
        print(f"🗑️  Eliminato da downloads/: {filename}")
    except Exception as e:
        aggiorna_status(f"Errore eliminazione: {e}", "error")
        messagebox.showerror("Errore", str(e)); return

    def _rm():
        try:
            if _nuovi_dati_coll is None:
                print("⚠️  MongoDB non disponibile, skip rimozione documento")
                return
            ris = _nuovi_dati_coll.delete_one({"filename": filename})
            if ris.deleted_count > 0:
                print(f"🗑️  Rimosso da nuovi_dati: {filename}")
            else:
                print(f"ℹ️  '{filename}' non era in nuovi_dati")
        except Exception as e:
            print(f"⚠️ Errore rimozione Mongo: {e}")
    threading.Thread(target=_rm, daemon=True).start()
    aggiorna_status(f"🗑️  '{filename}' eliminata da downloads/ e MongoDB", "success")


def sincronizza_downloads(silenzioso=False):
    """
    Allinea downloads/ con nuovi_dati su MongoDB usando connessione DIRETTA
    (non REST) → funziona sempre, anche se l'API non risponde.
    """
    def _worker():
        try:
            if _nuovi_dati_coll is None:
                err = "❌ MongoDB non raggiungibile — controlla che il container 'mongo' sia attivo."
                print(err); aggiorna_status(err, "error")
                if not silenzioso:
                    root.after(0, lambda: messagebox.showerror("Errore Sync", err))
                return

            ext_ok = {".png", ".jpg", ".jpeg", ".bmp", ".webp", ".tiff"}
            file_disco = {f for f in os.listdir(DOWNLOADS_DIR)
                          if os.path.isfile(os.path.join(DOWNLOADS_DIR, f))
                          and os.path.splitext(f)[1].lower() in ext_ok}

            file_mongo = {d["filename"] for d in
                          _nuovi_dati_coll.find({}, {"_id": 0, "filename": 1})}

            print(f"🔄 Sync: disco={len(file_disco)}  mongo={len(file_mongo)}")
            print(f"   disco → {sorted(file_disco) if file_disco else '(vuota)'}")
            print(f"   mongo → {sorted(file_mongo) if file_mongo else '(vuota)'}")

            da_aggiungere = file_disco - file_mongo
            da_rimuovere  = file_mongo - file_disco

            for fn in da_aggiungere:
                _analizza_e_salva_nuovi_dati(os.path.join(DOWNLOADS_DIR, fn))

            if da_rimuovere:
                ris = _nuovi_dati_coll.delete_many({"filename": {"$in": list(da_rimuovere)}})
                print(f"🗑️  Sync: rimossi {ris.deleted_count} orfani da Mongo: {', '.join(da_rimuovere)}")

            a, r_ = len(da_aggiungere), len(da_rimuovere)
            if a == 0 and r_ == 0:
                msg = "✅ downloads/ e MongoDB già sincronizzati."
            else:
                p = []
                if a: p.append(f"{a} aggiunt{'o' if a==1 else 'i'}")
                if r_: p.append(f"{r_} rimoss{'o' if r_==1 else 'i'}")
                msg = f"✅ Sync completata: {', '.join(p)}."
            print(f"🔄 {msg}")
            aggiorna_status(f"🔄 {msg}", "success")
            if not silenzioso:
                root.after(0, lambda: messagebox.showinfo("Sincronizzazione", msg))
        except Exception as e:
            err = f"Errore sync: {e}"; print(f"⚠️ {err}")
            aggiorna_status(err, "error")
            if not silenzioso:
                root.after(0, lambda: messagebox.showerror("Errore Sync", err))
    threading.Thread(target=_worker, daemon=True).start()


def _avvia_auto_sync():
    """Timer ricorsivo: sync silenziosa ogni 30 secondi."""
    sincronizza_downloads(silenzioso=True)
    root.after(30_000, _avvia_auto_sync)


def immagine_successiva():
    global current_image_index
    if image_paths:
        current_image_index = (current_image_index + 1) % len(image_paths)
        print(f"Indice immagine successiva: {current_image_index}")  
        mostra_immagine()

def immagine_precedente():
    global current_image_index
    if image_paths:
        print(f"Indice prima del cambio (precedente): {current_image_index}")     
        if current_image_index == 0:
            current_image_index = len(image_paths) -1
        else:
            current_image_index -= 1
        print(f"Indice dopo il cambio (precedente): {current_image_index}")  
        mostra_immagine()

def aggiorna_status(testo, tipo="info"):
    colori = {
        "info": ("#dddddd", "black"),
        "success": ("#d4edda", "green"),
        "error": ("#f8d7da", "red")
    }
    bg, fg = colori.get(tipo, ("#dddddd", "black"))
    

    status_frame.config(bg=bg)
    status_bar.config(text=testo, bg=bg, fg=fg)
    status_icon.config(image=icon_images.get(tipo), bg=bg)



def fetch_metadata(img_path):
    filename = os.path.basename(img_path)
    def worker():
        try:
            headers = {"Authorization": jwt_token} if jwt_token else {}
            res = requests.post(API_METADATA, json={"filename": filename}, headers=headers, timeout=8)
            if res.status_code == 200:
                meta = res.json()
                root.after(0, lambda: aggiorna_info_con_metadata(meta, img_path))
        except Exception as e:
            print("Errore metadata:", e)
    threading.Thread(target=worker, daemon=True).start()

def get_metadata_sync(img_path):
    filename = os.path.basename(img_path)
    try:
        headers = {"Authorization": jwt_token} if jwt_token else {}
        res = requests.post(API_METADATA, json={"filename": filename}, headers=headers, timeout=8)
        if res.status_code == 200:
            return res.json()
    except Exception as e:
        print("Errore metadata sync:", e)
    return {}

def aggiorna_info_con_metadata(meta, img_path):
    file_name     = os.path.basename(img_path)
    file_size     = os.path.getsize(img_path) / 1024
    file_ext      = os.path.splitext(img_path)[1].upper().replace(".", "")
    creation_date = datetime.datetime.fromtimestamp(os.path.getctime(img_path), tz=_TZ_IT).strftime('%d/%m/%Y %H:%M')
    resolution    = Image.open(img_path).size
    pos_text      = f"{current_image_index + 1} di {len(image_paths)} immagini"
    meta_lines    = "".join(f"• {str(k).capitalize()}: {v}\n" for k, v in meta.items()) if meta else "• Nessun metadata DB disponibile\n"
    info_label.config(text=(
        f"• Nome: {file_name}\n\n"
        f"• Genere: {current_genere if current_genere else 'Personalizzato'}\n\n"
        f"• Formato: {file_ext}\n\n"
        f"• Dimensione: {file_size:.1f} KB\n\n"
        f"• Risoluzione: {resolution[0]}×{resolution[1]} px\n\n"
        f"• Data creazione: {creation_date}\n\n"
        f"• Posizione: {pos_text}\n\n"
        f"─────────────────\n"
        f"📋 METADATA DB:\n{meta_lines}"
    ))

def classify_label(label):
    if label == PERSON_LABEL:
        return "persone"
    if label in ANIMAL_LABELS:
        return "animali"
    return "oggetti"


def rileva_immagine():
    global image_paths, current_image_index

    if not image_paths:
        messagebox.showwarning("Attenzione", "Carica prima un genere o un'immagine")
        return

    img_path = image_paths[current_image_index]
    aggiorna_status("Analisi YOLO + Mongo in corso...", "info")
    btn_rileva.config(state="disabled", text="Analisi...", bg="#555555")

    def worker():
        try:
            img_cv = cv2.imread(img_path)
            if img_cv is None:
                raise ValueError(f"Impossibile leggere l'immagine: {img_path}")


            _raw = model(img_path, verbose=False)

            if isinstance(_raw, (list, tuple)) and len(_raw) > 0:
                results = _raw[0]
            else:
                results = _raw

            if not hasattr(results, "boxes"):
                from ultralytics import YOLO as _YOLO
                globals()["model"] = _YOLO(os.path.join(PROJECT_DIR, "yolov8n.pt"))
                results = globals()["model"](img_path, verbose=False)[0]

            labels_count = {}
            yolo_people_count = 0
            animal_count = 0
            object_count = 0

            for box in results.boxes:
                label = model.names[int(box.cls[0])]
                conf = float(box.conf[0])

                x1, y1, x2, y2 = map(int, box.xyxy[0])

                cv2.rectangle(img_cv, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(
                    img_cv,
                    f"{label} {conf:.2f}",
                    (x1, max(y1 - 10, 15)),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (0, 255, 0),
                    2
                )

                labels_count[label] = labels_count.get(label, 0) + 1

                categoria = classify_label(label)
                if categoria == "persone":
                    yolo_people_count += 1
                elif categoria == "animali":
                    animal_count += 1
                else:
                    object_count += 1


            gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=(30, 30)
            )

            for (x, y, w, h) in faces:
                cv2.rectangle(img_cv, (x, y), (x + w, y + h), (255, 0, 0), 2)
                cv2.putText(
                    img_cv,
                    "Face",
                    (x, max(y - 10, 15)),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (255, 0, 0),
                    2
                )


            meta = get_metadata_sync(img_path)

            titolo_file = os.path.splitext(os.path.basename(img_path))[0]
            titolo_tipo = (
                meta.get("titolo")
                or meta.get("title")
                or meta.get("nome")
                or titolo_file.replace("_", " ").title()
            )

            img_rgb = cv2.cvtColor(img_cv, cv2.COLOR_BGR2RGB)
            pil_img = Image.fromarray(img_rgb)

            def update_ui():
                global tk_img

                lw = image_label.winfo_width() or 530
                lh = image_label.winfo_height() or 390

                pil_r = pil_img.copy().resize((lw, lh), Image.Resampling.LANCZOS)
                tk_img = ImageTk.PhotoImage(pil_r)
                image_label.config(image=tk_img)

                counts_lines = "\n".join(
                    f"• {label}: {count}"
                    for label, count in sorted(labels_count.items())
                ) if labels_count else "• Nessun oggetto rilevato"

                from datetime import datetime as _dt, timedelta

                dest_path = os.path.join(DOWNLOADS_DIR, os.path.basename(img_path))
                if os.path.exists(dest_path) and meta:
                    ora_corretta = _dt.now(_TZ_IT) - timedelta(hours=0)
                    meta["created_at"] = ora_corretta.strftime("%d/%m/%Y %H:%M:%S (ora italiana)")
                def _fmt(k, v):
                    if k == "created_at":
                        try:
                            if isinstance(v, _dt):
                                if v.tzinfo is None:
                                    v = v.replace(tzinfo=ZoneInfo("UTC"))
                                return v.astimezone(_TZ_IT).strftime("%d/%m/%Y %H:%M:%S (ora italiana)")
                            s = str(v).replace("(ora italiana)", "").replace("UTC", "").replace("GMT", "").strip()
                            dt = _dt.fromisoformat(s.replace("Z", "+00:00"))
                            if dt.tzinfo is None:
                                dt = dt.replace(tzinfo=ZoneInfo("UTC"))
                            return dt.astimezone(_TZ_IT).strftime("%d/%m/%Y %H:%M:%S (ora italiana)")
                        except Exception:
                            return str(v).replace("UTC", "").replace("GMT", "").strip()
                    return str(v)

                _skip = {"_id", "last_detected_at", "animali", "facce", "oggetti", "persone",
                         "dettaglio", "nomeImmagine", "titolo", "categoria"}
                meta_lines = "\n".join(
                    f"• {str(k).capitalize()}: {_fmt(k, v)}"
                    for k, v in meta.items() if k not in _skip
                ) if meta else "• Nessun metadata trovato nel database"

                info_label.config(text=(
                    f">>> TITOLO TIPO: {titolo_tipo}\n\n"
                    f">>> RILEVAMENTO YOLO\n"
                    f"• Persone (YOLO): {yolo_people_count}\n"
                    f"• Oggetti: {object_count}\n"
                    f"• Facce rilevate: {len(faces)}\n\n"
                    f">>> DETTAGLIO OGGETTI\n{counts_lines}\n\n"
                    f">>> CARATTERISTICHE TIPO DA MONGO\n{meta_lines}"
                ))

                aggiorna_status(
                    f"YOLO: {sum(labels_count.values())} rilevamenti, facce: {len(faces)}",
                    "success"
                )

            root.after(0, update_ui)


            if current_genere == "Personalizzato":
                _analizza_e_salva_nuovi_dati(img_path)

        except Exception as e:
            err_msg = str(e)
            root.after(0, lambda msg=err_msg: messagebox.showerror("Errore YOLO", msg))
            root.after(0, lambda msg=err_msg: aggiorna_status(f"Errore rilevamento: {msg}", "error"))
        finally:
            root.after(0, lambda: btn_rileva.config(
                state="normal", text="Rileva", bg="#2e7d32"))

    threading.Thread(target=worker, daemon=True).start()


info_frame = Frame(root, bg="#3c285e")
info_frame.place(relx=0.03, rely=0.35, relwidth=0.40, relheight=0.57)


Label(info_frame, text="INFORMAZIONI IMMAGINE", bg="#3c285e", fg="white", 
      font=("Arial", 12, "bold")).pack(pady=(0, 10))


info_label = Label(info_frame, text="Nessuna immagine caricata", 
                  bg="#3c285e", fg="white", font=("Arial", 10), 
                  justify=LEFT, anchor="nw", wraplength=280)
info_label.pack(fill=BOTH, expand=True)


titolo_genere = Label(root, text="📂  Seleziona una tipologia  📂", bg="#5a5e59", fg="white",
                      font=("Segoe UI Emoji", 13, "bold"), anchor="center")
titolo_genere.place(relx=0.45, rely=0.21, relwidth=0.52, relheight=0.05)


btn_specs = [
    ("Aerei",   0.450, carica_cartella_aerei,   "#1e88e5", "white"),
    ("Treni",   0.555, carica_cartella_treni,   "#546e7a", "white"),
    ("Auto",    0.660, carica_cartella_auto,    "#c62828", "white"),
    ("Persone", 0.765, carica_cartella_persone, "#2e7d32", "white"),
    ("Altro",   0.870, carica_cartella_altro,   "#f9a825", "black"),
]

for text, relx, command, bg_color, fg_color in btn_specs:
    Button(root, text=text, command=command, bg=bg_color, fg=fg_color, activebackground="#1ebaba", activeforeground="#fafcfc").place(relx=relx, rely=0.30, relwidth=0.10, relheight=0.05)


text_box = Text(root)
text_box.place(relx=0.03, rely=0.07, relwidth=0.46, relheight=0.10)


def apri_file():
    filetypes = (
        ('file di testo', '*.txt'),
        ('tutti i file', '*.*')
    )
    filename = filedialog.askopenfilename(title="Apri un file", initialdir="/", filetypes=filetypes) 
    if filename:  
        print(f"File aperto: {filename}")
        try:
            with open(filename, 'r', encoding='utf-8', errors='ignore') as f:
                data = f.read()
                text_box.delete('1.0', END)  
                text_box.insert(END, data)   
        except Exception as e:
            print(f"Errore nella lettura del file: {e}")

        try:
            f_save = filedialog.asksaveasfile(mode="w", title="Salva file", defaultextension=".txt")
            if f_save:
                data_to_write = "HO SOSTITUITO IL FILE" 
                f_save.write(data_to_write)
                f_save.close()
        except Exception as e:
            print(f"Errore nel salvataggio del file: {e}")



def mostra_istruzioni():
    win = Toplevel(root)
    win.title("Istruzioni — Galleria Tipologie")
    _w = 750
    _h = 700
    win.geometry(f"{_w}x{_h}")
    win.minsize(_w, 500)
    win.configure(bg="#1e1a2e")
    win.resizable(True, True)
    try:
        win.iconbitmap(os.path.join(PROJECT_DIR, "slide.ico"))
    except:
        pass

    Label(win, text="📌 Istruzioni — Galleria Tipologie",
          bg="#1e1a2e", fg="white", font=("Arial", 13, "bold")).pack(pady=(12, 4))


    Button(win, text="Chiudi", command=win.destroy,
           bg="#c44536", fg="white", font=("Arial", 11, "bold"),
           relief=FLAT, padx=20, pady=5).pack(side=BOTTOM, pady=(0, 12))

    frame = Frame(win, bg="#1e1a2e")
    frame.pack(fill=BOTH, expand=True, padx=10, pady=(0, 5))

    scrollbar = Scrollbar(frame)
    scrollbar.pack(side=RIGHT, fill=Y)

    testo = Text(frame, bg="#2a2540", fg="white", font=("Arial", 12),
                 wrap=WORD, yscrollcommand=scrollbar.set,
                 relief=FLAT, padx=12, pady=10)
    testo.pack(fill=BOTH, expand=True)
    scrollbar.config(command=testo.yview)

    istruzioni = (
        "── AVVIO RAPIDO ──────────────────────────────\n"
        "1. Esegui start.bat per avviare Docker Desktop e i container automaticamente.\n"
        "   start.bat stoppa automaticamente i container di altri progetti prima di avviare il tuo.\n"
        "   In alternativa: apri Docker manualmente e usa 'docker compose up -d'.\n\n"
        "2. Esegui seed_db_galleria.py per popolare MongoDB con i tipi e aprire Compass automaticamente.\n\n"
        "3. Avvia l'app con: python app2.py\n\n"
        "4. Per visualizzare i log dei microservizi REST auth_api e image_api su due tab(cmd) differenti oltre che su quella principale, basta scrivere da dentro la directory principale.\n"
        "   I comandi sono: python -m api.auth_api per la parte di autorizazzione e python -m api.image_api per le immagini.\n\n "
        "── LOGIN ─────────────────────────────────────\n"
        "5. Accedi con le credenziali (default: admin/admin123 o giovanni/pass1234).\n"
        "   Il token JWT si rinnova automaticamente ogni 8 minuti in background.\n"
        "   Chiudere la finestra di login senza autenticarsi blocca i campi per 3 secondi (max 3 tentativi) poi ti dà accesso.\n\n"
        "── CARICAMENTO IMMAGINI ──────────────────────\n"
        "6. Clicca su Aerei, Treni, Auto, Persone o Altro per caricare le immagini della tipologia.\n"
        "   → La barra diventa VERDE e mostra i nomi dei file caricati in ordine.\n"
        "   → La barra diventa GRIGIA con icona info durante la navigazione normale tra le immagini.\n"
        "   → La barra diventa ROSSA se la cartella non esiste o non contiene immagini.\n"
        "   → Il pannello INFORMAZIONI IMMAGINE, a sinistra, mostra le informazioni dettagliate: nome, formato, dimensione, risoluzione, data e posizione.\n\n"
        "7. Usa 'Carica Immagini' per caricare immagini da una cartella esterna (modalità Personalizzato).\n"
        "   → La barra di ricerca viene svuotata automaticamente al caricamento\n"
        "   → Dopo il caricamento puoi usare subito la barra di ricerca sulla cartella caricata.\n\n"
        "── BOTTONI PRINCIPALI ────────────────────────\n"
        "8. [Apri] — Apre un file di testo e ne mostra il contenuto nell'area di testo in alto a sinistra.\n"
        "   Dopo la lettura propone di salvare una copia del file con contenuto personalizzato.\n\n"
        "9. [Ridimensiona] — Ridimensiona la finestra dell'app a 1200x800 pixel con un solo click.\n\n"
        "── NAVIGAZIONE ───────────────────────────────\n"
        "10. Usa '← Precedente' e 'Successiva →' per scorrere tra le immagini caricate.\n\n"
        "11. Premi '⬇ Download' per salvare l'immagine corrente nella cartella downloads/ del progetto.\n"
        "    La cartella viene creata automaticamente se non esiste, premendo dopo il 'Rileva' aggiorna in automatico l'orario di creazione in YOLO.\n\n"
        "12. Premi '🗑 Elimina' per rimuovere l'immagine corrente da downloads/ e da MongoDB (collection nuovi_dati).\n"
        "    ATTENZIONE: funziona solo su immagini già scaricate con ⬇ Download.\n"
        "    Se l'immagine non è ancora in downloads/ viene mostrato un avviso.\n\n"
        "13. Premi '🔄 Sync' per sincronizzare la cartella downloads/ con MongoDB: aggiunge i file mancanti nel database e rimuove i record orfani.\n"
        "    La sincronizzazione avviene anche automaticamente ogni 30 secondi in background.\n\n"
        "── TASTO SELEZIONA ───────────────────────────\n"
        "14. Premi '✅ Seleziona' per aprire la finestra di esplorazione delle tipologie.\n"
        "    → Scegli la tipologia dal menu a tendina per vedere le miniature disponibili.\n"
        "    → Clicca su una miniatura per visualizzarla nel viewer principale: la finestra rimane aperta.\n"
        "    → La miniatura selezionata viene evidenziata con un bordo viola.\n"
        "    → Puoi cliccare quante miniature vuoi senza chiudere la finestra.\n"
        "    → Premi 'Chiudi' per chiudere la finestra di selezione.\n"
        "    → Premi '⬇ Scarica tutte dal server' per scaricare tutte le immagini della tipologia.\n\n"
        "── RILEVAMENTO YOLO ──────────────────────────\n"
        "15. Premi 'Rileva' per analizzare l'immagine con YOLO: persone, oggetti e facce.\n"
        "    Il pannello mostra titolo immagine, rilevamenti e caratteristiche da MongoDB.\n"
        "    Per immagini Personalizzate (premendo download) i dati vengono salvati automaticamente in MongoDB (collection nuovi_dati).\n\n"
        "16. Premi 'Scarica Simili dal Server' per cercare immagini simili tramite AI.\n"
        "    Tipologie rilevate: aerei, treni, auto, persone, altro.\n"
        "    Il sistema usa YOLO per rilevare la tipologia e interroga il servizio REST /simili.\n\n"
        "── RICERCA ───────────────────────────────────\n"
        "17. Usa la barra di ricerca in alto a destra, per cercare immagini per nome (ricerca in tempo reale da 3 caratteri).\n"
        "    → La ricerca funziona su tutte le tipologie (Aerei, Treni, Auto, Persone, Altro)\n"
        "      e anche sulle cartelle caricate manualmente con 'Carica Immagini'.\n"
        "    → Digitando meno di 3 caratteri la vista non cambia; da 3 in su parte la ricerca automatica.\n"
        "    → Svuotando la barra si torna automaticamente a tutte le immagini della categoria.\n"
        "    → Premi 🔍 o Invio per cercare, oppure 🤚 per resettare e tornare a tutte le immagini.\n\n"
        "── FILTRO FORMATO ────────────────────────────\n"
        "18. Usa i toggle button JPEG · PNG · ICO · BMP in alto a destra per filtrare per formato.\n"
        "    → VERDE = formato attivo (incluso nella vista).\n"
        "    → GRIGIO SCURO = formato non attivo (escluso dalla vista).\n"
        "    → Clicca un bottone per attivarlo/disattivarlo: la galleria si aggiorna subito.\n"
        "    → Se nessun formato corrisponde alle immagini caricate viene mostrato un avviso.\n"
        "    → Se deselezioni tutti i formati vengono mostrate tutte le immagini.\n"
        "    → Il filtro formato e la ricerca testo sono indipendenti: la ricerca testo cerca sempre\n"
        "      su tutti i file delle tipologie, il filtro formato filtra la vista senza testo.\n\n"
        "── DATABASE ──────────────────────────────────\n"
        "19. MongoDB contiene 3 collection: images (immagini per tipologia), users (credenziali), nuovi_dati (immagini esterne).\n"
        "    Il campo created_at registra data e ora italiana di ogni inserimento.\n"
        "    Compass si apre automaticamente dopo il seed puntando a mongodb://localhost:27017/myapp.\n\n"
        "── MENU IN ALTO ──────────────────────────────\n"
        "20. Tutti i bottoni del menu (File, Modifica, Visualizza, Guida) chiudono l'app e azzerano il token JWT.\n\n"
        "💡 Consigli: per resettare tutto usa 'docker compose down -v' poi riavvia con start.bat.\n\n"
        " Nel caso il bottone 'scarica simili dal Server' o 'Seleziona' diano errore 404, avviare docker compose up -d.\n\n"
        " Per passare da IPv6 a IPv4 e visualizzare i log nei due servizi REST (CMD) cambiare nell'ultimo paragrafo di auth_api.py e image_api.py da '::' all'indirizzo 0.0.0.0 per tornare a visualizzarli.\n\n"
        " Per la visualizzazione browser (web) delle immagini si può utilizzare sia localhost sia 127.0.0.1 sulla porta 5001 specificando dov'è contenuta e il nome dell'immagine.\n\n"
        "In caso di errore nelle funzionalità, all'interno della GUI, eseguire a parte da VS Code il docker-compose.yaml che installa tutte le dipendenze anche quelle più pesanti.\n\n"
    )

    testo.insert(END, istruzioni)
    testo.config(state=DISABLED)




try:
    icona = PhotoImage(file=os.path.join(PROJECT_DIR, "instruction_icon.png"))
    bottone_popup = ttk.Button(root, text=" Istruzioni", image=icona, compound="left", command=mostra_istruzioni)
except Exception as e:
    print("Icona non trovata o errore nel caricamento:", e)
    bottone_popup = ttk.Button(root, text="Istruzioni", command=mostra_istruzioni)

bottone_popup.place(relx=0.86, rely=0.12, relwidth=0.10, relheight=0.05, anchor="nw")



bottone = ttk.Button(root, text="Apri", command=apri_file)
bottone.place(relx=0.03, rely=0.21, relwidth=0.12, relheight=0.06)



menubar = Menu(root)
root.config(menu=menubar)  

File_menu = Menu(menubar, tearoff=0)
Modifica_menu = Menu(menubar, tearoff=0)
Visualizza_menu = Menu(menubar, tearoff=0)
Guida_menu = Menu(menubar, tearoff=0)
Altro_menu = Menu(menubar)

file_altro_submenu = Menu(File_menu, tearoff=0)
file_altro_submenu.add_command(label='Disponibilità Aggiornamenti', command=root.quit)
file_altro_submenu.add_command(label='About galleria Tipologie', command=root.quit)

File_menu.add_command(label='Nuovo', command=root.quit)
File_menu.add_separator()
File_menu.add_command(label='Apri', command=root.quit)
File_menu.add_separator()
File_menu.add_cascade(label='Altro', menu=file_altro_submenu)
File_menu.add_separator()
File_menu.add_command(label='Exit', command=root.quit)


Modifica_menu.add_command(label='Taglia', command=root.quit)
Modifica_menu.add_separator()
Modifica_menu.add_command(label='Copia', command=root.quit)
Modifica_menu.add_separator()
Modifica_menu.add_cascade(label='Incolla', command=root.quit)
Modifica_menu.add_separator()
Modifica_menu.add_command(label='Cerca', command=root.quit)


Visualizza_menu.add_command(label='Apri finestra', command=root.quit)
Visualizza_menu.add_separator()
Visualizza_menu.add_command(label='Esegui', command=root.quit)
Visualizza_menu.add_separator()
Visualizza_menu.add_cascade(label='Debug', command=root.quit)
Visualizza_menu.add_separator()
Visualizza_menu.add_command(label='Terminale', command=root.quit)


Guida_menu.add_command(label='FAQ', command=root.quit)
Guida_menu.add_separator()
Guida_menu.add_command(label='Estensioni', command=root.quit)
Guida_menu.add_separator()
Guida_menu.add_cascade(label='Guarda Licenza', command=root.quit)
Guida_menu.add_separator()
Guida_menu.add_command(label='Video Introduttivo', command=root.quit)


menubar.add_cascade(label='File', menu=File_menu)
menubar.add_cascade(label='Modifica', menu=Modifica_menu)
menubar.add_cascade(label='Visualizza', menu=Visualizza_menu)
menubar.add_cascade(label='Guida', menu=Guida_menu)



Button(root, text="Carica Immagini", bg="orange", command=carica_immagini).place(relx=0.21, rely=0.21, relwidth=0.12, relheight=0.06)
btn_rileva = Button(root, text="Rileva", bg="#2e7d32", fg="white", command=rileva_immagine)
btn_rileva.place(relx=0.34, rely=0.21, relwidth=0.09, relheight=0.06)
frame_bottoni = Frame(root, bg="#5a5e59")
frame_bottoni.place(relx=0.45, rely=0.88, relwidth=0.52, anchor="nw", height=34)

Button(frame_bottoni, text="← Precedente", command=immagine_precedente, width=12).pack(side=LEFT)
Button(frame_bottoni, text="Successiva →", command=immagine_successiva, width=12).pack(side=RIGHT)

frame_azioni = Frame(frame_bottoni, bg="#5a5e59")
frame_azioni.pack(side=LEFT, expand=True)

Button(frame_azioni, text="⬇ Download", bg="#1565c0", fg="white", command=scarica_immagine, width=9).pack(side=LEFT, padx=2)
Button(frame_azioni, text="🗑 Elimina",  bg="#b71c1c", fg="white", command=elimina_da_downloads, width=9).pack(side=LEFT, padx=2)
Button(frame_azioni, text="🔄 Sync",     bg="#00695c", fg="white", command=lambda: sincronizza_downloads(False), width=9).pack(side=LEFT, padx=2)


root.after(30_000, _avvia_auto_sync)



image_label = Label(root, bg="white", bd=0)
image_label.place(relx=0.45, rely=0.35, relwidth=0.52, relheight=0.53)
image_label.bind("<Configure>", lambda e: mostra_immagine())



status_frame = Frame(root, bd=1, relief=SUNKEN, bg="#dddddd")
status_frame.pack(side=BOTTOM, fill=X)

status_icon = Label(status_frame, bg="#dddddd")
status_icon.pack(side=LEFT, padx=5)

status_bar = Label(status_frame, text="Benvenuto nella galleria!", anchor=W, bg="#dddddd", fg="black")
status_bar.pack(side=LEFT, fill=X, expand=True)


def inizializza_formati():
    """Inizializza le variabili per i checkbox dei formati immagine"""
    global formati_var
    formati_var = {
        'JPEG': IntVar(value=1),
        'PNG': IntVar(value=1),
        'ICO': IntVar(value=0),
        'BMP': IntVar(value=0)
    }

def applica_filtro_formato():
    """Chiamata dalle checkbox: filtra le immagini per estensione e aggiorna il viewer."""
    global image_paths, current_image_index, _original_image_paths

    if not _original_image_paths:
        aggiorna_status("Carica prima una categoria di immagini", "error")
        return

    map_ext = {
        'JPEG': ('.jpg', '.jpeg'),
        'PNG':  ('.png',),
        'ICO':  ('.ico',),
        'BMP':  ('.bmp',),
    }
    estensioni_attive = []
    for fmt, var in formati_var.items():
        if var.get() == 1:
            estensioni_attive.extend(map_ext[fmt])

    if not estensioni_attive:

        image_paths = _original_image_paths.copy()
        current_image_index = 0
        mostra_immagine()
        aggiorna_status("Nessun filtro formato attivo — mostro tutte le immagini", "info")
        return

    estensioni_attive = tuple(estensioni_attive)
    risultati = [p for p in _original_image_paths if p.lower().endswith(estensioni_attive)]

    if risultati:
        image_paths = risultati
        current_image_index = 0
        mostra_immagine()
        fmt_attivi = [f for f, v in formati_var.items() if v.get() == 1]
        aggiorna_status(
            f"Filtro formato: {', '.join(fmt_attivi)} → {len(risultati)} immagini", "success")
    else:
        aggiorna_status("Nessuna immagine con i formati selezionati", "error")

def cerca_immagini(realtime=False):
    query = entry_ricerca.get().strip().lower()

    global image_paths, current_image_index, _original_image_paths


    if not _original_image_paths:
        if image_paths:
            _original_image_paths = image_paths.copy()
        else:
            if not realtime:
                aggiorna_status("Carica prima una categoria di immagini", "error")
            return

    if not query:
        reset_ricerca()
        return


    risultati = []
    exact_match = None

    for img_path in _original_image_paths:
        nome_file = os.path.splitext(os.path.basename(img_path))[0].lower()
        if query == nome_file:
            exact_match = img_path
            risultati = [img_path]
            break
        elif query in nome_file:
            risultati.append(img_path)

    if exact_match is not None:
        image_paths = risultati
        current_image_index = 0
        if not realtime:
            aggiorna_status(f"Trovato match esatto: {os.path.basename(image_paths[0])}", "success")
    elif risultati:
        image_paths = risultati
        current_image_index = 0
        if not realtime:
            aggiorna_status(f"Trovati {len(risultati)} risultati per '{query}'", "success")
    else:
        aggiorna_status(f"Nessun risultato per '{query}'", "error")
        return

    mostra_immagine()

    if realtime:
        aggiorna_status(f"Ricerca: {len(risultati)} risultati per '{query}'", "info")

            
def reset_ricerca():
    """Resetta la ricerca e mostra tutte le immagini"""
    global image_paths, current_image_index, _original_image_paths

    if _original_image_paths:
        image_paths = _original_image_paths.copy()
        current_image_index = 0
        mostra_immagine()
        aggiorna_status("Ricerca resettata - Mostro tutte le immagini", "info")
    try:
        entry_ricerca.delete(0, END)
    except (NameError, Exception):
        pass


def scarica_simili():
    """
    Trova e scarica immagini simili usando il SERVER REST.
    Workflow:
      1. Rileva tipologia con YOLO (locale, veloce)
      2. Chiama POST /simili con la tipologia → server ritorna lista filename
      3. Per ogni file → GET /images/<filename> → salva in downloads/simili_<tipologia>/
    """
    if not image_paths:
        messagebox.showwarning("Attenzione", "Carica prima un'immagine!"); return

    img_path = image_paths[current_image_index]
    aggiorna_status("🤖 Rilevamento tipologia in corso...", "info")

    def worker():
        try:

            _raw = model(img_path, verbose=False)
            results = _raw[0] if isinstance(_raw, (list, tuple)) and len(_raw) > 0 else _raw
            if not hasattr(results, "boxes"):
                from ultralytics import YOLO as _YOLO
                globals()["model"] = _YOLO(os.path.join(PROJECT_DIR, "yolov8n.pt"))
                results = globals()["model"](img_path, verbose=False)[0]

            mappa_tip = {
                "person": "persone",
                "car": "auto", "truck": "auto", "bus": "auto", "motorcycle": "auto",
                "train": "treni", "airplane": "aerei",
            }
            conteggi = {}
            for box in results.boxes:
                lbl = model.names[int(box.cls[0])]
                conteggi[mappa_tip.get(lbl, "altro")] = conteggi.get(mappa_tip.get(lbl, "altro"), 0) + 1

            tipologia = max(conteggi, key=conteggi.get) if conteggi else "altro"
            print(f"🎯 Tipologia rilevata: {tipologia}  (conteggi: {conteggi})")
            root.after(0, lambda t=tipologia: aggiorna_status(
                f"🎯 Tipologia: {t} — interrogo il server...", "info"))


            headers = {"Authorization": jwt_token} if jwt_token else {}
            try:
                res = requests.post(API_SIMILI, json={"tipologia": tipologia},
                                    headers=headers, timeout=10)
            except Exception as ex:
                err = str(ex)
                root.after(0, lambda m=err: messagebox.showerror(
                    "Server non raggiungibile",
                    f"Impossibile contattare il server REST.\n"
                    f"Verifica che il container sia attivo: docker compose ps\n\nErrore: {m}"))
                return

            if res.status_code != 200:
                root.after(0, lambda c=res.status_code, t=res.text[:200]: messagebox.showerror(
                    "Errore server", f"HTTP {c}\n{t}"))
                return

            simili = res.json().get("simili", [])
            print(f"📋 Server ha risposto con {len(simili)} immagini simili")
            for s in simili:
                print(f"   • {s.get('filename', '?')}  (fonte: {s.get('fonte', '?')})")

            if not simili:
                root.after(0, lambda t=tipologia: messagebox.showinfo(
                    "Nessun risultato",
                    f"Il server non ha trovato immagini simili per la tipologia '{t}'."))
                return


            anteprima = "\n".join(f"  • {s.get('filename', '?')}  ({s.get('fonte', '?')})"
                                  for s in simili[:15])
            piu = f"\n... e altri {len(simili) - 15}" if len(simili) > 15 else ""

            def chiedi_conferma():
                msg = (f"🎯 Tipologia: {tipologia}\n"
                       f"Il server ha trovato {len(simili)} immagini simili:\n\n"
                       f"{anteprima}{piu}\n\n"
                       f"Vuoi scaricarle in downloads/simili_{tipologia}/?")
                if not messagebox.askyesno("Scarica simili dal server", msg):
                    aggiorna_status("Operazione annullata", "info"); return


                cartella_dest = os.path.join(DOWNLOADS_DIR, f"simili_{tipologia}")
                os.makedirs(cartella_dest, exist_ok=True)

                def download_worker():
                    scaricate, saltate, errori = 0, 0, 0
                    err_dett = []
                    for i, s in enumerate(simili):
                        fn = s.get("filename", "")
                        if not fn:
                            errori += 1; err_dett.append("filename mancante"); continue
                        dest = os.path.join(cartella_dest, fn)
                        if os.path.exists(dest):
                            saltate += 1
                            print(f"⏭️  Già presente: {fn}")
                            continue
                        url_img = f"http://127.0.0.1:5001/images/{fn}"
                        root.after(0, lambda i=i, n=len(simili), fn=fn: aggiorna_status(
                            f"⬇ Download {i+1}/{n}: {fn}", "info"))
                        try:
                            r = requests.get(url_img, headers=headers, timeout=15)
                            if r.status_code == 200 and r.content:
                                with open(dest, "wb") as f: f.write(r.content)
                                scaricate += 1
                                print(f"✅ Scaricata da server: {fn}  ({len(r.content)} byte)")
                            else:
                                errori += 1
                                err_dett.append(f"{fn}: HTTP {r.status_code}")
                                print(f"❌ {fn}: HTTP {r.status_code}")
                        except Exception as ex:
                            errori += 1
                            err_dett.append(f"{fn}: {ex}")
                            print(f"❌ Eccezione {fn}: {ex}")

                    parti = []
                    if scaricate: parti.append(f"✅ {scaricate} scaricate")
                    if saltate:   parti.append(f"⏭️ {saltate} già presenti")
                    if errori:    parti.append(f"❌ {errori} errori")
                    riep = " · ".join(parti) if parti else "Nessuna operazione"
                    msg_fin = f"{riep}\n📁 {cartella_dest}\n🎯 Tipologia: {tipologia}"
                    if err_dett:
                        msg_fin += "\n\nErrori:\n" + "\n".join(err_dett[:5])
                    root.after(0, lambda r=riep: aggiorna_status(
                        f"🔄 {r}",
                        "success" if scaricate > 0 and errori == 0 else
                        ("error" if errori > 0 and scaricate == 0 else "info")))
                    root.after(0, lambda m=msg_fin: messagebox.showinfo("Download completato", m))

                threading.Thread(target=download_worker, daemon=True).start()

            root.after(0, chiedi_conferma)

        except Exception as e:
            err_msg = str(e)
            print(f"❌ Errore scarica_simili: {err_msg}")
            root.after(0, lambda msg=err_msg: aggiorna_status(f"Errore: {msg}", "error"))
            root.after(0, lambda msg=err_msg: messagebox.showerror("Errore", msg))

    threading.Thread(target=worker, daemon=True).start()


def ridimensiona_finestra():
    root.geometry("1200x800")
    aggiorna_status("Finestra ridimensionata a 1200x800", "info")

bottone_ridimensiona = Button(root, text="Ridimensiona", bg="#a86832", fg="white",
                              activebackground="#a832a8", command=ridimensiona_finestra)
bottone_ridimensiona.place(relx=0.50, rely=0.12, relwidth=0.11, relheight=0.05)
Button(root, text="Scarica Simili dal Server", bg="#6a0dad", fg="white",
       font=("Arial", 8), activebackground="#8b00ff",
       command=scarica_simili).place(relx=0.635, rely=0.12, relwidth=0.16, relheight=0.05)



TIPOLOGIE_DISPONIBILI = [
    "aerei", "treni", "auto", "persone", "altro"
]

def scarica_categoria():
    """
    Finestra di selezione tipologia con anteprima dinamica:
      • Selezioni tipologia → la finestra si espande mostrando le miniature
      • Click su una miniatura → l'immagine si carica nella GUI principale
      • Bottone Scarica → scarica TUTTE le immagini della tipologia dal server
    """
    global image_paths, current_image_index, current_genere

    win = Toplevel(root)
    win.title("📂 Esplora tipologia")
    win.geometry("520x250")
    win.resizable(False, False)
    win.configure(bg="#3c3f3b")
    win.grab_set()

    Label(win, text="📂 Esplora le tipologie disponibili",
          bg="#3c3f3b", fg="white",
          font=("Segoe UI Emoji", 12, "bold")).pack(pady=(12, 4))
    Label(win, text="Seleziona una tipologia per vedere le immagini",
          bg="#3c3f3b", fg="#cccccc", font=("Helvetica", 9)).pack(pady=(0, 8))


    sel_var = StringVar(value=TIPOLOGIE_DISPONIBILI[0])
    sel_frame = Frame(win, bg="#3c3f3b")
    sel_frame.pack(pady=4)
    Label(sel_frame, text="Tipologia:", bg="#3c3f3b", fg="white",
          font=("Helvetica", 10)).pack(side="left", padx=(0, 8))
    combo = ttk.Combobox(sel_frame, textvariable=sel_var, state="readonly",
                         values=TIPOLOGIE_DISPONIBILI, width=18)
    combo.pack(side="left")


    progress_label = Label(win, text="", bg="#3c3f3b", fg="#9ec5ff",
                           font=("Helvetica", 9), wraplength=480, justify="center")
    progress_label.pack(pady=4)


    galleria_frame = Frame(win, bg="#2a2a2a", relief="solid", bd=1)


    thumbs_cache = {}   
    btn_widgets = {}    
    sel_corrente = {"fn": None}

    def carica_in_gui(filename, tipologia):
        """Carica un'immagine nel viewer principale senza chiudere la finestra."""
        global image_paths, current_image_index, current_genere, _original_image_paths
        cartella = os.path.join(PROJECT_DIR, "images", tipologia)
        path = os.path.join(cartella, filename)
        if not os.path.exists(path):
            messagebox.showwarning("File mancante", f"Immagine non trovata:\n{path}")
            return
        ext_ok = (".png", ".jpg", ".jpeg", ".bmp", ".webp")
        tutte = sorted([os.path.join(cartella, f)
                        for f in os.listdir(cartella)
                        if f.lower().endswith(ext_ok)])
        image_paths = tutte
        _original_image_paths = tutte.copy()
        try:
            current_image_index = tutte.index(path)
        except ValueError:
            current_image_index = 0
        current_genere = tipologia.capitalize()
        mostra_immagine()
        aggiorna_status(f"📂 {filename} — usa ← → nel viewer per scorrere", "success")


        if sel_corrente["fn"] and sel_corrente["fn"] in btn_widgets:
            btn_widgets[sel_corrente["fn"]].config(bg="#1a1a1a", relief="flat", bd=2)
        if filename in btn_widgets:
            btn_widgets[filename].config(bg="#c015ba", relief="solid", bd=3)
        sel_corrente["fn"] = filename

    def aggiorna_galleria(*_):
        """Carica e visualizza le miniature della tipologia selezionata."""
        tipologia = sel_var.get()
        cartella = os.path.join(PROJECT_DIR, "images", tipologia)


        for w in galleria_frame.winfo_children():
            w.destroy()
        thumbs_cache.clear()
        btn_widgets.clear()
        sel_corrente["fn"] = None

        if not os.path.exists(cartella):
            progress_label.config(text=f"⚠️ Cartella '{tipologia}' non trovata",
                                  fg="#ff8888")
            galleria_frame.pack_forget()
            win.geometry("520x250")
            return

        ext_ok = (".png", ".jpg", ".jpeg", ".bmp", ".webp")
        files = sorted([f for f in os.listdir(cartella)
                        if f.lower().endswith(ext_ok)])

        if not files:
            progress_label.config(text=f"📭 Nessuna immagine in '{tipologia}'", fg="#ffaa00")
            galleria_frame.pack_forget()
            win.geometry("520x250")
            return

        progress_label.config(
            text=f"📷 {len(files)} immagini disponibili — clicca per visualizzare",
            fg="#9ec5ff")


        galleria_frame.pack(pady=10, padx=15, fill="both", expand=True)


        per_riga = 5
        righe = (len(files) + per_riga - 1) // per_riga
        nuova_h = 320 + righe * 110
        win.geometry(f"680x{nuova_h}")


        for i, fn in enumerate(files):
            r, c = divmod(i, per_riga)
            path = os.path.join(cartella, fn)
            try:
                pil = Image.open(path)
                pil.thumbnail((90, 90))
                thumb = ImageTk.PhotoImage(pil)
                thumbs_cache[fn] = thumb

                btn = Button(galleria_frame, image=thumb, bg="#1a1a1a",
                             activebackground="#3a3a3a", relief="flat", bd=2,
                             cursor="hand2",
                             command=lambda f=fn, t=tipologia: carica_in_gui(f, t))
                btn.grid(row=r * 2, column=c, padx=4, pady=4)
                btn_widgets[fn] = btn
                Label(galleria_frame, text=fn, bg="#2a2a2a", fg="white",
                      font=("Helvetica", 7), wraplength=95).grid(row=r * 2 + 1,
                                                                  column=c,
                                                                  padx=2,
                                                                  pady=(0, 4))
            except Exception as e:
                print(f"⚠️ Errore thumbnail {fn}: {e}")

    combo.bind("<<ComboboxSelected>>", aggiorna_galleria)

    btn_frame = Frame(win, bg="#3c3f3b")
    btn_frame.pack(side="bottom", pady=12)

    def scarica_tutte():
        """Scarica tutte le immagini della tipologia selezionata dal server REST."""
        tipologia = sel_var.get()
        cartella_dest = os.path.join(DOWNLOADS_DIR, f"tipologia_{tipologia}")
        os.makedirs(cartella_dest, exist_ok=True)

        def worker():
            headers = {"Authorization": jwt_token} if jwt_token else {}
            try:

                res = requests.post(
                    "http://127.0.0.1:5001/images",
                    json={"tipoImmagine": tipologia},
                    headers=headers, timeout=10
                )
                if res.status_code != 200:
                    root.after(0, lambda c=res.status_code, t=res.text[:200]:
                               messagebox.showerror("Errore server", f"HTTP {c}\n{t}"))
                    return
                files = res.json().get("images", [])
                if not files:
                    root.after(0, lambda: messagebox.showinfo(
                        "Nessuna immagine",
                        f"Il server non ha trovato immagini per '{tipologia}'."))
                    return


                scaricate, saltate, errori = 0, 0, 0
                for i, fn in enumerate(files):
                    dest = os.path.join(cartella_dest, fn)
                    if os.path.exists(dest):
                        saltate += 1; continue
                    root.after(0, lambda i=i, n=len(files), fn=fn:
                               progress_label.config(
                                   text=f"⬇ {i+1}/{n}: {fn}",
                                   fg="#9ec5ff"))
                    try:
                        r = requests.get(f"http://127.0.0.1:5001/images/{fn}",
                                         headers=headers, timeout=15)
                        if r.status_code == 200 and r.content:
                            with open(dest, "wb") as f: f.write(r.content)
                            scaricate += 1
                            print(f"✅ Scaricata: {fn}")
                        else:
                            errori += 1
                            print(f"❌ {fn}: HTTP {r.status_code}")
                    except Exception as ex:
                        errori += 1
                        print(f"❌ {fn}: {ex}")

                msg = (f"✅ {scaricate} scaricate"
                       + (f" · ⏭️ {saltate} già presenti" if saltate else "")
                       + (f" · ❌ {errori} errori" if errori else "")
                       + f"\n📁 {cartella_dest}")
                root.after(0, lambda m=msg: progress_label.config(text=m, fg="#80ff80"))
                root.after(0, lambda m=msg: messagebox.showinfo("Download completato", m))
                root.after(0, lambda: aggiorna_status(
                    f"✅ {scaricate} immagini scaricate in tipologia_{tipologia}/",
                    "success"))
            except Exception as e:
                err = str(e)
                root.after(0, lambda m=err: messagebox.showerror("Errore", m))

        threading.Thread(target=worker, daemon=True).start()

    Button(btn_frame, text="⬇ Scarica tutte dal server", bg="#1565c0", fg="white",
           font=("Helvetica", 10, "bold"), width=22,
           command=scarica_tutte).pack(side="left", padx=6)
    Button(btn_frame, text="Chiudi", bg="#555", fg="white",
           width=12, command=win.destroy).pack(side="left", padx=6)


    aggiorna_galleria()


def cerca_immagini_con_debounce(event=None):
    global debounce_id

    if debounce_id is not None:
        root.after_cancel(debounce_id)
        debounce_id = None

    query = entry_ricerca.get().strip().lower()

    if not query:

        reset_ricerca()
        return

    if len(query) < 3:

        return


    debounce_id = root.after(150, lambda: cerca_immagini(True))



inizializza_formati()

SEARCH_BAR_INIT_WIDTH = 500
SEARCH_BAR_MIN_WIDTH = 300

frame_ricerca_principale = Frame(root, bg="#5a5e59")
frame_ricerca_principale.place(relx=0.97, rely=0.02, anchor="ne")

frame_superiore = Frame(frame_ricerca_principale, bg="#5a5e59")
frame_superiore.pack(side=TOP, fill=X, pady=(0, 3))

label_formati = Label(frame_superiore, text="Formati:", 
                     bg="#5a5e59", fg="white", 
                     font=("Arial", 8, "bold"))
label_formati.pack(side=LEFT, padx=(0, 2))

frame_checkbox = Frame(frame_superiore, bg="#5a5e59")
frame_checkbox.pack(side=LEFT, fill=X)


_toggle_btns = {}

def _crea_toggle(fmt):
    """Crea un toggle button per il formato e lo collega a formati_var[fmt]."""
    attivo = formati_var[fmt].get() == 1
    btn = Button(
        frame_checkbox,
        text=fmt,
        font=("Arial", 8, "bold"),
        width=5,
        relief="flat",
        bd=0,
        cursor="hand2",
        bg="#86961a" if attivo else "#3c3c3c",
        fg="white",
        activeforeground="white",
    )
    def _toggle(f=fmt, b=btn):
        nuovo = 1 - formati_var[f].get()        
        formati_var[f].set(nuovo)
        b.config(bg="#86961a" if nuovo == 1 else "#3c3c3c",
                 activebackground="#6e7e14" if nuovo == 1 else "#555555")
        applica_filtro_formato()
    btn.config(command=_toggle,
               activebackground="#6e7e14" if attivo else "#555555")
    btn.pack(side=LEFT, padx=3, pady=1, ipady=2)
    _toggle_btns[fmt] = btn

for formato in formati_var:
    _crea_toggle(formato)

frame_ricerca_completo = Frame(frame_ricerca_principale, bg="#5a5e59")
frame_ricerca_completo.pack(side=BOTTOM, fill=X)

frame_ricerca = Frame(frame_ricerca_completo, bg="#3c285e", bd=1, relief=SOLID)
frame_ricerca.pack(side=LEFT, fill=BOTH, expand=True)

entry_ricerca = Entry(frame_ricerca, bg="white", fg="black", bd=0,
                     font=("Arial", 9))
entry_ricerca.pack(side=LEFT, fill=BOTH, expand=True, padx=2, pady=3)

entry_ricerca.bind("<Return>", lambda event: cerca_immagini())
entry_ricerca.bind("<KeyRelease>", cerca_immagini_con_debounce)

bottone_ricerca = Button(frame_ricerca, text="🔍", command=cerca_immagini,
                        bg="#86961a", fg="white", bd=0, width=3,
                        activebackground="#768a16", font=("Arial", 10))
bottone_ricerca.pack(side=RIGHT, fill=Y)

bottone_reset = Button(frame_ricerca_completo, text="↺", command=reset_ricerca,
                      bg="#c44536", fg="white", bd=0, width=3,
                      activebackground="#b23b2e", font=("Arial", 10))
bottone_reset.pack(side=LEFT, fill=Y, padx=(3, 0))

def adatta_ricerca(event=None):
    win_width = root.winfo_width()
    
    if win_width <= 1:
        return
    
    if win_width < 800:
        new_width = max(SEARCH_BAR_MIN_WIDTH, win_width * 0.4)
    else:
        new_width = SEARCH_BAR_INIT_WIDTH
    
    frame_ricerca_principale.config(width=int(new_width))
    frame_ricerca_principale.update_idletasks()

root.bind("<Configure>", adatta_ricerca)

adatta_ricerca()

bottone_popup.place(relx=0.97, rely=0.12, relwidth=0.15, relheight=0.05, anchor="ne")

Button(root, text="✅ Seleziona", bg="#c015ba", fg="white",
       activebackground="#0d47a1", command=scarica_categoria).place(relx=0.50, rely=0.05, relwidth=0.11, relheight=0.05)

root.mainloop()
