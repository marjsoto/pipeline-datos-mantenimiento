"""PIPELINE: orquestador del ETL completo.

Ejecuta las tres etapas en orden — Extract -> Transform -> Load — y reporta
que genero. Este es el unico archivo que se corre en el uso normal:

    python src/pipeline.py

Cada etapa vive en su propio modulo y se puede probar por separado
(python src/extract.py, python src/transform.py).
"""

import extract
import transform
import load


def main():
    print(">> EXTRACT: leyendo datos desde PostgreSQL...")
    ordenes = extract.extraer_ordenes()
    repuestos = extract.extraer_repuestos()
    uso_repuestos = extract.extraer_uso_repuestos()
    paros = extract.extraer_paros()
    programacion = extract.extraer_programacion()
    print(f"   {len(ordenes)} ordenes, {len(paros)} paros, "
          f"{len(programacion)} semanas programadas, {len(repuestos)} repuestos")

    print(">> TRANSFORM: calculando KPIs...")
    kpis = {
        "disponibilidad_por_linea": transform.disponibilidad_por_linea(paros, programacion),
        "mttr_mtbf_por_linea": transform.mttr_mtbf_por_linea(paros, programacion),
        "paros_por_categoria": transform.paros_por_categoria(paros),
        "costo_repuestos_por_linea": transform.costo_repuestos_por_linea(uso_repuestos),
        "valor_inventario_hml": transform.valor_inventario(repuestos),
        "cumplimiento_preventivo": transform.cumplimiento_preventivo(ordenes),
    }
    print(f"   {len(kpis)} KPIs calculados")

    print(">> LOAD: escribiendo reportes...")
    archivos = load.guardar_kpis(kpis)
    for ruta in archivos:
        print(f"   {ruta}")

    print("\nPipeline completado. Conecta Power BI a los archivos de output/")
    print("(Obtener datos -> Texto/CSV para los .csv, o -> Libro de Excel para el .xlsx)")


if __name__ == "__main__":
    main()
