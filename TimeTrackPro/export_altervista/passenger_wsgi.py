import sys
import os

# Aggiungi la cartella lib al path di Python (per librerie aggiuntive)
INTERP = os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib")
if os.path.isdir(INTERP):
    sys.path.insert(0, INTERP)

# Importa l'applicazione Flask
from main import app as application