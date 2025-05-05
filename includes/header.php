<!DOCTYPE html>
<html lang="it">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Form Tempi APM</title>
    
    <!-- Bootstrap CSS con tema Replit -->
    <link href="https://cdn.replit.com/agent/bootstrap-agent-dark-theme.min.css" rel="stylesheet">
    
    <!-- Flatpickr CSS per i date/time picker -->
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/flatpickr/dist/flatpickr.min.css">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/flatpickr/dist/themes/dark.css">
    
    <!-- Font Awesome per le icone -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    
    <!-- CSS personalizzato -->
    <link rel="stylesheet" href="css/styles.css">
</head>
<body>
    <header>
        <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
            <div class="container">
                <a class="navbar-brand" href="index.php">
                    <i class="fas fa-clock me-2"></i>
                    Sistema Tempi APM
                </a>
                <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                    <span class="navbar-toggler-icon"></span>
                </button>
                <div class="collapse navbar-collapse" id="navbarNav">
                    <ul class="navbar-nav ms-auto">
                        <li class="nav-item">
                            <a class="nav-link" href="index.php">
                                <i class="fas fa-plus-circle me-1"></i> Inserimento
                            </a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="riepilogo.php?view=settimanale">
                                <i class="fas fa-calendar-week me-1"></i> Riepilogo Settimanale
                            </a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="riepilogo.php?view=mensile">
                                <i class="fas fa-calendar-alt me-1"></i> Riepilogo Mensile
                            </a>
                        </li>
                    </ul>
                </div>
            </div>
        </nav>
    </header>
    
    <main class="container py-4">
        <!-- Il contenuto principale sarà inserito qui -->
