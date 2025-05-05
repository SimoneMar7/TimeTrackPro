from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from app import Utente

class RegistrationForm(FlaskForm):
    nome = StringField('Nome', validators=[
        DataRequired(message="Il nome è obbligatorio"), 
        Length(min=2, max=64, message="Il nome deve essere compreso tra 2 e 64 caratteri")
    ])
    cognome = StringField('Cognome', validators=[
        DataRequired(message="Il cognome è obbligatorio"), 
        Length(min=2, max=64, message="Il cognome deve essere compreso tra 2 e 64 caratteri")
    ])
    email = StringField('Email', validators=[
        DataRequired(message="L'email è obbligatoria"), 
        Email(message="Inserisci un indirizzo email valido")
    ])
    password = PasswordField('Password', validators=[
        DataRequired(message="La password è obbligatoria"),
        Length(min=6, message="La password deve essere di almeno 6 caratteri")
    ])
    password2 = PasswordField('Conferma Password', validators=[
        DataRequired(message="La conferma password è obbligatoria"),
        EqualTo('password', message="Le password non corrispondono")
    ])
    submit = SubmitField('Registrati')
    
    def validate_email(self, email):
        utente = Utente.query.filter_by(email=email.data).first()
        if utente:
            raise ValidationError('Questo indirizzo email è già registrato. Utilizzane un altro.')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[
        DataRequired(message="L'email è obbligatoria"), 
        Email(message="Inserisci un indirizzo email valido")
    ])
    password = PasswordField('Password', validators=[
        DataRequired(message="La password è obbligatoria")
    ])
    remember = BooleanField('Ricordami')
    submit = SubmitField('Accedi')