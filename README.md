# Pipeline de Datos — Análisis de Mantenimiento Industrial

Proyecto 2 del portafolio técnico de Marcelo. Pipeline ETL en Python que extrae los
datos operativos de la base PostgreSQL del [Proyecto 1](https://github.com/marjsoto/api-mantenimiento-industrial)
(equipos, órdenes de trabajo, repuestos), los limpia y transforma con Pandas, y genera
reportes automáticos listos para consumir desde Power BI.

## Stack
- **Python 3.12** + entorno virtual (`venv`)
- **Pandas** — transformación y análisis de datos
- **SQLAlchemy + psycopg** — extracción desde PostgreSQL
- **PostgreSQL 16** (el mismo contenedor Docker del Proyecto 1, como fuente)

## Qué demuestra este proyecto
- ETL básico: Extract (SQL) → Transform (Pandas) → Load (tablas de reporte / archivos)
- Limpieza y validación de datos reales
- Generación de reportes automáticos (CSV/Excel) para Power BI
- Reutilización de infraestructura entre proyectos (misma BD como fuente)

## Cómo levantar el proyecto
```bash
# Requiere el contenedor del Proyecto 1 corriendo:
#   cd ../01-api-mantenimiento-industrial && docker compose up -d
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -r requirements.txt
python src/pipeline.py
```

## Estado del proyecto
Este repo se trabaja de forma colaborativa entre Marcelo y distintos asistentes de IA.
El estado exacto vive en [`SESSION_STATE.md`](./SESSION_STATE.md). Las reglas de trabajo
están en [`PROMPT_MAESTRO.md`](./PROMPT_MAESTRO.md).
