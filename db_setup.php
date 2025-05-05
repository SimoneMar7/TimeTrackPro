<?php
// Configurazione del database per l'applicazione APM
// Questo script crea la tabella necessaria nel database

// Includi la connessione al database
require_once 'includes/db_connect.php';

// SQL per creare la tabella registrazioni (adattato per PostgreSQL)
$sql = "CREATE TABLE IF NOT EXISTS registrazioni (
    id SERIAL PRIMARY KEY,
    data DATE NOT NULL,
    ingresso TIME NOT NULL,
    uscita TIME NOT NULL,
    apm_ore INT NOT NULL,
    apm_minuti INT NOT NULL,
    pausa_minuti INT NOT NULL,
    totale_minuti INT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)";

// Esegui la query usando PDO
try {
    $conn_pdo->exec($sql);
    echo "Tabella 'registrazioni' creata con successo o già esistente.";
} catch (PDOException $e) {
    echo "Errore nella creazione della tabella: " . $e->getMessage();
}
?>

<p>Dopo aver eseguito questo script, <a href="index.php">torna all'applicazione</a>.</p>
