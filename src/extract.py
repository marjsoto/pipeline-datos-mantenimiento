"""EXTRACT: primera etapa del ETL.

Trae los datos crudos desde PostgreSQL (la base del Proyecto 1) y los convierte
en DataFrames de pandas. Esta etapa NO transforma nada: solo extrae. Mantener
las etapas separadas (extract / transform / load) hace el pipeline testeable
y facil de razonar — si un numero sale mal, sabes en que etapa buscar.
"""

import pandas as pd

from config import engine


def extraer_ordenes() -> pd.DataFrame:
    """Ordenes de trabajo con datos del equipo y tecnico ya unidos (JOIN).

    Hacemos el JOIN en SQL (y no despues en pandas) porque Postgres es mas
    eficiente uniendo tablas con sus indices, y el DataFrame llega listo
    para analizar.
    """
    query = """
        SELECT o.id,
               o.tipo,
               o.prioridad,
               o.estado,
               o.descripcion,
               o.fecha_programada,
               o.fecha_inicio,
               o.fecha_fin,
               o.created_at,
               e.codigo    AS equipo_codigo,
               e.nombre    AS equipo_nombre,
               e.ubicacion AS equipo_ubicacion,
               t.nombre    AS tecnico_nombre,
               t.especialidad AS tecnico_especialidad
        FROM ordenes_trabajo o
        JOIN equipos e ON o.equipo_id = e.id
        LEFT JOIN tecnicos t ON o.tecnico_id = t.id
    """
    return pd.read_sql(query, engine)


def extraer_equipos() -> pd.DataFrame:
    return pd.read_sql("SELECT * FROM equipos", engine)


def extraer_repuestos() -> pd.DataFrame:
    return pd.read_sql("SELECT * FROM repuestos", engine)


def extraer_uso_repuestos() -> pd.DataFrame:
    """Consumo de repuestos por orden (tabla puente + JOINs)."""
    query = """
        SELECT orep.orden_id,
               orep.cantidad_usada,
               r.codigo AS repuesto_codigo,
               r.nombre AS repuesto_nombre,
               o.tipo   AS orden_tipo,
               e.codigo AS equipo_codigo
        FROM orden_repuestos orep
        JOIN repuestos r ON orep.repuesto_id = r.id
        JOIN ordenes_trabajo o ON orep.orden_id = o.id
        JOIN equipos e ON o.equipo_id = e.id
    """
    return pd.read_sql(query, engine)


if __name__ == "__main__":
    # Prueba rapida de la etapa: ejecutar `python src/extract.py` muestra
    # cuantas filas trae cada extraccion y una vista previa.
    for nombre, funcion in [
        ("ordenes", extraer_ordenes),
        ("equipos", extraer_equipos),
        ("repuestos", extraer_repuestos),
        ("uso_repuestos", extraer_uso_repuestos),
    ]:
        df = funcion()
        print(f"\n=== {nombre}: {len(df)} filas ===")
        print(df.head(3).to_string())
