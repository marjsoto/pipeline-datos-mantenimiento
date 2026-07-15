# ESTADO DEL PROYECTO — PORTAFOLIO MARCELO
Última actualización: 2026-07-15
IA que trabajó esta sesión: Claude

## Proyecto activo
Nombre: Proyecto 2 — Pipeline de Datos (ETL) de Mantenimiento Industrial
Repositorio: https://github.com/marjsoto/pipeline-datos-mantenimiento
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
- Scaffolding inicial: carpeta, git init (main + develop), PROMPT_MAESTRO.md, README.md,
  .gitignore (incluye .venv y output/), .env.example. Repo conectado y pusheado a
  https://github.com/marjsoto/pipeline-datos-mantenimiento
- Se explicó a Marcelo qué es un entorno virtual (analogía con node_modules y Docker)
  y qué es un DataFrame (analogía con tabla SQL: WHERE→filtro, GROUP BY→groupby,
  JOIN→merge).
- venv creado, requirements.txt instalado y verificado (pandas 2.3.3, sqlalchemy 2.0.44,
  psycopg 3.2.13, python-dotenv, openpyxl).
- ETAPA EXTRACT COMPLETA Y PROBADA (`src/config.py` + `src/extract.py`): 4 funciones
  que devuelven DataFrames (ordenes con JOIN a equipos/tecnicos, equipos, repuestos,
  uso_repuestos). Cada etapa tiene mini-prueba integrada via `if __name__ == "__main__"`.
  Probado contra la base real: trae incluso datos que Marcelo creó él mismo desde el
  panel del Proyecto 1 (equipo MOTORREDUCTOR-01, orden 6, repuesto REP-02).

## Pregunta pendiente para Marcelo (calentamiento de la próxima sesión)
En extraer_ordenes() se usa LEFT JOIN tecnicos: ¿por qué la orden 5 (tecnico_id NULL)
sí aparece en el resultado, y qué pasaría con un JOIN normal? (Respuesta esperada: el
LEFT JOIN conserva todas las filas de la izquierda rellenando con NULL las que no
matchean; un JOIN interno habría OCULTADO la orden 5 — las órdenes sin técnico
asignado desaparecerían del análisis.)

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
├── .venv/            (no versionado)
├── requirements.txt
├── src/
│   ├── config.py     (dotenv + engine de SQLAlchemy)
│   └── extract.py    (etapa E del ETL, con mini-prueba integrada)
├── PROMPT_MAESTRO.md
├── README.md
└── SESSION_STATE.md
```

## Próximo paso
1. Retomar la pregunta pendiente del LEFT JOIN (arriba) como calentamiento.
2. Etapa TRANSFORM (`src/transform.py`): métricas de mantenimiento con pandas —
   órdenes por equipo y por tipo (.groupby), tiempo medio de resolución
   (fecha_fin - fecha_inicio, ojo con NULLs), consumo de repuestos por tipo de orden,
   equipos con más correctivos (indicador de "equipo problemático"). Explicar groupby
   desde cero y dar a Marcelo al menos una métrica como ejercicio guiado.
3. Etapa LOAD (`src/load.py`): exportar a CSV y Excel en output/ para Power BI.
4. `src/pipeline.py` como orquestador de las 3 etapas.
5. Marcelo conecta Power BI manualmente a los archivos generados (él lo hace, no la IA).

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
