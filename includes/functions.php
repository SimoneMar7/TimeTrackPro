<?php
/**
 * File con funzioni di utilità per l'applicazione
 */

/**
 * Converte minuti in formato ore:minuti leggibile
 * @param int $minutes Numero totale di minuti
 * @return string Tempo formattato come "ore:minuti"
 */
function formatMinutesToHoursMinutes($minutes) {
    $hours = floor($minutes / 60);
    $mins = $minutes % 60;
    return sprintf("%02d:%02d", $hours, $mins);
}

/**
 * Calcola il totale dei minuti in base a APM e pausa
 * @param int $apm_ore Ore APM
 * @param int $apm_minuti Minuti APM
 * @param int $pausa_minuti Minuti di pausa
 * @return int Totale dei minuti
 */
function calcolaTotaleMinuti($apm_ore, $apm_minuti, $pausa_minuti) {
    return ($apm_ore * 60 + $apm_minuti + $pausa_minuti);
}

/**
 * Valida i dati del form
 * @param array $data Array con i dati da validare
 * @return array Array con errori o vuoto se tutto ok
 */
function validaFormRegistrazione($data) {
    $errors = [];
    
    // Validazione data
    if (empty($data['data'])) {
        $errors['data'] = "La data è obbligatoria";
    }
    
    // Validazione orario ingresso
    if (empty($data['ingresso'])) {
        $errors['ingresso'] = "L'orario di ingresso è obbligatorio";
    }
    
    // Validazione orario uscita
    if (empty($data['uscita'])) {
        $errors['uscita'] = "L'orario di uscita è obbligatorio";
    }
    
    // Validazione APM ore (0-23)
    if (!isset($data['apm_ore']) || !is_numeric($data['apm_ore']) || $data['apm_ore'] < 0 || $data['apm_ore'] > 23) {
        $errors['apm_ore'] = "Le ore APM devono essere tra 0 e 23";
    }
    
    // Validazione APM minuti (0-59)
    if (!isset($data['apm_minuti']) || !is_numeric($data['apm_minuti']) || $data['apm_minuti'] < 0 || $data['apm_minuti'] > 59) {
        $errors['apm_minuti'] = "I minuti APM devono essere tra 0 e 59";
    }
    
    // Validazione pausa (valore ammesso: 15, 30, 45)
    $pauseValide = [15, 30, 45];
    if (!isset($data['pausa_minuti']) || !in_array($data['pausa_minuti'], $pauseValide)) {
        $errors['pausa_minuti'] = "Seleziona una pausa valida";
    }
    
    return $errors;
}

/**
 * Ottiene le registrazioni per una settimana specifica
 * @param object $conn Connessione al database
 * @param string $data Data di riferimento per la settimana
 * @return array Registrazioni della settimana
 */
function getRegistrazioniSettimanali($conn, $data) {
    global $conn_pdo;
    
    // Calcola il primo giorno della settimana (lunedì)
    $timestamp = strtotime($data);
    $giorno_settimana = date('N', $timestamp);
    $inizio_settimana = date('Y-m-d', strtotime("-" . ($giorno_settimana - 1) . " days", $timestamp));
    $fine_settimana = date('Y-m-d', strtotime("+6 days", strtotime($inizio_settimana)));
    
    $sql = "SELECT * FROM registrazioni 
            WHERE data BETWEEN :inizio AND :fine 
            ORDER BY data ASC";
    
    try {
        $stmt = $conn_pdo->prepare($sql);
        $stmt->bindParam(':inizio', $inizio_settimana);
        $stmt->bindParam(':fine', $fine_settimana);
        $stmt->execute();
        
        $registrazioni = [];
        $totale_settimanale = 0;
        
        while ($row = $stmt->fetch(PDO::FETCH_ASSOC)) {
            $registrazioni[] = $row;
            $totale_settimanale += $row['totale_minuti'];
        }
        
        return [
            'registrazioni' => $registrazioni,
            'totale' => $totale_settimanale,
            'inizio_settimana' => $inizio_settimana,
            'fine_settimana' => $fine_settimana
        ];
    } catch (PDOException $e) {
        // In caso di errore, registra l'errore e restituisci un array vuoto
        error_log("Errore durante il recupero delle registrazioni settimanali: " . $e->getMessage());
        return [
            'registrazioni' => [],
            'totale' => 0,
            'inizio_settimana' => $inizio_settimana,
            'fine_settimana' => $fine_settimana
        ];
    }
}

/**
 * Ottiene le registrazioni per un mese specifico
 * @param object $conn Connessione al database
 * @param string $anno Anno
 * @param string $mese Mese
 * @return array Registrazioni del mese
 */
function getRegistrazioniMensili($conn, $anno, $mese) {
    global $conn_pdo;
    
    $primo_giorno = "$anno-$mese-01";
    $ultimo_giorno = date('Y-m-t', strtotime($primo_giorno));
    
    $sql = "SELECT * FROM registrazioni 
            WHERE data BETWEEN :primo AND :ultimo 
            ORDER BY data ASC";
    
    try {
        $stmt = $conn_pdo->prepare($sql);
        $stmt->bindParam(':primo', $primo_giorno);
        $stmt->bindParam(':ultimo', $ultimo_giorno);
        $stmt->execute();
        
        $registrazioni = [];
        $totale_mensile = 0;
        
        while ($row = $stmt->fetch(PDO::FETCH_ASSOC)) {
            $registrazioni[] = $row;
            $totale_mensile += $row['totale_minuti'];
        }
        
        return [
            'registrazioni' => $registrazioni,
            'totale' => $totale_mensile,
            'primo_giorno' => $primo_giorno,
            'ultimo_giorno' => $ultimo_giorno
        ];
    } catch (PDOException $e) {
        // In caso di errore, registra l'errore e restituisci un array vuoto
        error_log("Errore durante il recupero delle registrazioni mensili: " . $e->getMessage());
        return [
            'registrazioni' => [],
            'totale' => 0,
            'primo_giorno' => $primo_giorno,
            'ultimo_giorno' => $ultimo_giorno
        ];
    }
}

/**
 * Formatta una data in formato italiano
 * @param string $data Data in formato Y-m-d
 * @return string Data in formato italiano (d/m/Y)
 */
function dataItaliana($data) {
    return date('d/m/Y', strtotime($data));
}

/**
 * Restituisce il nome del mese in italiano
 * @param int $mese Numero del mese (1-12)
 * @return string Nome del mese in italiano
 */
function nomeMese($mese) {
    $mesi = [
        1 => 'Gennaio',
        2 => 'Febbraio',
        3 => 'Marzo',
        4 => 'Aprile',
        5 => 'Maggio',
        6 => 'Giugno',
        7 => 'Luglio',
        8 => 'Agosto',
        9 => 'Settembre',
        10 => 'Ottobre',
        11 => 'Novembre',
        12 => 'Dicembre'
    ];
    
    return $mesi[(int)$mese];
}
?>
