from flask import render_template, redirect, url_for, flash, request, session, make_response
from flask_login import login_user, logout_user, login_required, current_user
from datetime import datetime, timedelta
from app import app, db, Utente, Registrazione
from forms import RegistrationForm, LoginForm
import re
import io
import pyotp
import qrcode
import base64
import xlsxwriter

# Funzioni di utilità per le date
def get_registrazioni_settimanali(data, utente_id):
    """
    Ottiene le registrazioni di un utente per una settimana specifica
    """
    from app import get_registrazioni_settimanali as get_settimanale
    
    # Ottieni i dati della settimana
    dati = get_settimanale(data)
    
    # Filtra solo le registrazioni dell'utente corrente
    registrazioni_utente = [reg for reg in dati['registrazioni'] if reg.utente_id == utente_id]
    
    # Ricalcola il totale
    totale_settimanale = sum(reg.totale_minuti for reg in registrazioni_utente)
    
    # Sostituisci nell'oggetto dati
    dati['registrazioni'] = registrazioni_utente
    dati['totale'] = totale_settimanale
    
    return dati

def get_registrazioni_mensili(anno, mese, utente_id):
    """
    Ottiene le registrazioni di un utente per un mese specifico
    """
    from app import get_registrazioni_mensili as get_mensile
    
    # Ottieni i dati del mese
    dati = get_mensile(anno, mese)
    
    # Filtra solo le registrazioni dell'utente corrente
    registrazioni_utente = [reg for reg in dati['registrazioni'] if reg.utente_id == utente_id]
    
    # Ricalcola il totale
    totale_mensile = sum(reg.totale_minuti for reg in registrazioni_utente)
    
    # Sostituisci nell'oggetto dati
    dati['registrazioni'] = registrazioni_utente
    dati['totale'] = totale_mensile
    
    return dati

@app.template_filter('nome_mese')
def nome_mese_filter(value):
    """Template filter per mostrare il nome del mese"""
    from app import nome_mese
    return nome_mese(value)

@app.template_filter('data_italiana')
def data_italiana_filter(value):
    """Template filter per mostrare data in formato italiano"""
    from app import data_italiana
    return data_italiana(value)

@app.template_filter('format_minutes')
def format_minutes_filter(value):
    """Template filter per mostrare i minuti in formato HH:MM"""
    from app import format_minutes
    return format_minutes(value)

@app.context_processor
def inject_now():
    """Aggiunge la data attuale ai template"""
    return {'now': datetime.now()}

# Routes per autenticazione
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        remember = 'remember' in request.form
        
        utente = Utente.query.filter_by(email=email).first()
        if utente and utente.check_password(password):
            # Se l'utente ha 2FA attivo, reindirizza alla verifica OTP
            if utente.otp_enabled:
                # Salva i dati dell'utente in sessione per completare il login dopo OTP
                session['user_id'] = utente.id
                session['remember'] = remember
                return redirect(url_for('verify_otp'))
            else:
                # Login diretto senza 2FA
                login_user(utente, remember=remember)
                next_page = request.args.get('next')
                flash('Accesso effettuato con successo!', 'success')
                return redirect(next_page or url_for('index'))
        else:
            flash('Accesso fallito. Controlla email e password.', 'danger')
    
    return render_template('login.html')

@app.route('/verify-otp', methods=['GET', 'POST'])
def verify_otp():
    # Verifica che sia presente un user_id in sessione (fase 1 del login completata)
    if 'user_id' not in session:
        flash('Devi prima effettuare il login.', 'danger')
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        otp_code = request.form.get('otp_code')
        user_id = session['user_id']
        remember = session.get('remember', False)
        
        utente = Utente.query.get(user_id)
        if not utente:
            session.pop('user_id', None)
            session.pop('remember', None)
            flash('Utente non trovato. Riprova.', 'danger')
            return redirect(url_for('login'))
        
        # Verifica il codice OTP
        if utente.verify_otp(otp_code):
            # Login completato con successo
            login_user(utente, remember=remember)
            session.pop('user_id', None)
            session.pop('remember', None)
            
            next_page = session.pop('next', None)
            flash('Accesso completato con successo!', 'success')
            return redirect(next_page or url_for('index'))
        else:
            flash('Codice di verifica non valido. Riprova.', 'danger')
    
    return render_template('verify_otp.html')

@app.route('/cancel-login', methods=['POST'])
def cancel_login():
    # Cancella i dati di login temporanei
    session.pop('user_id', None)
    session.pop('remember', None)
    flash('Login annullato.', 'info')
    return redirect(url_for('login'))

@app.route('/logout')
def logout():
    logout_user()
    flash('Hai effettuato il logout con successo.', 'success')
    return redirect(url_for('login'))

@app.route('/registrazione', methods=['GET', 'POST'])
def registrazione():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        nome = request.form.get('nome')
        cognome = request.form.get('cognome')
        email = request.form.get('email')
        password = request.form.get('password')
        password2 = request.form.get('password2')
        
        # Validazione base
        error = None
        if not nome or not cognome or not email or not password or not password2:
            error = 'Tutti i campi sono obbligatori.'
        elif password != password2:
            error = 'Le password non corrispondono.'
        elif len(password) < 6:
            error = 'La password deve essere di almeno 6 caratteri.'
        elif Utente.query.filter_by(email=email).first():
            error = 'Questo indirizzo email è già registrato. Utilizzane un altro.'
        
        if error:
            flash(error, 'danger')
        else:
            # Crea nuovo utente
            utente = Utente(
                nome=nome,
                cognome=cognome,
                email=email
            )
            utente.set_password(password)
            
            db.session.add(utente)
            db.session.commit()
            
            flash('Registrazione completata con successo! Ora puoi accedere.', 'success')
            return redirect(url_for('login'))
    
    return render_template('registrazione.html')

@app.route('/configure-otp', methods=['GET', 'POST'])
@login_required
def configure_otp():
    if request.method == 'POST':
        otp_code = request.form.get('otp_code')
        
        # Verifica che il codice OTP sia valido
        if current_user.verify_otp(otp_code):
            # Attiva 2FA per l'utente
            current_user.otp_enabled = True
            db.session.commit()
            
            flash('Autenticazione a due fattori attivata con successo!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Codice di verifica non valido. Riprova.', 'danger')
    
    # Genera OTP secret se non esiste già
    if not current_user.otp_secret:
        current_user.generate_otp_secret()
        db.session.commit()
    
    # Genera QR code per l'app
    qr_code = current_user.get_qr_code()
    
    return render_template('configure_otp.html', qr_code=qr_code)

@app.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    """Pagina per modificare la password dell'utente"""
    if request.method == 'POST':
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        # Validazione
        if not current_password or not new_password or not confirm_password:
            flash('Tutti i campi sono obbligatori.', 'danger')
        elif not current_user.check_password(current_password):
            flash('La password attuale non è corretta.', 'danger')
        elif new_password != confirm_password:
            flash('Le nuove password non corrispondono.', 'danger')
        elif len(new_password) < 6:
            flash('La nuova password deve essere di almeno 6 caratteri.', 'danger')
        else:
            # Aggiorna la password
            current_user.set_password(new_password)
            db.session.commit()
            
            flash('Password aggiornata con successo!', 'success')
            return redirect(url_for('index'))
    
    return render_template('change_password.html')

@app.route('/disable-otp', methods=['POST'])
@login_required
def disable_otp():
    password = request.form.get('password')
    
    # Verifica la password dell'utente
    if current_user.check_password(password):
        current_user.otp_enabled = False
        db.session.commit()
        flash('Autenticazione a due fattori disattivata con successo.', 'success')
    else:
        flash('Password non corretta.', 'danger')
    
    return redirect(url_for('configure_otp'))

# Routes per amministrazione
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    """Pagina di login amministratore"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Credenziali codificate come richiesto
        if username == 'sysadm' and password == '.!sysadm!.@':
            # Salva temporaneamente le credenziali admin per la verifica 2FA
            session['admin_login_pending'] = True
            session['admin_user'] = username
            # Verifica se esiste già un segreto OTP per l'admin
            admin_otp_secret = app.config.get('ADMIN_OTP_SECRET')
            
            # Se non esiste, lo crea e lo memorizza
            if not admin_otp_secret:
                admin_otp_secret = pyotp.random_base32()
                app.config['ADMIN_OTP_SECRET'] = admin_otp_secret
                flash('Un nuovo codice 2FA è stato generato per l\'amministratore. Scansionalo con Google Authenticator.', 'warning')
                return redirect(url_for('admin_setup_otp'))
            
            # Reindirizza alla pagina di verifica 2FA per admin
            return redirect(url_for('admin_verify_otp'))
        else:
            flash('Credenziali amministratore non valide.', 'danger')
    
    return render_template('admin_login.html')

@app.route('/admin/setup-otp')
def admin_setup_otp():
    """Configurazione OTP per l'amministratore"""
    # Verifica che ci sia un accesso admin in corso
    if not session.get('admin_login_pending'):
        flash('Accesso negato.', 'danger')
        return redirect(url_for('admin_login'))
    
    admin_otp_secret = app.config.get('ADMIN_OTP_SECRET')
    if not admin_otp_secret:
        flash('Errore nella configurazione 2FA.', 'danger')
        return redirect(url_for('admin_login'))
    
    # Crea URL per QR code
    totp_uri = pyotp.totp.TOTP(admin_otp_secret).provisioning_uri(
        "admin@tempi-apm.it", issuer_name="Tempi APM Admin"
    )
    
    # Genera QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(totp_uri)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    buffered = io.BytesIO()
    img.save(buffered)
    img_str = base64.b64encode(buffered.getvalue()).decode()
    
    return render_template('admin_setup_otp.html', qr_code=img_str, secret=admin_otp_secret)

@app.route('/admin/verify-otp', methods=['GET', 'POST'])
def admin_verify_otp():
    """Verifica OTP per admin"""
    # Verifica che ci sia un accesso admin in corso
    if not session.get('admin_login_pending'):
        flash('Accesso negato.', 'danger')
        return redirect(url_for('admin_login'))
    
    if request.method == 'POST':
        # Ottieni il codice inserito dall'utente
        otp_code = request.form.get('otp_code', '')
        
        # Verifica il codice OTP
        admin_otp_secret = app.config.get('ADMIN_OTP_SECRET')
        if not admin_otp_secret:
            flash('Errore nella configurazione 2FA.', 'danger')
            return redirect(url_for('admin_login'))
        
        totp = pyotp.TOTP(admin_otp_secret)
        if totp.verify(otp_code):
            # Autenticazione completata con successo
            session.pop('admin_login_pending', None)
            session['admin_logged_in'] = True
            flash('Accesso amministratore completato con successo!', 'success')
            return redirect(url_for('admin_panel'))
        else:
            flash('Codice OTP non valido. Riprova.', 'danger')
    
    return render_template('admin_verify_otp.html')

@app.route('/admin/panel')
def admin_panel():
    """Pannello amministratore"""
    # Verifica che l'utente sia autenticato come admin
    if not session.get('admin_logged_in'):
        flash('Accesso riservato agli amministratori.', 'danger')
        return redirect(url_for('admin_login'))
    
    # Ottieni tutti gli utenti
    utenti = Utente.query.all()
    
    return render_template('admin.html', utenti=utenti)

@app.route('/admin/reset-password', methods=['POST'])
def admin_reset_password():
    """Resetta la password di un utente"""
    # Verifica che l'utente sia autenticato come admin
    if not session.get('admin_logged_in'):
        flash('Accesso riservato agli amministratori.', 'danger')
        return redirect(url_for('admin_login'))
    
    user_id = request.form.get('user_id')
    
    try:
        user_id = int(user_id)
        utente = Utente.query.get(user_id)
        
        if utente:
            # Imposta la password di default
            default_password = '12345678a'
            utente.set_password(default_password)
            db.session.commit()
            flash(f'Password di {utente.nome} {utente.cognome} resettata a: {default_password}', 'success')
        else:
            flash('Utente non trovato.', 'danger')
    except:
        flash('ID utente non valido.', 'danger')
    
    return redirect(url_for('admin_panel'))

@app.route('/admin/delete-user', methods=['POST'])
def admin_delete_user():
    """Elimina un utente e tutti i suoi dati"""
    # Verifica che l'utente sia autenticato come admin
    if not session.get('admin_logged_in'):
        flash('Accesso riservato agli amministratori.', 'danger')
        return redirect(url_for('admin_login'))
    
    user_id = request.form.get('user_id')
    
    try:
        user_id = int(user_id)
        utente = Utente.query.get(user_id)
        
        if utente:
            # Elimina tutte le registrazioni dell'utente
            Registrazione.query.filter_by(utente_id=utente.id).delete()
            
            # Elimina l'utente
            db.session.delete(utente)
            db.session.commit()
            
            flash(f'Utente {utente.nome} {utente.cognome} e tutti i suoi dati eliminati con successo!', 'success')
        else:
            flash('Utente non trovato.', 'danger')
    except Exception as e:
        flash(f'Errore durante l\'eliminazione dell\'utente: {str(e)}', 'danger')
    
    return redirect(url_for('admin_panel'))

# Routes principali dell'applicazione
@app.route('/')
@login_required
def index():
    """Pagina principale con form di inserimento"""
    return render_template('index.html')

@app.route('/process', methods=['POST'])
@login_required
def process():
    """Processa i dati del form"""
    action = request.form.get('action')
    
    if action == 'salva':
        # Raccogli i dati dal form
        data = {
            'data': request.form.get('data', ''),
            'ingresso': request.form.get('ingresso', ''),
            'uscita': request.form.get('uscita', ''),
            'ore_totali': request.form.get('ore_totali', 0),
            'apm_ore': request.form.get('apm_ore', 0),
            'apm_minuti': request.form.get('apm_minuti', 0),
            'pausa_minuti': request.form.get('pausa_minuti', 0),
            'totale_apm': request.form.get('totale_apm', 0),
            'totale_minuti': request.form.get('totale_minuti', 0)
        }
        
        # Validazione
        from app import valida_form_registrazione
        errors = valida_form_registrazione(data)
        
        if not errors:
            # Conversione dei dati
            try:
                data_obj = datetime.strptime(data['data'], '%Y-%m-%d').date()
                apm_ore = int(data['apm_ore'])
                apm_minuti = int(data['apm_minuti'])
                pausa_minuti = int(data['pausa_minuti'])
                totale_minuti = int(data['totale_minuti'])
                
                # Crea una nuova registrazione
                registrazione = Registrazione(
                    data=data_obj,
                    ingresso=data['ingresso'],
                    uscita=data['uscita'],
                    apm_ore=apm_ore,
                    apm_minuti=apm_minuti,
                    pausa_minuti=pausa_minuti,
                    totale_minuti=totale_minuti,
                    utente_id=current_user.id
                )
                
                db.session.add(registrazione)
                db.session.commit()
                
                flash('Registrazione salvata con successo!', 'success')
            except Exception as e:
                flash(f'Errore nel salvataggio della registrazione: {str(e)}', 'danger')
        else:
            for error in errors:
                flash(error, 'danger')
    
    elif action == 'elimina':
        id_registrazione = request.form.get('id')
        
        try:
            id_registrazione = int(id_registrazione)
            registrazione = Registrazione.query.filter_by(id=id_registrazione, utente_id=current_user.id).first()
            
            if registrazione:
                db.session.delete(registrazione)
                db.session.commit()
                flash('Registrazione eliminata con successo!', 'success')
            else:
                flash('Registrazione non trovata o non autorizzata.', 'danger')
        except:
            flash('ID registrazione non valido.', 'danger')
    
    # Redirect alla pagina principale
    return redirect(url_for('index'))

@app.route('/riepilogo')
@login_required
def riepilogo():
    """Pagina di riepilogo settimanale o mensile"""
    view = request.args.get('view', 'settimanale')
    
    if view == 'settimanale':
        # Riepilogo settimanale
        data_riferimento = request.args.get('data', datetime.now().strftime('%Y-%m-%d'))
        dati_settimana = get_registrazioni_settimanali(data_riferimento, current_user.id)
        
        return render_template(
            'riepilogo.html',
            view='settimanale',
            registrazioni=dati_settimana['registrazioni'],
            totale=dati_settimana['totale'],
            data_riferimento=data_riferimento,
            inizio_settimana=dati_settimana['inizio_settimana'],
            fine_settimana=dati_settimana['fine_settimana'],
            day_delta=timedelta(days=7), # Per la navigazione tra settimane
            user=current_user
        )
    else:
        # Riepilogo mensile
        today = datetime.now()
        anno = int(request.args.get('anno', today.year))
        mese = int(request.args.get('mese', today.month))
        
        dati_mese = get_registrazioni_mensili(anno, mese, current_user.id)
        
        return render_template(
            'riepilogo.html',
            view='mensile',
            registrazioni=dati_mese['registrazioni'],
            totale=dati_mese['totale'],
            anno=anno,
            mese=mese,
            nome_mese=nome_mese_filter(mese),
            anno_corrente=today.year,
            user=current_user
        )

@app.route('/export/excel')
@login_required
def export_excel():
    """Esporta i dati in formato Excel"""
    view = request.args.get('view', 'settimanale')
    
    # Ottieni i dati in base alla vista
    if view == 'settimanale':
        data_riferimento = request.args.get('data', datetime.now().strftime('%Y-%m-%d'))
        dati = get_registrazioni_settimanali(data_riferimento, current_user.id)
        periodo = f"Settimana: {data_italiana_filter(dati['inizio_settimana'])} - {data_italiana_filter(dati['fine_settimana'])}"
        filename = f"tempi_apm_{current_user.cognome}_{current_user.nome}_settimana_{dati['inizio_settimana'].strftime('%d_%m_%Y')}.xlsx"
    else:
        anno = int(request.args.get('anno', datetime.now().year))
        mese = int(request.args.get('mese', datetime.now().month))
        dati = get_registrazioni_mensili(anno, mese, current_user.id)
        periodo = f"Mese: {nome_mese_filter(mese)} {anno}"
        filename = f"tempi_apm_{current_user.cognome}_{current_user.nome}_mese_{mese}_{anno}.xlsx"
    
    # Crea un file Excel in memoria
    output = io.BytesIO()
    workbook = xlsxwriter.Workbook(output)
    worksheet = workbook.add_worksheet('Riepilogo Tempi')

    # Definisci stili
    titolo_formato = workbook.add_format({
        'bold': True,
        'font_size': 16,
        'align': 'center',
        'valign': 'vcenter'
    })
    
    sottotitolo_formato = workbook.add_format({
        'font_size': 12,
        'align': 'left',
        'valign': 'vcenter'
    })
    
    intestazione_formato = workbook.add_format({
        'bold': True,
        'font_size': 10,
        'align': 'center',
        'valign': 'vcenter',
        'bg_color': '#ADD8E6',  # Azzurro chiaro
        'border': 1
    })
    
    dati_formato = workbook.add_format({
        'font_size': 10,
        'align': 'center',
        'valign': 'vcenter',
        'border': 1
    })
    
    dati_sinistra_formato = workbook.add_format({
        'font_size': 10,
        'align': 'left',
        'valign': 'vcenter',
        'border': 1
    })
    
    totale_formato = workbook.add_format({
        'bold': True,
        'font_size': 10,
        'align': 'center',
        'valign': 'vcenter',
        'bg_color': '#E0E0E0',  # Grigio chiaro
        'border': 1
    })
    
    # Imposta larghezza colonne
    worksheet.set_column('A:A', 15)  # Data
    worksheet.set_column('B:H', 12)  # Altre colonne
    
    # Intestazione del documento
    worksheet.merge_range('A1:H1', 'Riepilogo Tempi APM', titolo_formato)
    worksheet.write('A2', f'Nome: {current_user.nome} {current_user.cognome}', sottotitolo_formato)
    worksheet.write('A3', periodo, sottotitolo_formato)
    
    # Intestazione tabella
    headers = ['Data', 'Ingresso', 'Uscita', 'APM', 'Pausa', 'Totale APM', 'Totale Ore', '']
    for col, header in enumerate(headers):
        worksheet.write(4, col, header, intestazione_formato)
    
    # Dati
    row = 5
    for reg in dati['registrazioni']:
        # Calcola totale APM in ore
        totale_apm_ore = (reg.apm_ore * 60 + reg.apm_minuti + reg.pausa_minuti) / 60
        
        # Calcola totale ore (differenza ingresso-uscita)
        ingresso = reg.ingresso.split(':')
        uscita = reg.uscita.split(':')
        ingresso_ore = int(ingresso[0])
        ingresso_minuti = int(ingresso[1])
        uscita_ore = int(uscita[0])
        uscita_minuti = int(uscita[1])
        
        # Calcola la differenza corretta
        diff_ore = uscita_ore - ingresso_ore
        diff_minuti = uscita_minuti - ingresso_minuti
        
        if diff_minuti < 0:
            diff_minuti += 60
            diff_ore -= 1
        
        if diff_ore < 0:
            diff_ore += 24
            
        totale_ore = diff_ore + (diff_minuti / 60)
        
        worksheet.write(row, 0, data_italiana_filter(reg.data), dati_sinistra_formato)
        worksheet.write(row, 1, reg.ingresso, dati_formato)
        worksheet.write(row, 2, reg.uscita, dati_formato)
        worksheet.write(row, 3, f"{reg.apm_ore}:{reg.apm_minuti:02d}", dati_formato)
        worksheet.write(row, 4, f"{reg.pausa_minuti} min", dati_formato)
        worksheet.write(row, 5, f"{totale_apm_ore:.2f} ore", dati_formato)
        worksheet.write(row, 6, f"{totale_ore:.2f} ore", dati_formato)
        row += 1
    
    # Totale finale
    worksheet.merge_range(f'A{row+1}:E{row+1}', 'TOTALE:', totale_formato)
    worksheet.write(row, 5, f"{(dati['totale'] / 60):.2f} ore", totale_formato)
    worksheet.write(row, 6, '', totale_formato)
    
    # Chiudi il workbook
    workbook.close()
    
    # Crea la risposta
    output.seek(0)
    response = make_response(output.getvalue())
    response.headers['Content-Disposition'] = f'attachment; filename={filename}'
    response.headers['Content-type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    
    return response

