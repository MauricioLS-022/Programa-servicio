"""
backend/tests/__init__.py - Inicialización del paquete de pruebas.
Configura automáticamente el directorio backend en sys.path para permitir ejecuciones
tanto desde la raíz del workspace como desde el directorio backend/.
"""
import os
import sys

BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

