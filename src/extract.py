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
    """Consumo de repuestos por orden (tabla puente + JOINs).

    Incluye el precio unitario y la linea del equipo para poder calcular
    costos de mantenimiento por linea/centro de costo en la etapa transform.
    """
    query = """
        SELECT orep.orden_id,
               orep.cantidad_usada,
               r.codigo AS repuesto_codigo,
               r.nombre AS repuesto_nombre,
               r.precio_unitario,
               cc.codigo AS centro_costo,
               o.tipo   AS orden_tipo,
               COALESCE(o.fecha_fin, o.created_at) AS fecha,
               e.codigo AS equipo_codigo,
               l.nombre AS linea
        FROM orden_repuestos orep
        JOIN repuestos r ON orep.repuesto_id = r.id
        LEFT JOIN centros_costo cc ON r.centro_costo_id = cc.id
        JOIN ordenes_trabajo o ON orep.orden_id = o.id
        JOIN equipos e ON o.equipo_id = e.id
        LEFT JOIN lineas l ON e.linea_id = l.id
    """
    return pd.read_sql(query, engine)


def extraer_paros() -> pd.DataFrame:
    """Paros (downtime) con equipo, linea y responsable segun categoria."""
    query = """
        SELECT p.id,
               p.categoria,
               p.descripcion,
               p.fecha_inicio,
               p.fecha_fin,
               p.horas_paro,
               e.codigo AS equipo_codigo,
               e.criticidad,
               l.nombre AS linea,
               t.nombre AS tecnico_nombre,
               op.nombre AS operador_nombre
        FROM paros p
        JOIN equipos e ON p.equipo_id = e.id
        LEFT JOIN lineas l ON e.linea_id = l.id
        LEFT JOIN tecnicos t ON p.tecnico_id = t.id
        LEFT JOIN operadores op ON p.operador_id = op.id
    """
    return pd.read_sql(query, engine)


def extraer_programacion() -> pd.DataFrame:
    """Horas programadas de produccion por linea y semana."""
    query = """
        SELECT ps.semana_inicio,
               ps.horas_programadas,
               l.nombre AS linea
        FROM programacion_semanal ps
        JOIN lineas l ON ps.linea_id = l.id
    """
    return pd.read_sql(query, engine)


def extraer_metas() -> pd.DataFrame:
    """Metas AOP mensuales por KPI (cargadas manualmente en la base)."""
    return pd.read_sql(
        "SELECT kpi, mes, valor_aop, valor_anio_anterior FROM metas_kpi",
        engine,
    )


if __name__ == "__main__":
    # Prueba rapida de la etapa: ejecutar `python src/extract.py` muestra
    # cuantas filas trae cada extraccion y una vista previa.
    for nombre, funcion in [
        ("ordenes", extraer_ordenes),
        ("equipos", extraer_equipos),
        ("repuestos", extraer_repuestos),
        ("uso_repuestos", extraer_uso_repuestos),
        ("paros", extraer_paros),
        ("programacion", extraer_programacion),
    ]:
        df = funcion()
        print(f"\n=== {nombre}: {len(df)} filas ===")
        print(df.head(3).to_string())
