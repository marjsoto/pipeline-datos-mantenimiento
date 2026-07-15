"""TRANSFORM: segunda etapa del ETL.

Recibe los DataFrames crudos de extract y calcula los KPIs de mantenimiento
y produccion. Cada funcion es "pura": recibe DataFrames, devuelve un DataFrame
nuevo, no toca la base de datos — eso las hace faciles de probar y de razonar.

REGLA ANTI FAN-OUT (aprendida en el Proyecto 1): nunca hacer merge antes de
agregar. Primero se agrega cada tabla por separado (.groupby), y recien
despues se unen los resultados ya resumidos (.merge).
"""

import pandas as pd


def disponibilidad_por_linea(paros: pd.DataFrame, programacion: pd.DataFrame) -> pd.DataFrame:
    """Disponibilidad = (horas programadas - horas de paro) / horas programadas.

    Agregamos paros y programacion POR SEPARADO y unimos al final —
    exactamente la correccion del bug de fan-out que vimos en SQL con CTEs.
    """
    horas_prog = (
        programacion.groupby('linea')['horas_programadas'].sum().reset_index()
    )
    horas_paro = (
        paros.dropna(subset=['linea'])          # paros de equipos sin linea no aplican
             .groupby('linea')['horas_paro'].sum()
             .reset_index()
    )

    # merge = el JOIN de pandas. how='left' = LEFT JOIN: una linea sin paros
    # debe aparecer igual (con 100% de disponibilidad), no desaparecer.
    kpi = horas_prog.merge(horas_paro, on='linea', how='left')
    kpi['horas_paro'] = kpi['horas_paro'].fillna(0)  # sin paros -> 0 horas, no NaN

    kpi['disponibilidad_pct'] = (
        100 * (kpi['horas_programadas'] - kpi['horas_paro']) / kpi['horas_programadas']
    ).round(1)
    return kpi


def mttr_mtbf_por_linea(paros: pd.DataFrame, programacion: pd.DataFrame) -> pd.DataFrame:
    """MTTR y MTBF por linea, considerando solo FALLAS (paros tecnicos:
    mecanico/electrico). Paros operacionales y ausentismo no son fallas de equipo.

    MTTR = horas de paro por fallas / numero de fallas   (que tan rapido reparamos)
    MTBF = horas operadas / numero de fallas             (cada cuanto falla algo)
    donde horas operadas = horas programadas - horas de paro por fallas.
    """
    fallas = paros[paros['categoria'].isin(['mecanico', 'electrico'])].dropna(subset=['linea'])

    agg_fallas = (
        fallas.groupby('linea')
              .agg(numero_fallas=('id', 'count'), horas_falla=('horas_paro', 'sum'))
              .reset_index()
    )
    horas_prog = programacion.groupby('linea')['horas_programadas'].sum().reset_index()

    kpi = horas_prog.merge(agg_fallas, on='linea', how='left')
    kpi[['numero_fallas', 'horas_falla']] = kpi[['numero_fallas', 'horas_falla']].fillna(0)

    kpi['mttr_horas'] = (kpi['horas_falla'] / kpi['numero_fallas']).round(2)
    kpi['mtbf_horas'] = (
        (kpi['horas_programadas'] - kpi['horas_falla']) / kpi['numero_fallas']
    ).round(1)
    return kpi[['linea', 'numero_fallas', 'horas_falla', 'mttr_horas', 'mtbf_horas']]


def costo_repuestos_por_linea(uso_repuestos: pd.DataFrame) -> pd.DataFrame:
    """Costo de repuestos consumidos, por linea y centro de costo.

    El costo por fila se calcula aqui (columna derivada), no se guarda en la
    base: cantidad x precio siempre se puede recalcular.
    """
    df = uso_repuestos.copy()
    df['costo'] = df['cantidad_usada'] * df['precio_unitario']

    return (
        df.groupby(['linea', 'centro_costo'], dropna=False)
          .agg(costo_total=('costo', 'sum'), items_consumidos=('cantidad_usada', 'sum'))
          .reset_index()
          .sort_values('costo_total', ascending=False)
    )


def valor_inventario(repuestos: pd.DataFrame) -> pd.DataFrame:
    """Valor de inventario por clasificacion HML: stock x precio unitario."""
    df = repuestos.copy()
    df['valor_stock'] = df['stock_actual'] * df['precio_unitario']

    return (
        df.groupby('clasificacion_costo', dropna=False)
          .agg(
              repuestos=('id', 'count'),
              unidades_stock=('stock_actual', 'sum'),
              valor_total=('valor_stock', 'sum'),
          )
          .reset_index()
          .sort_values('valor_total', ascending=False)
    )


def cumplimiento_preventivo(ordenes: pd.DataFrame) -> pd.DataFrame:
    """% de ordenes preventivas completadas sobre el total de preventivas."""
    prev = ordenes[ordenes['tipo'] == 'preventivo']
    total = len(prev)
    completadas = (prev['estado'] == 'completada').sum()
    pct = round(100 * completadas / total, 1) if total > 0 else 0.0
    return pd.DataFrame([{
        'preventivas_totales': total,
        'preventivas_completadas': completadas,
        'cumplimiento_pct': pct,
    }])


# TODO (Marcelo — tu ejercicio, el mas directo de todos):
# def paros_por_categoria(paros: pd.DataFrame) -> pd.DataFrame:
#     Agrupa los paros por 'categoria' y devuelve, por cada una:
#       - eventos: cantidad de paros        -> ('id', 'count')
#       - horas_totales: suma de horas      -> ('horas_paro', 'sum')
#     Pista: mira agg_fallas en mttr_mtbf_por_linea — es el mismo patron
#     groupby + agg + reset_index, sin el filtro previo.


if __name__ == "__main__":
    # Prueba de la etapa completa: extrae y calcula todos los KPIs.
    from extract import (
        extraer_ordenes, extraer_repuestos, extraer_uso_repuestos,
        extraer_paros, extraer_programacion,
    )

    paros = extraer_paros()
    programacion = extraer_programacion()

    print("\n=== Disponibilidad por linea ===")
    print(disponibilidad_por_linea(paros, programacion).to_string(index=False))

    print("\n=== MTTR / MTBF por linea (solo fallas tecnicas) ===")
    print(mttr_mtbf_por_linea(paros, programacion).to_string(index=False))

    print("\n=== Costo de repuestos por linea / centro de costo ===")
    print(costo_repuestos_por_linea(extraer_uso_repuestos()).to_string(index=False))

    print("\n=== Valor de inventario por clasificacion HML ===")
    print(valor_inventario(extraer_repuestos()).to_string(index=False))

    print("\n=== Cumplimiento del plan preventivo ===")
    print(cumplimiento_preventivo(extraer_ordenes()).to_string(index=False))
