import os
import re
import base64
import pyotp
import qrcode
import logging
from io import BytesIO
from datetime import datetime, timedelta
from calendar import monthrange
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

# Configurazione logging per Altervista
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
)


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)

# Creazione dell'app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "qG8mLk9a7nV4Xc2ZtP5uYh3WjQ0Rr6BsDdF1KeLmN")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)  # Necessario per url_for con https

# Configurazione del database
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

# Inizializzazione del db con l'app
db.init_app(app)

# Setup login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Effettua il login per accedere a questa pagina.'

# Modelli
class Utente(UserMixin, db.Model):
    __tablename__ = 'utenti'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(64), nullable=False)
    cognome = db.Column(db.String(64), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    password_chiaro = db.Column(db.String(100), nullable=True)  # Per recupero amministratore
    otp_secret = db.Column(db.String(32), nullable=True)
    otp_enabled = db.Column(db.Boolean, default=False)
    registrazioni = db.relationship('Registrazione', backref='utente', lazy=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        self.password_chiaro = password  # Salva anche in chiaro per il recupero
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def generate_otp_secret(self):
        """Genera un nuovo OTP secret per l'utente"""
        self.otp_secret = pyotp.random_base32()
        return self.otp_secret
    
    def get_totp_uri(self):
        """Ottiene URI per QR code di Google Authenticator"""
        if not self.otp_secret:
            self.generate_otp_secret()
        
        totp = pyotp.TOTP(self.otp_secret)
        return totp.provisioning_uri(
            name=self.email,
            issuer_name="Sistema Tempi APM"
        )
    
    def verify_otp(self, otp_code):
        """Verifica se il codice OTP fornito è valido"""
        if not self.otp_secret:
            return False
        
        totp = pyotp.TOTP(self.otp_secret)
        return totp.verify(otp_code)
    
    def get_qr_code(self):
        """Genera un QR code per l'OTP"""
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(self.get_totp_uri())
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        
        return base64.b64encode(buffer.getvalue()).decode()
    
    def __repr__(self):
        return f'<Utente {self.nome} {self.cognome}>'

@login_manager.user_loader
def load_user(user_id):
    return Utente.query.get(int(user_id))

class Registrazione(db.Model):
    __tablename__ = 'registrazioni'
    
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.Date, nullable=False)
    ingresso = db.Column(db.String(5), nullable=False)
    uscita = db.Column(db.String(5), nullable=False)
    apm_ore = db.Column(db.Integer, nullable=False, default=0)
    apm_minuti = db.Column(db.Integer, nullable=False, default=0)
    pausa_minuti = db.Column(db.Integer, nullable=False, default=30)
    totale_minuti = db.Column(db.Integer, nullable=False, default=0)
    utente_id = db.Column(db.Integer, db.ForeignKey('utenti.id'), nullable=False)
    
    def to_dict(self):
        return {
            'id': self.id,
            'data': self.data.strftime('%Y-%m-%d'),
            'ingresso': self.ingresso,
            'uscita': self.uscita,
            'apm_ore': self.apm_ore,
            'apm_minuti': self.apm_minuti,
            'pausa_minuti': self.pausa_minuti,
            'totale_minuti': self.totale_minuti,
            'utente_id': self.utente_id
        }


# Filtri per i template
@app.template_filter('data_italiana')
def data_italiana(value):
    """Formatta una data in formato italiano (dd/mm/yyyy)"""
    if isinstance(value, str):
        value = datetime.strptime(value, '%Y-%m-%d').date()
    return value.strftime('%d/%m/%Y')

@app.template_filter('format_minutes')
def format_minutes(minutes):
    """Formatta minuti in ore e minuti (HH:MM)"""
    ore = minutes // 60
    minuti = minutes % 60
    return f"{ore:02d}:{minuti:02d}"

@app.template_filter('nome_mese')
def nome_mese(mese):
    """Restituisce il nome del mese in italiano"""
    mesi = [
        'Gennaio', 'Febbraio', 'Marzo', 'Aprile', 'Maggio', 'Giugno', 
        'Luglio', 'Agosto', 'Settembre', 'Ottobre', 'Novembre', 'Dicembre'
    ]
    return mesi[int(mese) - 1]


# Funzioni di utilità
def get_registrazioni_settimanali(data):
    """
    Ottiene le registrazioni per una settimana specifica
    
    Args:
        data: Data di riferimento per la settimana
    
    Returns:
        dict: Registrazioni della settimana e informazioni correlate
    """
    # Calcola il primo giorno della settimana (lunedì)
    if isinstance(data, str):
        data = datetime.strptime(data, '%Y-%m-%d').date()
    
    giorno_settimana = data.weekday()  # 0=Lunedì, 6=Domenica
    inizio_settimana = data - timedelta(days=giorno_settimana)
    fine_settimana = inizio_settimana + timedelta(days=6)
    
    registrazioni = Registrazione.query.filter(
        Registrazione.data.between(inizio_settimana, fine_settimana)
    ).order_by(Registrazione.data).all()
    
    totale_settimanale = sum(reg.totale_minuti for reg in registrazioni)
    
    return {
        'registrazioni': registrazioni,
        'totale': totale_settimanale,
        'inizio_settimana': inizio_settimana,
        'fine_settimana': fine_settimana
    }

def get_registrazioni_mensili(anno, mese):
    """
    Ottiene le registrazioni per un mese specifico
    
    Args:
        anno: Anno di riferimento
        mese: Mese di riferimento (1-12)
    
    Returns:
        dict: Registrazioni del mese e informazioni correlate
    """
    anno = int(anno)
    mese = int(mese)
    
    primo_giorno = datetime(anno, mese, 1).date()
    _, giorni_mese = monthrange(anno, mese)
    ultimo_giorno = datetime(anno, mese, giorni_mese).date()
    
    registrazioni = Registrazione.query.filter(
        Registrazione.data.between(primo_giorno, ultimo_giorno)
    ).order_by(Registrazione.data).all()
    
    totale_mensile = sum(reg.totale_minuti for reg in registrazioni)
    
    return {
        'registrazioni': registrazioni,
        'totale': totale_mensile,
        'primo_giorno': primo_giorno,
        'ultimo_giorno': ultimo_giorno
    }

def valida_form_registrazione(data):
    """
    Valida i dati del form di registrazione
    
    Args:
        data: Dizionario con i dati del form
    
    Returns:
        list: Lista di errori o lista vuota se tutto ok
    """
    errors = []
    
    # Validazione data
    try:
        datetime.strptime(data['data'], '%Y-%m-%d')
    except ValueError:
        errors.append("La data non è valida. Utilizzare il formato YYYY-MM-DD.")
    
    # Validazione orari (formato HH:MM)
    time_pattern = '^([01]?[0-9]|2[0-3]):[0-5][0-9]$'
    if not re.match(time_pattern, data['ingresso']):
        errors.append("L'orario di ingresso non è valido. Utilizzare il formato HH:MM.")
    if not re.match(time_pattern, data['uscita']):
        errors.append("L'orario di uscita non è valido. Utilizzare il formato HH:MM.")
    
    # Validazione numeri
    try:
        apm_ore = int(data['apm_ore'])
        apm_minuti = int(data['apm_minuti'])
        pausa_minuti = int(data['pausa_minuti'])
        totale_minuti = int(data['totale_minuti'])
        
        if apm_ore < 0 or apm_ore > 23:
            errors.append("Le ore APM devono essere tra 0 e 23.")
        if apm_minuti < 0 or apm_minuti > 59:
            errors.append("I minuti APM devono essere tra 0 e 59.")
        if pausa_minuti < 0:
            errors.append("I minuti di pausa non possono essere negativi.")
        if totale_minuti < 0:
            errors.append("Il totale minuti non può essere negativo.")
    except ValueError:
        errors.append("I valori numerici non sono validi.")
    
    return errors

# Inizializzazione del database
with app.app_context():
    db.create_all()
