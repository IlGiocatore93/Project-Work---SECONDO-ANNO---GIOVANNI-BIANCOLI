# 🖼️🗂️ Galleria - Tipologie --> Project-Work DevOps 2026 --> SECONDO ANNO


![Python](https://img.shields.io/badge/Python-3.x-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-REST%20API-000000?style=for-the-badge&logo=flask&logoColor=white)
![MongoDB](https://img.shields.io/badge/MongoDB-8-47A248?style=for-the-badge&logo=mongodb&logoColor=white)
![PyMongo](https://img.shields.io/badge/PyMongo-Driver-47A248?style=for-the-badge&logo=mongodb&logoColor=white)
![PyJWT](https://img.shields.io/badge/PyJWT-JWT-000000?style=for-the-badge)
![Ultralytics](https://img.shields.io/badge/Ultralytics-YOLO-111111?style=for-the-badge)
![OpenCV](https://img.shields.io/badge/OpenCV-Image%20Processing-5C3EE8?style=for-the-badge&logo=opencv&logoColor=white)
![Pillow](https://img.shields.io/badge/Pillow-Image%20Processing-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Requests](https://img.shields.io/badge/Requests-HTTP-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Containerization-2496ED?style=for-the-badge&logo=docker&logoColor=white)



Benvenuto nel mio progetto Github!🛠️ Sono <h3>Giovanni</h3>, studente DevOps, amante dell'informatica e di ogni tecnologia esistente. In questo progetto viene ottimizzata la ricerca, l'autenticazione e lo scaricamento dal server, in una galleria di tipologie casuali, principalmente quando devo cambiare Tipologia o verificare le immagini che siano presenti nel server e l'orario a cui le scarichi ma soprattutto le informazioni che rileva con YOLO e i vari messaggi che vengono scritti sulla barra di caricamento.

⚙️Funzionalità:


 ▶ Per accedere all'interfaccia bisogna autenticarsi tramite credenziali (JWT), nel caso vengano inserite errate, dà un messaggio di errore con un messaggio di timing per poter inserire nuovamente le credenziali fino a tre volte poi si      chiude automaticamente

 
 ▶ La finestra dell'interfaccia(Galleria - Tipologie) è "responsive", ovvero tutti i componenti all'interno di essa si muovono in modo proporzionale se allarghi o restringi la finestra dell'interfaccia

 
 ▶ E' possibile scorrere il "menu" in alto a sinistra aprendo delle tendine per ogni sezione: file, modifica, visualizza, guida con l'ulteriore possibilità di scorrere nelle sottosezioni

 
 ▶ Nell'area di testo, collegata al tasto "apri", è possibile visualizzare il contenuto all'interno dei file .txt e successivamente si possono salvare con un altro nome

 
 ▶ Col tasto "carica immagini", è possibile caricare una cartella [immagini] generica o [images] specifica, oppure selezionando direttamente la cartella della tipologia scelta('aerei' o 'treni' o 'auto' o 'persone' o 'altro'), proiettandolo direttamente nel photo viewer, inoltre sfruttando i bottoni precedente e successiva, si possono scorrere le immagini

 
 ▶ Sotto al photoviewer sono presenti tre bottoni, che agiscono sulla singola immagine, "Download" ti fa scaricare la singola immagine, "Elimina" ti fa eliminare le singole immagini appena salvate o se già presenti nella cartella mandandoti un messaggio di conferma e togliendole da dentro la cartella, "Sync" invece, ti fa sincronizzare le informazioni da quando viene salvata l'immagine aggiornando l'orario, ogni volta che se ne salva una nuova, e con la cartella downloads e MongoDB appena si clicca sul bottone

 
 ▶ Con il bottone "Rileva" è possibile, data una specifica cartella, cercare: (volti o oggetti o animali) in quelle determinate immagini e categorizzarle con YOLO, inoltre è possibile salvare in MongoDB i seguenti dati, dopo che vengono registrati con alcuni parametri(data e ora di creazione, descrizione, nome del file, marca, modello, tipo)

 
 ▶ Nel pannello "informazione immagine" possiamo visualizzare alcune caratteristiche dell'immagine selezionata (nome file, genere, formato, dimensione(peso), risoluzione(pixel), data creazione(se modificata), posizione, percorso)

 
 ▶ Nel bordo sotto dell'interfaccia, è presente una "barra di stato" nel quale viene mostrato un messaggio nel momento in cui l'immagine caricata con successo(v) della visualizzazione(i), e dell'errore nel trovare l'immagine(x), viene anche visualizzato, se selezionata (una cartella generica), fa vedere l'ordine esatto delle immagini, come viene visualizzata, inoltre se i downloads e i dati di MongoDB si sono sincronizzati

 
 ▶ E' possibile scorrere, da una tipologia all'altra, semplicemente cliccando, su una delle cinque tipologie(aerei, treni, auto, persone e altro)

 
 ▶ Nell'interfaccia, è anche presente il bottone "istruzioni", nel quale, cliccandolo, apre un popup, con tutte le indicazioni e le funzionalità legate a quest'app

 
 ▶ Sulla destra dell'interfaccia, troviamo, inoltre, il bottone "ridimensiona", che quando cliccato, ripristina la finestra alle dimesioni originarie, prima delle modifiche

 
 ▶ In alto a destra, dell'interfaccia, abbiamo la "barra di ricerca automatica", nel quale, è possibile digitare il nome di una specifica immagine, e al terzo carattere digitato, verrà già mostrata oppure cliccando sulla lente nel tasto a fianco, nel caso, si debba pulire la barra, si usa, il tasto rosso accanto chiamato "pulisci"

 
 ▶ Sopra la barra, sono presenti dei bottoni selezionabili in base al formato immagine(jpeg, png, ico, bmp) che si vuole ricercare, dalla barra di ricerca automatica

 
 ▶ Sopra il photoviewer è presente il tasto "Scarica Immagini dal Server", praticamente controlla se nel server sono presenti immagini uguali a quelle che stai scaricando, della stessa tipologia e nel caso te le fa scaricare e te le divide per tipologia 

 
 ▶ Sopra è presente il tasto "Seleziona", ovvero ti dà la possibilità, attraverso un popup(Esplora Tipologie), di scegliere con un menù a tendina all'interno, la Tipologia, con un anteprima di tutte le immagini per categoria, conteggiandoti per categoria quante sono le immagini e c'è la scelta volendo di scaricarle attraverso il bottone "scarica tutte dal server"

 
 ▶ Utilizzo moduli per avere un interfaccia più snella e dinamica come "ttk", moduli per la comunicazione con le cartelle tramite "filedialog", moduli per la visualizzazzione dei messaggi di caricamento e di errore con "messagebox", moduli per interagine con il sistema operativo presente tramite "os", moduli per lavorare con date e orari utilizzando "datetime" e moduli per utilizzare le pause e le misure temporali con "time", inoltre il modulo "timezone " per il riconoscimento del fuso orario in ogni zona del mondo

 
 ▶ Utilizzo della libreria "Pillow" potendo caricare immagini in molteplici formati, visualizzando, caricando, creando e salvando ogni qualsivoglia immagine

 
 ▶ Viene creata tramite un container Docker dei microservizi REST(auth_api - "sulla porta 5000" e image_api - "sulla porta 5001") nel quale fa visualizzare tramite modulo IpV4 e IpV6 le immagini .png tramite un servizio web

 
 ▶ Ho creato un file chiamato seed_db_galleria.py che esegue un injection nel database MongoDB e lo popola, successivamente ho sviluppato un bat che automatizzava il tutto: Apertura Docker + Esecuzione see_db_galleria.py + Apertura MongoDB con già credenziali attive 
 

🐍Anteprima dell'interfaccia🪟:




<img width="1698" height="816" alt="avvio python seed_db_galleria py(cmd)" src="https://github.com/user-attachments/assets/e9b1bf91-30ec-47b9-a103-941a308a0d76" />
<img width="1733" height="523" alt="avvio rapido-start bat(cmd)" src="https://github.com/user-attachments/assets/f4fce4e0-8dd1-4ab7-ae5d-23d5c003acfa" />
<img width="1607" height="670" alt="docker" src="https://github.com/user-attachments/assets/66076b9c-8e27-46d2-869e-885c24f3425c" />
<img width="431" height="387" alt="blocco autenticazione(delay)" src="https://github.com/user-attachments/assets/26588852-a1dc-4c32-8171-adb610542c48" />
<img width="1246" height="920" alt="bottone rileva-rilevazione yolo" src="https://github.com/user-attachments/assets/ed6fb190-6f15-47cb-9b6c-04649732f1a6" />
<img width="1567" height="915" alt="bottone istruzioni" src="https://github.com/user-attachments/assets/bc261c4d-b732-4232-8d7d-2466b46f2b52" />
<img width="1494" height="1021" alt="bottone seleziona-esplora tipologie-scarica tutte dal server" src="https://github.com/user-attachments/assets/9d4e47ad-d0e9-4222-8462-68c849bff900" />
<img width="1865" height="690" alt="mongo1" src="https://github.com/user-attachments/assets/7e28d51f-beb5-49c9-b837-cc9ed94b6192" />

<br>


💻Tecnologia utilizzata: 🔖 Python 3.x, 🔖 tkinter + ttk + filedialog + messagebox, 🔖 pillow(gestione immagini), 🔖 flask, 🔖 MongoDB, 🔖 YOLO, 🔖 OpenCV, 🔖 Docker


<br>


🌟Una volta autenticato, esplora ogni singola funzionalità dell'applicazione, dalla visualizzazione delle Tipologie(immagini) da dentro il photoviewer ad una visualizzazzione via web grazie ai microservizi API REST, da Cloud a Web in un attimo!!😯🔥

<br>



🔑Requisiti: Assicurati di avere Python 3 installato correttamente. Ti consiglio di creare un ambiente virtuale per evitare conflitti tra pacchetti:

<br>


# Creazione di un ambiente virtuale (cmd da dentro la cartella-->poi prompt dei comandi):
- \Python313\python.exe -m venv .                --> # in Windows
- Scripts\activate           
- code .                                         --> # IDE Visual Studio Code




# Installazione delle dipendenze necessarie:
- pip install ttk
- pip install flask
- pip install requests
- pip install pymongo
- pip install ultralytics
- pip install tzdata
- pip install pillow
- pip install opencv
- pip install pyJWT




# Avvio dell'applicativo:
python app2.py


<br>


🤝 Vuoi contribuire e migliorare il progetto?💭 Apri una Issue o una Pull Request su Github!💡


<br>


Licenza: MIT - Libero di esplorare, migliorare e condividere.


<br>



🧑‍💻 Creato da: [Giovanni](https://github.com/IlGiocatore93)



<br>


🤙 Se ti è piaciuto il progetto, lascia una ✨ su GitHub!🌐





