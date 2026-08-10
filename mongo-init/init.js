db = db.getSiblingDB("myapp");

print("🔧 [init.js] Inizializzazione database → myapp");

if (!db.getCollectionNames().includes("images")) {
    db.createCollection("images", {
        validator: {
            $jsonSchema: {
                bsonType: "object",
                required: ["filename", "titolo", "genere", "anno"],
                properties: {
                    filename: {
                        bsonType: "string",
                        description: "Nome file immagine — obbligatorio"
                    },
                    titolo: {
                        bsonType: "string",
                        description: "Titolo del film — obbligatorio"
                    },
                    genere: {
                        bsonType: "string",
                        enum: ["Azione", "Avventura", "Animazione", "Commedia"],
                        description: "Genere cinematografico — obbligatorio"
                    },
                    anno: {
                        bsonType: "string",
                        description: "Anno di uscita — obbligatorio"
                    },
                    descrizione: {
                        bsonType: "string"
                    },
                    animali_speciali: {
                        bsonType: "array",
                        items: { bsonType: "string" }
                    },
                    created_at: {
                        bsonType: "date",
                        description: "Timestamp di inserimento — gestito da seed_db_galleria.py"
                    }
                }
            }
        },
        validationLevel: "moderate",   
        validationAction: "warn"        
    });

    
    db.images.createIndex({ genere: 1 }, { name: "idx_genere" });
    
    db.images.createIndex({ filename: 1 }, { unique: true, name: "idx_filename_unique" });

    print("✅ [init.js] Collection 'images' creata con validatore e indici");
} else {
    print("ℹ️  [init.js] Collection 'images' già esistente — skip creazione");
}

if (!db.getCollectionNames().includes("users")) {
    db.createCollection("users", {
        validator: {
            $jsonSchema: {
                bsonType: "object",
                required: ["username", "password"],
                properties: {
                    username: {
                        bsonType: "string",
                        minLength: 3,
                        description: "Username — obbligatorio, min 3 caratteri"
                    },
                    password: {
                        bsonType: "string",
                        minLength: 4,
                        description: "Password — obbligatoria, min 4 caratteri"
                    }
                }
            }
        },
        validationLevel: "strict",
        validationAction: "error"
    });

    
    db.users.createIndex({ username: 1 }, { unique: true, name: "idx_username_unique" });

    print("✅ [init.js] Collection 'users' creata con validatore e indice univoco");
} else {
    print("ℹ️  [init.js] Collection 'users' già esistente — skip creazione");
}


if (db.users.countDocuments() === 0) {
    db.users.insertMany([
        { username: "admin",    password: "admin123" },
        { username: "giovanni", password: "pass1234" }
    ]);
    print("✅ [init.js] Utenti di default inseriti (admin, giovanni)");
} else {
    print("ℹ️  [init.js] Utenti già presenti — skip inserimento default");
}


if (!db.getCollectionNames().includes("nuovi_dati")) {
    db.createCollection("nuovi_dati", {
        validator: {
            $jsonSchema: {
                bsonType: "object",
                required: ["filename"],
                properties: {
                    filename:    { bsonType: "string" },
                    descrizione: { bsonType: "string" },
                    percorso:    { bsonType: "string" },
                    persone:    { bsonType: "int" },
                    animali:    { bsonType: "int" },
                    oggetti:    { bsonType: "int" },
                    facce:      { bsonType: "int" },
                    dettaglio:  { bsonType: "object" },
                    created_at: { bsonType: "string" }
                }
            }
        },
        validationLevel: "moderate",
        validationAction: "warn"
    });

    db.nuovi_dati.createIndex({ filename: 1 }, { unique: true, name: "idx_nuovi_dati_filename" });
    print("✅ [init.js] Collection 'nuovi_dati' creata con validatore e indice univoco");
} else {
    print("ℹ️  [init.js] Collection 'nuovi_dati' già esistente — skip creazione");
}


print("🎉 [init.js] Setup myapp completato → collections: " +
      db.getCollectionNames().join(", "));