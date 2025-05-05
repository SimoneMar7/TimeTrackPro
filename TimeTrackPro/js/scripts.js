/**
 * Scripts per l'applicazione Tempi APM
 */

document.addEventListener('DOMContentLoaded', function() {
    // Inizializzazione date picker
    initializeDatePickers();
    
    // Inizializzazione del calcolo automatico
    initializeCalcolo();
    
    // Inizializzazione dei selettori dei riepiloghi
    initializeSelettoriRiepilogo();
});

/**
 * Inizializza tutti i date/time picker
 */
function initializeDatePickers() {
    // Date picker per la data
    if (document.getElementById('data')) {
        flatpickr("#data", {
            dateFormat: "Y-m-d",
            locale: "it",
            altInput: true,
            altFormat: "d/m/Y",
            defaultDate: new Date()
        });
    }
    
    // Time picker per orario di ingresso
    if (document.getElementById('ingresso')) {
        flatpickr("#ingresso", {
            enableTime: true,
            noCalendar: true,
            dateFormat: "H:i",
            time_24hr: true,
            locale: "it",
            defaultHour: 9,
            defaultMinute: 0
        });
    }
    
    // Time picker per orario di uscita
    if (document.getElementById('uscita')) {
        flatpickr("#uscita", {
            enableTime: true,
            noCalendar: true,
            dateFormat: "H:i",
            time_24hr: true,
            locale: "it",
            defaultHour: 18,
            defaultMinute: 0
        });
    }
    
    // Data picker per filtro settimanale
    if (document.getElementById('filtro_settimana')) {
        flatpickr("#filtro_settimana", {
            dateFormat: "Y-m-d",
            locale: "it",
            altInput: true,
            altFormat: "d/m/Y",
            defaultDate: new Date()
        });
    }
    
    // Selettori per filtro mensile
    if (document.getElementById('filtro_mese') && document.getElementById('filtro_anno')) {
        // Mese corrente come default
        const oggi = new Date();
        const meseCorrente = oggi.getMonth() + 1; // JavaScript usa 0-11 per i mesi
        const annoCorrente = oggi.getFullYear();
        
        if (document.getElementById('filtro_mese').value === '') {
            document.getElementById('filtro_mese').value = meseCorrente;
        }
        
        if (document.getElementById('filtro_anno').value === '') {
            document.getElementById('filtro_anno').value = annoCorrente;
        }
    }
}

/**
 * Inizializza il calcolo automatico del totale
 */
function initializeCalcolo() {
    const btnCalcola = document.getElementById('btn-calcola');
    if (btnCalcola) {
        btnCalcola.addEventListener('click', calcolaTotale);
        
        // Inizializziamo anche con un calcolo automatico all'avvio
        calcolaTotale();
        
        // Aggiungiamo listener per il calcolo automatico quando i campi cambiano
        document.getElementById('apm_ore').addEventListener('change', calcolaTotale);
        document.getElementById('apm_minuti').addEventListener('change', calcolaTotale);
        document.getElementById('pausa_minuti').addEventListener('change', calcolaTotale);
    }
}

/**
 * Calcola il totale dei minuti in base a APM e pausa
 */
function calcolaTotale() {
    const apmOre = parseInt(document.getElementById('apm_ore').value) || 0;
    const apmMinuti = parseInt(document.getElementById('apm_minuti').value) || 0;
    const pausaMinuti = parseInt(document.getElementById('pausa_minuti').value) || 0;
    
    // Validazione dei campi
    if (apmOre < 0 || apmOre > 23) {
        alert("Le ore APM devono essere tra 0 e 23");
        document.getElementById('apm_ore').value = 0;
        return;
    }
    
    if (apmMinuti < 0 || apmMinuti > 59) {
        alert("I minuti APM devono essere tra 0 e 59");
        document.getElementById('apm_minuti').value = 0;
        return;
    }
    
    // Calcolo del totale in minuti
    const totaleMinuti = apmOre * 60 + apmMinuti + pausaMinuti;
    
    // Converti in formato ore:minuti
    const ore = Math.floor(totaleMinuti / 60);
    const minuti = totaleMinuti % 60;
    const totaleFormattato = `${ore.toString().padStart(2, '0')}:${minuti.toString().padStart(2, '0')}`;
    
    // Aggiorna il campo totale e il testo visibile
    document.getElementById('totale_minuti').value = totaleMinuti;
    document.getElementById('totale-visualizzato').textContent = totaleFormattato;
    
    // Aggiorna la UI per mostrare il risultato
    const totaleElement = document.getElementById('totale-calcolato');
    if (totaleElement) {
        totaleElement.classList.remove('d-none');
    }
}

/**
 * Inizializza i selettori dei riepiloghi
 */
function initializeSelettoriRiepilogo() {
    // Filtro settimanale
    const filtroSettimana = document.getElementById('filtro_settimana');
    if (filtroSettimana) {
        filtroSettimana.addEventListener('change', function() {
            const url = new URL(window.location.href);
            url.searchParams.set('view', 'settimanale');
            url.searchParams.set('data', this.value);
            window.location.href = url.toString();
        });
    }
    
    // Filtro mensile
    const formFiltroMensile = document.getElementById('form-filtro-mensile');
    if (formFiltroMensile) {
        formFiltroMensile.addEventListener('submit', function(e) {
            e.preventDefault();
            const mese = document.getElementById('filtro_mese').value;
            const anno = document.getElementById('filtro_anno').value;
            
            const url = new URL(window.location.href);
            url.searchParams.set('view', 'mensile');
            url.searchParams.set('mese', mese);
            url.searchParams.set('anno', anno);
            window.location.href = url.toString();
        });
    }
}

/**
 * Conferma prima di eliminare una registrazione
 */
function confermaElimina(id) {
    if (confirm('Sei sicuro di voler eliminare questa registrazione?')) {
        window.location.href = 'process.php?action=elimina&id=' + id;
    }
}
