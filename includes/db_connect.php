<?php
// Configurazione della connessione al database
// Utilizzando le variabili di ambiente fornite da Replit

$servername = getenv("PGHOST") ?: "localhost";
$username = getenv("PGUSER") ?: "postgres";
$password = getenv("PGPASSWORD") ?: "";
$dbname = getenv("PGDATABASE") ?: "postgres";
$port = getenv("PGPORT") ?: "5432";

// Crea connessione usando PDO per compatibilità con PostgreSQL
try {
    $dsn = "pgsql:host=$servername;port=$port;dbname=$dbname;";
    $conn_pdo = new PDO($dsn, $username, $password, [PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION]);
    
    // Creiamo anche un oggetto mysqli per compatibilità con il codice esistente
    $conn = new mysqli($servername, $username, $password, $dbname, $port);
    
    // Imposta il set di caratteri a utf8
    $conn->set_charset("utf8");
} catch (PDOException $e) {
    die("Connessione fallita: " . $e->getMessage());
} catch (Exception $e) {
    die("Errore: " . $e->getMessage());
}
?>
