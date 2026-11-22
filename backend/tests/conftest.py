"""Configuración de pruebas offline.

Define las variables de entorno antes de importar la aplicación para que
config.py no dependa de un archivo .env ni de una base de datos real.
"""

import os

os.environ.setdefault(
    "DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5432/postgres",
)
os.environ.setdefault(
    "JWT_SECRET",
    "secreto_de_pruebas_con_mas_de_32_caracteres_123456",
)
os.environ.setdefault("JWT_EXPIRACION_MINUTOS", "60")
os.environ.setdefault("CORS_ORIGINS", "http://localhost:4200")
