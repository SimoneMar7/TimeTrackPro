#!/bin/bash
# Script per installare le dipendenze Python nella cartella lib
# Da eseguire nel tuo spazio Altervista tramite SSH

# Crea directory lib se non esiste
mkdir -p lib

# Installa le dipendenze nella cartella lib
pip install -t ./lib -r requirements.txt

echo "Installazione completata!"