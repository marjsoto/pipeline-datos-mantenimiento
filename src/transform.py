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


def _mes(fechas: pd.Series) -> pd.Series:
    """Trunca fechas al primer dia de su mes (para agrupar por mes)."""
    return pd.to_datetime(fechas).dt.to_period('M').dt.to_timestamp()


def kpi_mensual_vs_aop(paros: pd.DataFrame, programacion: pd.DataFrame,
                       uso_repuestos: pd.DataFrame, metas: pd.DataFrame) -> pd.DataFrame:
    """El dataset central estilo KTB: por cada KPI y mes, las tres series
    Real / AOP / Anio anterior — listo para graficos de linea en Power BI.

    Formato "largo" (una fila por kpi+mes) a proposito: en Power BI filtras
    por kpi y pones mes en el eje, real/aop/anio_anterior como series.
    """
    # --- Reales mensuales, cada uno agregado POR SEPARADO (anti fan-out) ---
    prog = programacion.copy()
    prog['mes'] = _mes(prog['semana_inicio'])
    prog_mes = prog.groupby('mes')['horas_programadas'].sum()

    par = paros.copy()
    par['mes'] = _mes(par['fecha_inicio'])
    paro_mes = par.groupby('mes')['horas_paro'].sum()

    fallas = par[par['categoria'].isin(['mecanico', 'electrico'])]
    fallas_mes = fallas.groupby('mes').agg(
        n_fallas=('id', 'count'), horas_falla=('horas_paro', 'sum'))

    uso = uso_repuestos.copy()
    uso['mes'] = _mes(uso['fecha'])
    uso['costo'] = uso['cantidad_usada'] * uso['precio_unitario']
    gasto_mes = uso.groupby('mes')['costo'].sum()

    # --- Combinar en una tabla por mes y derivar los KPIs ---
    base = pd.DataFrame({'horas_prog': prog_mes, 'horas_paro': paro_mes}).join(fallas_mes)
    base['disponibilidad_pct'] = (
        100 * (base['horas_prog'] - base['horas_paro']) / base['horas_prog']).round(1)
    base['mttr_horas'] = (base['horas_falla'] / base['n_fallas']).round(2)
    base['mtbf_horas'] = (
        (base['horas_prog'] - base['horas_falla']) / base['n_fallas']).round(1)
    base['gasto_repuestos_usd'] = gasto_mes.round(2)

    # --- A formato largo: una fila por (kpi, mes) con el valor real ---
    kpis = ['disponibilidad_pct', 'mttr_horas', 'mtbf_horas', 'gasto_repuestos_usd']
    real_largo = (
        base[kpis].reset_index()
                  .melt(id_vars='mes', var_name='kpi', value_name='real')
    )

    # --- Unir con las metas AOP (LEFT: un mes sin meta cargada igual aparece) ---
    metas = metas.copy()
    metas['mes'] = pd.to_datetime(metas['mes'])
    kpi = real_largo.merge(metas, on=['kpi', 'mes'], how='left')
    kpi = kpi.rename(columns={'valor_aop': 'aop', 'valor_anio_anterior': 'anio_anterior'})
    kpi['desviacion_vs_aop'] = (kpi['real'] - kpi['aop']).round(2)
    return kpi.sort_values(['kpi', 'mes']).reset_index(drop=True)


def pareto_paros_por_equipo(paros: pd.DataFrame) -> pd.DataFrame:
    """Pareto clasico de mantenimiento: que equipos concentran las horas de
    paro. peso_pct y acumulado_pct permiten la regla 80/20 en Power BI."""
    pareto = (
        paros.groupby('equipo_codigo')
             .agg(eventos=('id', 'count'), horas_paro=('horas_paro', 'sum'))
             .reset_index()
             .sort_values('horas_paro', ascending=False)
    )
    total = pareto['horas_paro'].sum()
    pareto['peso_pct'] = (100 * pareto['horas_paro'] / total).round(1)
    pareto['acumulado_pct'] = pareto['peso_pct'].cumsum().round(1)
    return pareto


def cascada_horas_operadas(paros: pd.DataFrame, programacion: pd.DataFrame) -> pd.DataFrame:
    """Datos para el grafico de cascada (waterfall) de Power BI:
    horas programadas -> menos cada categoria de paro -> horas operadas.
    'orden' define la secuencia de izquierda a derecha en el grafico."""
    total_prog = programacion['horas_programadas'].sum()
    por_categoria = paros.groupby('categoria')['horas_paro'].sum()

    filas = [{'concepto': 'Horas programadas', 'horas': round(total_prog, 2), 'orden': 0}]
    for i, (categoria, horas) in enumerate(
            por_categoria.sort_values(ascending=False).items(), start=1):
        filas.append({'concepto': f'Paro {categoria}', 'horas': round(-horas, 2), 'orden': i})
    filas.append({
        'concepto': 'Horas operadas',
        'horas': round(total_prog - por_categoria.sum(), 2),
        'orden': len(filas),
    })
    return pd.DataFrame(filas)


def paros_por_categoria(paros: pd.DataFrame) -> pd.DataFrame:
    """Total de eventos y horas de paro por categoria (mecanico/electrico/
    operacional/ausentismo). El desglose que pidio Marcelo para ver de un
    vistazo donde se concentra el downtime."""
    return (
        paros.groupby('categoria')
             .agg(eventos=('id', 'count'), horas_totales=('horas_paro', 'sum'))
             .reset_index()
             .sort_values('horas_totales', ascending=False)
    )


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

    print("\n=== Paros por categoria ===")
    print(paros_por_categoria(paros).to_string(index=False))
