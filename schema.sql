-- Creazione delle tabelle del database

-- Tabella utenti
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

-- Tabella registrazioni
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

-- Note: Prima di eseguire questo script, assicurati di avere creato il database
-- e di avere i permessi necessari per creare tabelle e indici.