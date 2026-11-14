"""Step 3 - Count evenly: from hot spots to 1 km cell-days.

Input:  data/derivados/focos_limpios.parquet (step 2)
Output: data/derivados/conteo_provincia.parquet (+ .csv)   province x month x satellite x day/night
        data/derivados/conteo_pais.parquet                  same for Argentina, counted on the cells directly
        data/derivados/conteo_departamento.parquet          same by department (for the app's area view)
        data/derivados/servicio_satelites.csv               months each satellite counts for
        reportes/paso3_contar.md                            the counts and the checks

A cell-day is a ~1 km cell (0.01 deg, floor of the coordinates) that had at least one hot spot on a date (local
Argentine date). It is counted separately for each satellite and for day and night; satellites are never added
together (step 4 brings them to one scale). Months in which a satellite was flying and saw no fire are 0;
months before or after its service do not exist in the table ("no data", not zero).

Usage: python pipeline/paso3_contar.py
"""

from datetime import date, datetime
from pathlib import Path

import duckdb
import pandas as pd

RAIZ = Path(__file__).resolve().parents[1]
DERIV = RAIZ / "data" / "derivados"
LIMPIOS = (DERIV / "focos_limpios.parquet").as_posix()
REPORTES = RAIZ / "reportes"

con = duckdb.connect()
con.execute("set TimeZone = 'UTC'")
con.execute(f"create view limpios as select * from '{LIMPIOS}'")

# --- service period of each satellite, from the data itself (first and last date with any detection) -------
servicio = con.execute("""
select plataforma, any_value(sensor) as sensor, min(fecha) as desde, max(fecha) as hasta
from limpios group by plataforma order by desde""").df()
servicio["desde"] = pd.to_datetime(servicio.desde).dt.date
servicio["hasta"] = pd.to_datetime(servicio.hasta).dt.date
# Terra's first detection is 31/10/2000 (one day): it counts from November 2000.
servicio.loc[servicio.plataforma == "Terra", "desde"] = date(2000, 11, 1)
servicio.to_csv(DERIV / "servicio_satelites.csv", index=False)

meses = []
for r in servicio.itertuples():
    for m in pd.period_range(r.desde, r.hasta, freq="M"):
        ini, fin = max(m.start_time.date(), r.desde), min(m.end_time.date(), r.hasta)
        meses.append((r.plataforma, r.sensor, m.year, m.month, (fin - ini).days + 1, m.days_in_month))
meses = pd.DataFrame(meses, columns=["plataforma", "sensor", "anio", "mes", "dias_servicio", "dias_mes"])
meses["mes_completo"] = meses.dias_servicio == meses.dias_mes
con.register("meses_df", meses)
con.execute("create table meses as select * from meses_df")
con.execute("create table momentos as select * from (values ('dia', true), ('noche', false)) t(momento, dia)")

# --- 3.1-3.3: cell-days -------------------------------------------------------------------------------------
def contar(clave, donde="true"):
    return f"""
    select {clave}, anio, mes, plataforma, case when dia then 'dia' else 'noche' end as momento,
           count(distinct (ci, cj, fecha)) as celdas_dia, count(*) as focos
    from limpios where {donde} group by all"""


con.execute(f"create table c_prov as {contar('prov_cod, provincia', 'provincia is not null')}")
con.execute(f"create table c_dep as {contar('prov_cod, provincia, depto_cod, depto', 'depto_cod is not null')}")
con.execute(f"create table c_pais as {contar(chr(39) + '00' + chr(39) + ' as prov_cod, ' + chr(39) + 'Argentina' + chr(39) + ' as provincia')}")

# --- 3.4: zeros only where the satellite was flying ---------------------------------------------------------
def completar(tabla, claves, universo):
    on = " and ".join(f"c.{k} = g.{k}" for k in claves + ["anio", "mes", "plataforma", "momento"])
    sel = ", ".join(f"g.{k}" for k in claves)
    return f"""
    select {sel}, g.anio, g.mes, g.plataforma, g.sensor, g.momento,
           coalesce(c.celdas_dia, 0) as celdas_dia, coalesce(c.focos, 0) as focos,
           g.dias_servicio, g.mes_completo
    from (select u.*, m.*, mo.momento from ({universo}) u cross join meses m cross join momentos mo) g
    left join {tabla} c on {on}
    order by all"""


salidas = {
    "provincia": completar("c_prov", ["prov_cod", "provincia"],
                           "select distinct prov_cod, provincia from limpios where provincia is not null"),
    "departamento": completar("c_dep", ["prov_cod", "provincia", "depto_cod", "depto"],
                              "select distinct prov_cod, provincia, depto_cod, depto from limpios where depto_cod is not null"),
    "pais": completar("c_pais", ["prov_cod", "provincia"], "select '00' as prov_cod, 'Argentina' as provincia"),
}
for nivel, sql in salidas.items():
    con.execute(f"create table conteo_{nivel} as {sql}")
    con.execute(f"copy conteo_{nivel} to '{(DERIV / f'conteo_{nivel}.parquet').as_posix()}' (format parquet)")
con.execute(f"copy conteo_provincia to '{(DERIV / 'conteo_provincia.csv').as_posix()}' (header, delimiter ',')")

# --- checks -------------------------------------------------------------------------------------------------
q = lambda s: con.execute(s).fetchall()
chk = []


def control(nombre, ok, detalle):
    chk.append((nombre, ok, detalle))
    assert ok, f"{nombre}: {detalle}"


# every counted cell-day landed in the zero-filled table (no fire outside the service months)
# (the only exclusion on purpose: Terra's single day of October 2000)
for nivel, src in [("provincia", "c_prov"), ("departamento", "c_dep"), ("pais", "c_pais")]:
    a, b, x = q(f"""select (select sum(celdas_dia) from {src}), (select sum(celdas_dia) from conteo_{nivel}),
                   (select coalesce(sum(celdas_dia), 0) from {src} where plataforma = 'Terra' and anio = 2000 and mes = 10)""")[0]
    control(f"Nada se pierde al completar ({nivel})", a - x == b,
            f"{a:,} contadas - {x} de Terra 31/10/2000 = {b:,} en la tabla")
n_prov = q("select count(distinct provincia) from conteo_provincia")[0][0]
control("Las 24 provincias", n_prov == 24, f"{n_prov}")
huecos = q("""select count(*) from (select provincia, plataforma, momento, count(*) n from conteo_provincia group by all) t
              join (select plataforma, count(*) esperados from meses group by 1) e using (plataforma)
              where t.n <> e.esperados""")[0][0]
control("Sin huecos: cada provincia tiene todos los meses de servicio de cada satélite", huecos == 0, f"{huecos} combinaciones incompletas")
antes = q("select count(*) from conteo_provincia where plataforma = 'NOAA20' and anio * 100 + mes < 201804")[0][0]
control("Sin ceros de más: NOAA-20 no aparece antes de abril de 2018", antes == 0, f"{antes} filas")

fpc = q("""select plataforma, sum(focos) / sum(celdas_dia) from conteo_pais where anio = 2025 group by 1 order by 1""")
fpc = dict(fpc)
ok = all(1.0 <= fpc[p] <= 1.15 for p in ("Aqua", "Terra")) and all(1.4 <= fpc[p] <= 2.0 for p in ("SNPP", "NOAA20", "NOAA21"))
control("Focos por celda-día 2025: MODIS cerca de 1, VIIRS entre 1,4 y 2", ok,
        ", ".join(f"{p} {v:.2f}" for p, v in fpc.items()))

anual = con.execute("""
select anio, sum(celdas_dia) filter (where plataforma = 'SNPP') / sum(celdas_dia) filter (where plataforma = 'Aqua') as snpp_aqua,
       sum(celdas_dia) filter (where plataforma = 'NOAA20') / sum(celdas_dia) filter (where plataforma = 'SNPP') as n20_snpp,
       sum(celdas_dia) filter (where plataforma = 'NOAA21') / sum(celdas_dia) filter (where plataforma = 'NOAA20') as n21_n20
from conteo_pais where mes_completo group by anio order by anio""").df()
r = anual[anual.anio.between(2013, 2022)].snpp_aqua
control("Suomi NPP / Aqua estable, cerca de 3, en 2013-2022", r.between(2.3, 3.8).all(), f"{r.min():.2f} a {r.max():.2f}")
r = anual[anual.anio.between(2019, 2025)].n20_snpp
control("NOAA-20 / Suomi NPP cerca de 1 desde 2019", r.between(0.85, 1.15).all(), f"{r.min():.2f} a {r.max():.2f}")
r = anual[anual.anio.between(2024, 2025)].n21_n20
control("NOAA-21 / NOAA-20 cerca de 1 (2024-2025)", r.between(0.85, 1.15).all(), f"{r.min():.2f} a {r.max():.2f}")
dif = q("""select (select sum(celdas_dia) from conteo_provincia) / (select sum(celdas_dia) from conteo_pais) - 1""")[0][0]
control("Suma de provincias vs. país contado directo: diferencia chica", abs(dif) < 0.01, f"{dif:+.2%}")

cat = con.execute("""
select anio, mes, sum(celdas_dia) as celdas from conteo_provincia
where provincia = 'Catamarca' and plataforma = 'NOAA20' group by all order by celdas desc limit 3""").fetchall()

# --- report -------------------------------------------------------------------------------------------------
def miles(x):
    return f"{x:,.0f}".replace(",", ".")


nombres = {"Terra": "Terra (MODIS)", "Aqua": "Aqua (MODIS)", "SNPP": "Suomi NPP (VIIRS)",
           "NOAA20": "NOAA-20 (VIIRS)", "NOAA21": "NOAA-21 (VIIRS)"}
t25 = con.execute("""select plataforma, sum(focos), sum(celdas_dia) from conteo_pais where anio = 2025
                     group by 1 order by 1""").fetchall()
n_filas = {n: q(f"select count(*), count(*) filter (where celdas_dia > 0) from conteo_{n}")[0] for n in salidas}
cat926 = con.execute("""select plataforma, momento, celdas_dia from conteo_provincia
                        where provincia = 'Catamarca' and anio = 2026 and mes = 9 order by plataforma, momento""").fetchall()

L = ["# Paso 3: contar parejo", "",
     f"Generado por `pipeline/paso3_contar.py` el {datetime.now():%d/%m/%Y %H:%M}.", "",
     "## Meses de servicio de cada satélite", "",
     "| Satélite | Desde | Hasta | Meses |", "|---|---|---|---|"]
for r in servicio.itertuples():
    L.append(f"| {nombres[r.plataforma]} | {r.desde:%d/%m/%Y} | {r.hasta:%d/%m/%Y} | {(meses.plataforma == r.plataforma).sum()} |")
L += ["", "Fuera de esas fechas la tabla no tiene filas (\"sin dato\"). Los meses de entrada, de salida y el mes en curso "
      "llevan `mes_completo = False` y `dias_servicio` con los días que cubren.", "",
      "## 2025, todo el país", "", "| Satélite | Focos | Celdas-día | Focos por celda-día |", "|---|---|---|---|"]
L += [f"| {nombres[p]} | {miles(f)} | {miles(c)} | {f / c:.2f} |".replace(".", ",", 1) if False else
      f"| {nombres[p]} | {miles(f)} | {miles(c)} | {f / c:.2f} |" for p, f, c in t25]
L += ["", "## Cocientes anuales (celdas-día, meses completos)", "",
      "| Año | Suomi NPP / Aqua | NOAA-20 / Suomi NPP | NOAA-21 / NOAA-20 |", "|---|---|---|---|"]
fmt = lambda v: "" if pd.isna(v) else f"{v:.2f}"
L += [f"| {int(r.anio)} | {fmt(r.snpp_aqua)} | {fmt(r.n20_snpp)} | {fmt(r.n21_n20)} |" for r in anual.itertuples() if r.anio >= 2012]
L += ["", "## Catamarca, septiembre de 2026", "", "| Satélite | Momento | Celdas-día |", "|---|---|---|"]
L += [f"| {nombres[p]} | {m} | {c} |" for p, m, c in cat926]
L += ["", "Meses más altos de Catamarca con NOAA-20 (día + noche): " +
      "; ".join(f"{m:02d}/{a}: {c}" for a, m, c in cat), "",
      "## Tablas", "", "| Tabla | Filas | Con fuego |", "|---|---|---|"]
L += [f"| `conteo_{n}.parquet` | {miles(a)} | {miles(b)} |" for n, (a, b) in n_filas.items()]
L += ["", "## Controles", ""] + [f"- {'OK' if ok else 'FALLA'} — {n}: {d}" for n, ok, d in chk]
(REPORTES / "paso3_contar.md").write_text("\n".join(L) + "\n", encoding="utf-8")
print("\n".join(L))
