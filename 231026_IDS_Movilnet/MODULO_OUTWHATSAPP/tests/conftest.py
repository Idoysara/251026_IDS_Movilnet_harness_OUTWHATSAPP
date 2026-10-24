"""
Configuración de Fixtures y Rutas para Pytest en MODULO_OUTWHATSAPP.
"""
import os
import sys

MODULE_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if MODULE_ROOT not in sys.path:
    sys.path.append(MODULE_ROOT)

from outwhatsapp.infrastructure.database import init_outwhatsapp_db
init_outwhatsapp_db()
