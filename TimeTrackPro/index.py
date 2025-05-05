#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Script di avvio per Altervista

Questo script è un punto di ingresso per Altervista,
che reindirizza all'applicazione Flask.
"""

import sys
import os

# Aggiungi la cartella lib al path di Python (per librerie aggiuntive)
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib"))

# Importa l'applicazione Flask
from main import app as application

# Necessario per esecuzione come CGI in alcuni ambienti
if __name__ == "__main__":
    from wsgiref.handlers import CGIHandler
    CGIHandler().run(application)