<?php
// Includi file di configurazione e funzioni
require_once 'includes/db_connect.php';
require_once 'includes/functions.php';

// Avvia la sessione per i messaggi
session_start();

// Determina l'azione da eseguire
$action = isset($_REQUEST['action']) ? $_REQUEST['action'] : '';

switch ($action) {
    case 'salva':
        // Gestisce il salvataggio di una nuova registrazione
        salvaRegistrazione();
        break;
        
    case 'elimina':
        // Gestisce l'eliminazione di una registrazione
        eliminaRegistrazione();
        break;
        
    default:
        // Azione non valida, reindirizza alla home
        $_SESSION['success_message'] = "Operazione non valida.";
        header("Location: index.php");
        exit();
}

/**
 * Salva una nuova registrazione nel database
 */
function salvaRegistrazione() {
    global $conn, $conn_pdo;
    
    // Ottieni i dati dal form
    $data = [
        'data' => $_POST['data'] ?? '',
        'ingresso' => $_POST['ingresso'] ?? '',
        'uscita' => $_POST['uscita'] ?? '',
        'apm_ore' => $_POST['apm_ore'] ?? 0,
        'apm_minuti' => $_POST['apm_minuti'] ?? 0,
        'pausa_minuti' => $_POST['pausa_minuti'] ?? 0,
        'totale_minuti' => $_POST['totale_minuti'] ?? 0
    ];
    
    // Valida i dati
    $errors = validaFormRegistrazione($data);
    
    if (empty($errors)) {
        try {
            // Prepara la query SQL per PostgreSQL
            $sql = "INSERT INTO registrazioni (data, ingresso, uscita, apm_ore, apm_minuti, pausa_minuti, totale_minuti) 
                    VALUES (:data, :ingresso, :uscita, :apm_ore, :apm_minuti, :pausa_minuti, :totale_minuti)";
            
            $stmt = $conn_pdo->prepare($sql);
            $stmt->bindParam(':data', $data['data']);
            $stmt->bindParam(':ingresso', $data['ingresso']);
            $stmt->bindParam(':uscita', $data['uscita']);
            $stmt->bindParam(':apm_ore', $data['apm_ore'], PDO::PARAM_INT);
            $stmt->bindParam(':apm_minuti', $data['apm_minuti'], PDO::PARAM_INT);
            $stmt->bindParam(':pausa_minuti', $data['pausa_minuti'], PDO::PARAM_INT);
            $stmt->bindParam(':totale_minuti', $data['totale_minuti'], PDO::PARAM_INT);
            
            // Esegui la query
            if ($stmt->execute()) {
                $_SESSION['success_message'] = "Registrazione salvata con successo!";
            } else {
                $_SESSION['error_message'] = "Errore nel salvataggio della registrazione.";
            }
        } catch (PDOException $e) {
            $_SESSION['error_message'] = "Errore nel salvataggio della registrazione: " . $e->getMessage();
            error_log("Errore nel salvataggio della registrazione: " . $e->getMessage());
        }
    } else {
        // Ci sono errori di validazione
        $_SESSION['errors'] = $errors;
    }
    
    // Reindirizza alla pagina principale
    header("Location: index.php");
    exit();
}

/**
 * Elimina una registrazione dal database
 */
function eliminaRegistrazione() {
    global $conn, $conn_pdo;
    
    // Ottieni l'ID della registrazione da eliminare
    $id = isset($_GET['id']) ? (int)$_GET['id'] : 0;
    
    if ($id > 0) {
        try {
            // Prepara la query SQL per PostgreSQL
            $sql = "DELETE FROM registrazioni WHERE id = :id";
            
            $stmt = $conn_pdo->prepare($sql);
            $stmt->bindParam(':id', $id, PDO::PARAM_INT);
            
            // Esegui la query
            if ($stmt->execute()) {
                $_SESSION['success_message'] = "Registrazione eliminata con successo!";
            } else {
                $_SESSION['error_message'] = "Errore nell'eliminazione della registrazione.";
            }
        } catch (PDOException $e) {
            $_SESSION['error_message'] = "Errore nell'eliminazione della registrazione: " . $e->getMessage();
            error_log("Errore nell'eliminazione della registrazione: " . $e->getMessage());
        }
    } else {
        $_SESSION['error_message'] = "ID registrazione non valido.";
    }
    
    // Determina da dove proviene la richiesta per il reindirizzamento
    $referer = $_SERVER['HTTP_REFERER'] ?? 'index.php';
    header("Location: $referer");
    exit();
}
?>
