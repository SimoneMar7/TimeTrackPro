# Guida all'installazione su Altervista Free

Questa guida ti aiuterà a installare l'applicazione "Form di Inserimento e Riepilogo Tempi APM" su un hosting Altervista Free.

## Prerequisiti

1. Un account Altervista Free
2. Accesso FTP al tuo spazio web
3. Aver abilitato Python su Altervista (dal pannello di controllo)
4. Accesso al database PostgreSQL da Altervista

## Passaggi per l'installazione

### 1. Preparazione dei file

1. Scarica tutti i file dell'applicazione dal repository
2. Assicurati che il file `passenger_wsgi.py` sia presente nella cartella principale

### 2. Configurazione del database

1. Accedi al pannello di controllo di Altervista
2. Vai alla sezione "Database"
3. Crea un nuovo database PostgreSQL
4. Annota le credenziali (nome utente, password, nome database)

### 3. Modifica delle variabili d'ambiente

1. Crea un file `.htaccess` nella cartella principale con il seguente contenuto:

```
SetEnv DATABASE_URL "postgresql://username:password@localhost/database_name"
SetEnv FLASK_APP "main.py"
SetEnv FLASK_ENV "production"
SetEnv SECRET_KEY "una_chiave_segreta_molto_lunga_e_complessa"
```

Sostituisci `username`, `password` e `database_name` con le tue credenziali di database.

### 4. Caricamento dei file

1. Utilizza un client FTP (come FileZilla) per caricare tutti i file sul tuo spazio web
2. Assicurati che la struttura delle cartelle sia mantenuta

### 5. Installazione delle dipendenze

Altervista Free ha già molte librerie Python preinstallate. Se hai bisogno di librerie aggiuntive, puoi installarle nella cartella locale del tuo progetto:

```bash
pip install -t ./lib pillow qrcode pyotp flask-sqlalchemy flask-login flask-wtf gunicorn psycopg2-binary xlsxwriter
```

### 6. Inizializzazione del database

1. Accedi via SSH al tuo spazio web (se disponibile) o usa phpPgAdmin
2. Esegui lo script di inizializzazione del database:

```sql
CREATE TABLE IF NOT EXISTS utenti (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(64) NOT NULL,
    cognome VARCHAR(64) NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(256) NOT NULL,
    password_chiaro VARCHAR(100), -- Per recupero amministratore
    otp_secret VARCHAR(32),
    otp_enabled BOOLEAN DEFAULT FALSE
);

CREATE TABLE IF NOT EXISTS registrazioni (
    id SERIAL PRIMARY KEY,
    data DATE NOT NULL,
    ingresso VARCHAR(5) NOT NULL,
    uscita VARCHAR(5) NOT NULL,
    apm_ore INTEGER NOT NULL DEFAULT 0,
    apm_minuti INTEGER NOT NULL DEFAULT 0,
    pausa_minuti INTEGER NOT NULL DEFAULT 30,
    totale_minuti INTEGER NOT NULL DEFAULT 0,
    utente_id INTEGER NOT NULL REFERENCES utenti(id)
);

-- Indici per migliorare le performance
CREATE INDEX IF NOT EXISTS idx_registrazioni_data ON registrazioni (data);
CREATE INDEX IF NOT EXISTS idx_registrazioni_utente_id ON registrazioni (utente_id);
CREATE INDEX IF NOT EXISTS idx_utenti_email ON utenti (email);
```

### 7. Configurazione per Passenger (WSGI)

Assicurati che il file `passenger_wsgi.py` contenga:

```python
import sys
import os

# Aggiungi la cartella lib al path di Python
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'lib'))

# Importa l'applicazione Flask
from main import app as application
```

### 8. Riavvio dell'applicazione

1. Dal pannello di controllo di Altervista, naviga alla sezione Python
2. Riavvia l'applicazione Python

## Risoluzione dei problemi comuni

### Errore "Internal Server Error"

- Controlla i log di errore nel pannello di controllo di Altervista
- Verifica che tutte le dipendenze siano installate correttamente
- Controlla le credenziali del database nel file `.htaccess`

### Problemi di connessione al database

- Verifica che il database PostgreSQL sia stato creato correttamente
- Controlla che le credenziali nel file `.htaccess` siano corrette
- Assicurati che l'utente del database abbia i permessi necessari

### Errori 404 (File non trovato)

- Controlla che tutti i file siano stati caricati nella posizione corretta
- Verifica che i permessi dei file siano impostati correttamente (in genere 755 per le cartelle e 644 per i file)

## Supporto

Se riscontri problemi nell'installazione, puoi:
1. Consultare la documentazione di Altervista per Python
2. Controllare i log di errore nel pannello di controllo
3. Richiedere assistenza al supporto di Altervista

Buon utilizzo dell'applicazione "Form di Inserimento e Riepilogo Tempi APM"!