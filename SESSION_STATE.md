# ESTADO DEL PROYECTO — PORTAFOLIO MARCELO
Última actualización: 2026-07-15
IA que trabajó esta sesión: Claude

## Proyecto activo
Nombre: Proyecto 2 — Pipeline de Datos (ETL) de Mantenimiento Industrial
Repositorio: (pendiente — Marcelo debe crear el repo vacío en GitHub y pasar la URL)
Rama activa: develop

## Contexto del portafolio
- El Proyecto 1 (API REST Node.js + Express + PostgreSQL) está TERMINADO y mergeado a
  main: https://github.com/marjsoto/api-mantenimiento-industrial
- Este Proyecto 2 usa LA MISMA base de datos del Proyecto 1 como FUENTE: el contenedor
  Docker `maintenance_db` (postgres:16-alpine, localhost:5432). Para trabajar, ese
  contenedor debe estar corriendo (`docker compose up -d` en la carpeta del Proyecto 1).
- La base ya tiene datos de prueba: 2 equipos, 3 técnicos, órdenes correctivas y
  preventivas, 1 plan de mantenimiento, 1 repuesto con movimientos de stock.

## Último paso completado
Scaffolding inicial: carpeta, git init (rama develop), PROMPT_MAESTRO.md copiado,
README.md, .gitignore (incluye .venv y output/), .env.example. Nada de código todavía.

## Decisiones tomadas en esta sesión
- Stack de conexión: SQLAlchemy + psycopg (v3) para extraer con `pd.read_sql`, en vez
  de psycopg2 crudo — es el camino recomendado por Pandas y lo que más se ve en
  ofertas de Data Engineer Jr.
- Las salidas del pipeline van a `output/` (ignorada por git — se regeneran al correr).
- El pipeline se estructura como módulos separados extract/transform/load para enseñar
  el patrón ETL de forma explícita (es un proyecto de aprendizaje/portafolio).

## Stack actual del proyecto
- Lenguaje: Python 3.12 (verificado en la máquina de Marcelo)
- Entorno: venv (pendiente de crear)
- Librerías previstas: pandas, sqlalchemy, psycopg[binary], python-dotenv, openpyxl
  (para exportar Excel)
- Fuente de datos: PostgreSQL del Proyecto 1

## Estructura de archivos actual
```
02-pipeline-datos-mantenimiento/
├── .git/
├── .gitignore
├── .env.example
├── PROMPT_MAESTRO.md
├── README.md
└── SESSION_STATE.md
```

## Próximo paso
1. Marcelo crea el repo vacío en GitHub (sin README/gitignore/licencia) y pasa la URL.
2. Explicarle a Marcelo qué es un entorno virtual (venv) y POR QUÉ se usa en Python
   (aislamiento de dependencias por proyecto) — concepto nuevo para él.
3. Crear venv, requirements.txt, instalar dependencias.
4. Módulo extract: conectar a Postgres con SQLAlchemy y traer las tablas a DataFrames
   de Pandas (explicar qué es un DataFrame — primer contacto de Marcelo con Pandas).
5. Metodología igual que el Proyecto 1: un paso → una prueba → siguiente. Ejercicios
   guiados para Marcelo en las partes clave.

## Pendientes / deuda técnica detectada
- Ninguna todavía (proyecto recién iniciado).
- Heredada del Proyecto 1 (no bloquea): tests automatizados Jest + supertest.

## Variables de entorno necesarias (.env.example)
```
DATABASE_URL=postgresql+psycopg://maintenance_user:changeme@localhost:5432/maintenance_db
OUTPUT_DIR=output
```

## Comandos para levantar el proyecto localmente
```
# 1. Levantar la fuente de datos (desde la carpeta del Proyecto 1):
docker compose up -d
# 2. En esta carpeta:
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt   # (cuando exista)
python src/pipeline.py            # (cuando exista)
```

## Notas para la próxima IA
- Marcelo es Ing. Mecatrónico retomando programación: explicar conceptos nuevos desde
  cero ANTES de escribir código (así se trabajó todo el Proyecto 1 y funcionó muy bien).
- Conceptos que ya domina (validados en ronda de entrevista): PK/FK, CRUD, códigos
  HTTP, JWT, inyección SQL/queries parametrizadas, hash vs encriptación, transacciones.
- Conceptos NUEVOS para él en este proyecto: venv, pip/requirements.txt, DataFrames,
  el patrón ETL. Ir despacio ahí.
- Su punto débil a reforzar: precisión terminológica (las ideas las capta rápido).
