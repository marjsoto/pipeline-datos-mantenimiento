"""LOAD: tercera etapa del ETL.

Escribe los KPIs calculados a la carpeta output/ en dos formatos:
- Un CSV por KPI: formato universal, es lo que Power BI conecta mas facil.
- Un unico Excel con una hoja por KPI: comodo para revision humana rapida.

Los archivos NO se versionan en git (output/ esta en .gitignore): son datos
derivados — se regeneran corriendo el pipeline, la fuente de verdad es Postgres.
"""

from pathlib import Path

import pandas as pd

from config import OUTPUT_DIR


def guardar_kpis(kpis: dict[str, pd.DataFrame]) -> list[Path]:
    """Recibe un diccionario {nombre_kpi: DataFrame} y escribe todo a disco.

    Devuelve la lista de archivos generados (para loguear/verificar).
    """
    carpeta = Path(OUTPUT_DIR)
    # Crea output/ si no existe (parents=True crea carpetas intermedias;
    # exist_ok=True evita error si ya estaba creada).
    carpeta.mkdir(parents=True, exist_ok=True)

    generados = []

    # --- Un CSV por KPI ---
    for nombre, df in kpis.items():
        ruta_csv = carpeta / f"{nombre}.csv"
        # index=False: no escribir el indice de pandas como columna extra
        # (Power BI lo veria como una columna basura sin nombre).
        df.to_csv(ruta_csv, index=False, encoding="utf-8")
        generados.append(ruta_csv)

    # --- Un Excel con una hoja por KPI ---
    ruta_excel = carpeta / "kpis_mantenimiento.xlsx"
    with pd.ExcelWriter(ruta_excel, engine="openpyxl") as writer:
        for nombre, df in kpis.items():
            # Los nombres de hoja en Excel tienen limite de 31 caracteres.
            df.to_excel(writer, sheet_name=nombre[:31], index=False)
    generados.append(ruta_excel)

    return generados
