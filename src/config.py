"""Configuracion central del pipeline: variables de entorno y conexion a la BD."""

import os

from dotenv import load_dotenv
from sqlalchemy import create_engine

# Carga el .env ANTES de leer cualquier variable (mismo principio que en el
# Proyecto 1: require('dotenv').config() como primera linea).
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
OUTPUT_DIR = os.getenv("OUTPUT_DIR", "output")

if not DATABASE_URL:
    # Fallar temprano y con mensaje claro es mejor que un error criptico
    # de conexion mas adelante.
    raise RuntimeError("Falta DATABASE_URL en el archivo .env")

# El engine es el equivalente del Pool de pg en Node: administra las
# conexiones a Postgres y se crea UNA sola vez para todo el pipeline.
engine = create_engine(DATABASE_URL)
