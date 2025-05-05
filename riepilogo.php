<?php
// Includi file di configurazione e funzioni
require_once 'includes/db_connect.php';
require_once 'includes/functions.php';

// Inizializza variabili
$view = isset($_GET['view']) ? $_GET['view'] : 'settimanale';
$data_riferimento = isset($_GET['data']) ? $_GET['data'] : date('Y-m-d');
$anno = isset($_GET['anno']) ? (int)$_GET['anno'] : date('Y');
$mese = isset($_GET['mese']) ? (int)$_GET['mese'] : date('n');

// Ottieni i dati richiesti in base alla vista
$dati_riepilogo = [];
$titolo_pagina = '';

if ($view === 'settimanale') {
    $dati_riepilogo = getRegistrazioniSettimanali($conn, $data_riferimento);
    $titolo_pagina = "Riepilogo Settimanale";
} else if ($view === 'mensile') {
    $dati_riepilogo = getRegistrazioniMensili($conn, $anno, $mese);
    $titolo_pagina = "Riepilogo Mensile - " . nomeMese($mese) . " " . $anno;
}

// Controlla se ci sono messaggi di successo in sessione
session_start();
$success_message = '';
if (isset($_SESSION['success_message'])) {
    $success_message = $_SESSION['success_message'];
    unset($_SESSION['success_message']);
}

// Includi l'header
include 'includes/header.php';
?>

<div class="row mb-4">
    <div class="col-md-10 mx-auto">
        <div class="card">
            <div class="card-header bg-primary text-white d-flex justify-content-between align-items-center">
                <h2 class="h4 mb-0">
                    <?php if ($view === 'settimanale'): ?>
                        <i class="fas fa-calendar-week me-2"></i><?php echo $titolo_pagina; ?>
                    <?php else: ?>
                        <i class="fas fa-calendar-alt me-2"></i><?php echo $titolo_pagina; ?>
                    <?php endif; ?>
                </h2>
                
                <div>
                    <?php if ($view === 'settimanale'): ?>
                        <a href="riepilogo.php?view=mensile" class="btn btn-light btn-sm">
                            <i class="fas fa-sync me-1"></i>Vai al mensile
                        </a>
                    <?php else: ?>
                        <a href="riepilogo.php?view=settimanale" class="btn btn-light btn-sm">
                            <i class="fas fa-sync me-1"></i>Vai al settimanale
                        </a>
                    <?php endif; ?>
                </div>
            </div>
            <div class="card-body">
                <?php if (!empty($success_message)): ?>
                    <div class="alert alert-success">
                        <?php echo $success_message; ?>
                    </div>
                <?php endif; ?>
                
                <!-- Filtri di ricerca -->
                <div class="filtro-riepilogo mb-4">
                    <?php if ($view === 'settimanale'): ?>
                        <div class="row align-items-center">
                            <div class="col-md-4">
                                <label for="filtro_settimana" class="form-label">Seleziona una data della settimana:</label>
                            </div>
                            <div class="col-md-5">
                                <input type="text" class="form-control" id="filtro_settimana" value="<?php echo $data_riferimento; ?>">
                            </div>
                            <div class="col-md-3 text-md-end mt-2 mt-md-0">
                                <?php if (!empty($dati_riepilogo['inizio_settimana']) && !empty($dati_riepilogo['fine_settimana'])): ?>
                                    <span class="text-muted">
                                        <?php echo dataItaliana($dati_riepilogo['inizio_settimana']); ?> - 
                                        <?php echo dataItaliana($dati_riepilogo['fine_settimana']); ?>
                                    </span>
                                <?php endif; ?>
                            </div>
                        </div>
                    <?php else: ?>
                        <form id="form-filtro-mensile">
                            <div class="row align-items-center">
                                <div class="col-md-2">
                                    <label for="filtro_mese" class="form-label">Mese:</label>
                                    <select id="filtro_mese" name="mese" class="form-select">
                                        <?php for ($m = 1; $m <= 12; $m++): ?>
                                            <option value="<?php echo $m; ?>" <?php echo $m == $mese ? 'selected' : ''; ?>>
                                                <?php echo nomeMese($m); ?>
                                            </option>
                                        <?php endfor; ?>
                                    </select>
                                </div>
                                <div class="col-md-2">
                                    <label for="filtro_anno" class="form-label">Anno:</label>
                                    <select id="filtro_anno" name="anno" class="form-select">
                                        <?php for ($a = date('Y') - 5; $a <= date('Y') + 1; $a++): ?>
                                            <option value="<?php echo $a; ?>" <?php echo $a == $anno ? 'selected' : ''; ?>>
                                                <?php echo $a; ?>
                                            </option>
                                        <?php endfor; ?>
                                    </select>
                                </div>
                                <div class="col-md-2 mt-4 mt-md-0">
                                    <button type="submit" class="btn btn-primary">
                                        <i class="fas fa-filter me-1"></i>Filtra
                                    </button>
                                </div>
                            </div>
                        </form>
                    <?php endif; ?>
                </div>
                
                <!-- Tabella riepilogo -->
                <?php if (!empty($dati_riepilogo['registrazioni'])): ?>
                    <div class="table-responsive">
                        <table class="table table-striped table-hover table-riepilogo">
                            <thead>
                                <tr>
                                    <th>Data</th>
                                    <th>Ingresso</th>
                                    <th>Uscita</th>
                                    <th>Tempo APM</th>
                                    <th>Pausa</th>
                                    <th>Totale</th>
                                    <th>Azioni</th>
                                </tr>
                            </thead>
                            <tbody>
                                <?php foreach ($dati_riepilogo['registrazioni'] as $reg): ?>
                                    <tr>
                                        <td><?php echo dataItaliana($reg['data']); ?></td>
                                        <td><?php echo $reg['ingresso']; ?></td>
                                        <td><?php echo $reg['uscita']; ?></td>
                                        <td>
                                            <?php 
                                                echo sprintf("%02d:%02d", $reg['apm_ore'], $reg['apm_minuti']); 
                                            ?>
                                        </td>
                                        <td><?php echo $reg['pausa_minuti']; ?> min</td>
                                        <td>
                                            <strong>
                                                <?php echo formatMinutesToHoursMinutes($reg['totale_minuti']); ?>
                                            </strong>
                                        </td>
                                        <td>
                                            <button class="btn btn-sm btn-danger" onclick="confermaElimina(<?php echo $reg['id']; ?>)">
                                                <i class="fas fa-trash"></i>
                                            </button>
                                        </td>
                                    </tr>
                                <?php endforeach; ?>
                            </tbody>
                            <tfoot>
                                <tr class="totale-riepilogo">
                                    <td colspan="5" class="text-end">Totale <?php echo $view === 'settimanale' ? 'settimanale' : 'mensile'; ?>:</td>
                                    <td colspan="2">
                                        <strong>
                                            <?php echo formatMinutesToHoursMinutes($dati_riepilogo['totale']); ?>
                                        </strong>
                                    </td>
                                </tr>
                            </tfoot>
                        </table>
                    </div>
                <?php else: ?>
                    <div class="alert alert-info">
                        <i class="fas fa-info-circle me-2"></i>
                        Nessuna registrazione trovata per il periodo selezionato.
                    </div>
                <?php endif; ?>
                
                <div class="mt-4">
                    <a href="index.php" class="btn btn-outline-primary">
                        <i class="fas fa-plus-circle me-1"></i>Inserisci nuova registrazione
                    </a>
                </div>
            </div>
        </div>
    </div>
</div>

<?php
// Includi il footer
include 'includes/footer.php';
?>
