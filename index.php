<?php
// Includi file di configurazione e funzioni
require_once 'includes/db_connect.php';
require_once 'includes/functions.php';

// Inizializza variabili
$errors = [];
$success_message = '';

// Controlla se ci sono messaggi di successo in sessione
session_start();
if (isset($_SESSION['success_message'])) {
    $success_message = $_SESSION['success_message'];
    unset($_SESSION['success_message']);
}

// Includi l'header
include 'includes/header.php';
?>

<div class="row">
    <div class="col-md-8 mx-auto">
        <div class="card">
            <div class="card-header bg-primary text-white">
                <h2 class="h4 mb-0">
                    <i class="fas fa-clock me-2"></i>Inserimento Tempo Giornaliero
                </h2>
            </div>
            <div class="card-body">
                <?php if (!empty($success_message)): ?>
                    <div class="alert alert-success">
                        <?php echo $success_message; ?>
                    </div>
                <?php endif; ?>
                
                <?php if (!empty($errors)): ?>
                    <div class="alert alert-danger">
                        <ul class="mb-0">
                            <?php foreach ($errors as $error): ?>
                                <li><?php echo $error; ?></li>
                            <?php endforeach; ?>
                        </ul>
                    </div>
                <?php endif; ?>

                <form action="process.php" method="post" id="form-registrazione">
                    <input type="hidden" name="action" value="salva">
                    
                    <div class="row mb-3">
                        <div class="col-md-4">
                            <label for="data" class="form-label">Data</label>
                            <input type="text" class="form-control" id="data" name="data" required>
                        </div>
                    </div>
                    
                    <div class="row mb-3">
                        <div class="col-md-4">
                            <label for="ingresso" class="form-label">Orario Ingresso</label>
                            <input type="text" class="form-control" id="ingresso" name="ingresso" required>
                        </div>
                        <div class="col-md-4">
                            <label for="uscita" class="form-label">Orario Uscita</label>
                            <input type="text" class="form-control" id="uscita" name="uscita" required>
                        </div>
                    </div>
                    
                    <hr class="my-4">
                    
                    <div class="row mb-3">
                        <div class="col-md-6">
                            <label class="form-label">Tempo APM</label>
                            <div class="row">
                                <div class="col-6">
                                    <div class="input-group">
                                        <input type="number" class="form-control" id="apm_ore" name="apm_ore" min="0" max="23" value="0" required>
                                        <span class="input-group-text">ore</span>
                                    </div>
                                </div>
                                <div class="col-6">
                                    <div class="input-group">
                                        <input type="number" class="form-control" id="apm_minuti" name="apm_minuti" min="0" max="59" value="0" required>
                                        <span class="input-group-text">min</span>
                                    </div>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-6">
                            <label for="pausa_minuti" class="form-label">Pausa (minuti)</label>
                            <select class="form-select" id="pausa_minuti" name="pausa_minuti" required>
                                <option value="15">15 minuti</option>
                                <option value="30" selected>30 minuti</option>
                                <option value="45">45 minuti</option>
                            </select>
                        </div>
                    </div>

                    <div class="text-center">
                        <button type="button" class="btn btn-primary btn-calcola" id="btn-calcola">
                            <i class="fas fa-calculator me-2"></i>Calcola
                        </button>
                    </div>
                    
                    <div id="totale-calcolato" class="totale-calcolato text-center mt-3 d-none">
                        <div class="mb-2">Totale tempo calcolato:</div>
                        <div class="bg-light p-2 rounded">
                            <span id="totale-visualizzato" class="h3">00:00</span>
                        </div>
                        <input type="hidden" id="totale_minuti" name="totale_minuti" value="0">
                    </div>
                    
                    <div class="d-grid gap-2 col-md-6 mx-auto mt-4">
                        <button type="submit" class="btn btn-success">
                            <i class="fas fa-save me-2"></i>Salva Registrazione
                        </button>
                    </div>
                </form>
            </div>
        </div>
    </div>
</div>

<?php
// Includi il footer
include 'includes/footer.php';
?>
