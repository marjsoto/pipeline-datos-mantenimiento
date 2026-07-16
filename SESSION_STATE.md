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

## DECISIÓN DE ALCANCE IMPORTANTE (acordada con Marcelo, 2026-07-15)
Marcelo aportó su visión completa de CMMS real (avisos con horas de paro, centros de
costo con presupuesto, clasificación HML/FSN de repuestos, taxonomía área/línea/sistema/
subsistema ISO 14224, tipos de técnico mecánico/eléctrico/autónomo/confiabilidad,
paros clasificados mecánico/eléctrico/operacional/ausentismo, programación semanal de
producción, KPIs). Acuerdo:
- Se mantiene la ruta de 5 proyectos como estaba. La visión COMPLETA (workflows:
  supervisor, checklists autónomos, módulo predictivo) va al Proyecto Integrador.
- La visión completa se documentará en un ROADMAP.md en el repo del Proyecto 1.
- REQUISITO INNEGOCIABLE de Marcelo: el portafolio debe mostrar KPIs básicos de
  mantenimiento Y producción (MTBF, MTTR, disponibilidad, costo por línea, paros por
  categoría). Para eso se extiende el esquema con un paquete MÍNIMO (sin workflows):
  tablas `lineas`/`areas`, `paros` (con categoría y responsable según regla: mecánico/
  eléctrico→técnico, operacional→operador, ausentismo→nadie), `centros_costo`,
  `programacion_semanal` (solo horas programadas por línea/semana), precio_unitario +
  clasificación HML/FSN en repuestos, tipo en técnicos, linea_id en equipos.
  Con datos de prueba realistas para que los KPIs den valores con sentido.

## AVANCE SESIÓN 2026-07-15 (continuación)
- Pregunta del LEFT JOIN respondida y consolidada (Marcelo eligió bien LEFT JOIN;
  se afinó el porqué: lo opcional es el vínculo al plan, no el tipo de orden).
- ROADMAP.md creado en el Proyecto 1 y extensión v2 del esquema aplicada + seed
  (ver SESSION_STATE del Proyecto 1 para el detalle — incluye lección de fan-out).
- ETAPA TRANSFORM COMPLETA (`src/transform.py`): 6 KPIs como funciones puras —
  disponibilidad_por_linea, mttr_mtbf_por_linea (solo fallas técnicas mecanico/
  electrico), paros_por_categoria (patrón groupby→agg→reset_index→sort_values,
  explicado a nivel principiante a pedido de Marcelo), costo_repuestos_por_linea,
  valor_inventario (HML), cumplimiento_preventivo. Regla anti fan-out aplicada:
  agregar por separado, merge después. Validación cruzada: disponibilidad de pandas
  coincide exacta con la query SQL de CTEs (L1 816h/14.17h/98.3%).
- ETAPA LOAD COMPLETA (`src/load.py`): un CSV por KPI + un Excel con hoja por KPI,
  en output/ (no versionado). `src/pipeline.py` orquesta E→T→L en un comando.
  Probado end-to-end: 9 órdenes, 14 paros, 14 semanas → 6 KPIs → 7 archivos.

## Próximo paso
1. MARCELO (manual, sin IA): conectar Power BI Desktop a output/ —
   Obtener datos → Texto/CSV (cada .csv) o Libro de Excel (kpis_mantenimiento.xlsx).
   Armar un dashboard básico: tarjetas de disponibilidad y MTTR/MTBF, barras de
   paros por categoría, dona de valor de inventario HML, medidor de cumplimiento.
2. Cuando el dashboard exista: captura de pantalla al README del Proyecto 2.
3. Pulir README final del Proyecto 2 y merge develop → main (cierre del proyecto).
4. Luego: Proyecto 3 (mini-app web CRUD con frontend).

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
