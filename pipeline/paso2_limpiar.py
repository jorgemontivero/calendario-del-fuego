"""Step 2 - Clean: keep only vegetation fires.

Input:  data/focos.parquet (step 1: every NASA FIRMS hot spot in Argentina, MODIS + VIIRS, 2000-today)
Output: data/derivados/fuentes_fijas.parquet  ~1 km cells that are persistent heat sources (gas flares, industry)
        data/derivados/focos_limpios.parquet  hot spots that pass the three filters, with the 1 km cell (ci, cj)
        reportes/paso2_limpiar.md             the funnel and where each filter removes

Filters (each one has a stated reason, is measured, and is checked by province):
  2.1  FIRMS type = 0 (vegetation fire). Drops volcanoes (1), other static sources (2), offshore (3).
       Near-real-time data has no type: it comes as 0 and is covered by 2.3.
  2.2  Confidence: MODIS >= 30; VIIRS nominal or high (`conf_ok`, computed in step 1).
  2.3  Persistent sources FIRMS did not flag: 0.01 deg cells (~1 km) where VIIRS detected heat on
       >= 30 distinct days (2012-today). All hot spots in those cells are dropped, from every satellite
       and year. Threshold chosen with two control provinces: Neuquen (gas flares) and Formosa (real fire).
  2.4  Day/night flag (`dia`): nothing is dropped; step 4 converts day and night separately.

Usage: python pipeline/paso2_limpiar.py
"""

from datetime import datetime
from pathlib import Path

import duckdb

RAIZ = Path(__file__).resolve().parents[1]
FOCOS = (RAIZ / "data" / "focos.parquet").as_posix()
DERIV = RAIZ / "data" / "derivados"
REPORTES = RAIZ / "reportes"
UMBRAL_DIAS = 30

DERIV.mkdir(parents=True, exist_ok=True)
REPORTES.mkdir(parents=True, exist_ok=True)
con = duckdb.connect()
con.execute("set TimeZone = 'UTC'")

# --- the funnel, filter by filter ---------------------------------------------------------------------------
con.execute(f"""
create view todo as
select *, floor(lat * 100)::int as ci, floor(lon * 100)::int as cj, substr(depto_cod, 1, 2) as prov_cod
from '{FOCOS}'
""")
con.execute("create view f21 as select * from todo where tipo = 0")
con.execute("create view base as select * from f21 where conf_ok")
con.execute(f"""
create table fijos as
select ci, cj, count(distinct fecha) as dias, min(fecha) as primera, max(fecha) as ultima,
       (ci + 0.5) / 100 as lat, (cj + 0.5) / 100 as lon, mode(provincia) as provincia
from base where sensor = 'VIIRS'
group by ci, cj having count(distinct fecha) >= {UMBRAL_DIAS}
""")
con.execute("create view limpio as select * from base anti join fijos using (ci, cj)")

n = {k: con.execute(f"select count(*) from {v}").fetchone()[0]
     for k, v in [("todo", "todo"), ("f21", "f21"), ("base", "base"), ("limpio", "limpio")]}
n_fijos = con.execute("select count(*) from fijos").fetchone()[0]

# --- outputs ------------------------------------------------------------------------------------------------
con.execute(f"copy (select * from fijos order by dias desc) to '{(DERIV / 'fuentes_fijas.parquet').as_posix()}' (format parquet)")
con.execute(f"""
copy (
  select fuente, sensor, plataforma, lat, lon, ci, cj, dt_utc, fecha, anio, mes, dia, frp, scan, track,
         prov_cod, provincia, depto_cod, depto
  from limpio order by fecha, plataforma
) to '{(DERIV / 'focos_limpios.parquet').as_posix()}' (format parquet, compression zstd)
""")

# --- checks -------------------------------------------------------------------------------------------------
assert n["todo"] >= n["f21"] >= n["base"] >= n["limpio"] > 0
escrito = con.execute(f"select count(*) from '{(DERIV / 'focos_limpios.parquet').as_posix()}'").fetchone()[0]
assert escrito == n["limpio"], (escrito, n["limpio"])
fijos_en_limpio = con.execute(f"""select count(*) from '{(DERIV / 'focos_limpios.parquet').as_posix()}'
                             semi join fijos using (ci, cj)""").fetchone()[0]
assert fijos_en_limpio == 0

# --- report -------------------------------------------------------------------------------------------------
def miles(x):
    return f"{x:,.0f}".replace(",", ".")


por_sensor = con.execute("""
select sensor,
       count(*) as total,
       count(*) filter (where tipo <> 0) as saca_21,
       count(*) filter (where tipo = 0 and not conf_ok) as saca_22
from todo group by sensor order by sensor""").fetchall()
saca_23 = dict(con.execute("select sensor, count(*) from base semi join fijos using (ci, cj) group by sensor").fetchall())
por_tipo = con.execute("select tipo, count(*) from todo group by tipo order by tipo").fetchall()
por_prov = con.execute("""
select provincia, count(*) as saca,
       count(*) / (select count(*) from base b2 where b2.provincia = b.provincia) as prop
from base b semi join fijos using (ci, cj)
group by provincia order by saca desc limit 8""").fetchall()
top = con.execute("select provincia, lat, lon, dias, primera, ultima from fijos order by dias desc limit 5").fetchall()
nuevos_2026 = con.execute("select count(*) from fijos where primera >= '2026-01-01'").fetchone()[0]
diaynoche = con.execute("select sensor, avg(dia::int) from limpio group by sensor order by sensor").fetchall()
rango = con.execute("select min(fecha), max(fecha) from limpio").fetchone()
cat = con.execute("""select count(*) filter (where provincia = 'Catamarca'),
                 count(*) filter (where provincia = 'Catamarca' and (ci, cj) in (select (ci, cj) from fijos))
                 from base""").fetchone()

nombres_tipo = {0: "vegetación (se queda)", 1: "volcán", 2: "otra fuente fija", 3: "costa afuera"}
L = [
    "# Paso 2: limpiar",
    "",
    f"Generado por `pipeline/paso2_limpiar.py` el {datetime.now():%d/%m/%Y %H:%M}. Datos del {rango[0]:%d/%m/%Y} "
    f"al {rango[1]:%d/%m/%Y}.",
    "",
    "## El embudo",
    "",
    "| Paso | Focos | Saca |",
    "|---|---|---|",
    f"| Todo lo bajado (paso 1) | {miles(n['todo'])} | |",
    f"| 2.1 Tipo vegetación | {miles(n['f21'])} | {miles(n['todo'] - n['f21'])} |",
    f"| 2.2 Confianza suficiente | {miles(n['base'])} | {miles(n['f21'] - n['base'])} |",
    f"| 2.3 Sin fuentes fijas ({miles(n_fijos)} cuadrados) | {miles(n['limpio'])} | {miles(n['base'] - n['limpio'])} |",
    f"| **Quedan** | **{miles(n['limpio'])}** | **{n['limpio'] / n['todo']:.1%} de lo bajado** |",
    "",
    "## Por sensor",
    "",
    "| Sensor | Bajado | Saca 2.1 | Saca 2.2 | Saca 2.3 | De día (lo que queda) |",
    "|---|---|---|---|---|---|",
]
dn = dict(diaynoche)
for s, tot, s21, s22 in por_sensor:
    L.append(f"| {s} | {miles(tot)} | {miles(s21)} | {miles(s22)} | {miles(saca_23.get(s, 0))} | {dn[s]:.0%} |")
L += ["", "## 2.1 Tipos de FIRMS", "", "| Tipo | Qué es | Focos |", "|---|---|---|"]
L += [f"| {t} | {nombres_tipo.get(t, '?')} | {miles(c)} |" for t, c in por_tipo]
L += ["", f"## 2.3 Fuentes fijas: {miles(n_fijos)} cuadrados con VIIRS en {UMBRAL_DIAS} días distintos o más", "",
      "Dónde más saca:", "", "| Provincia | Focos que saca | Proporción de sus focos |", "|---|---|---|"]
L += [f"| {p} | {miles(s)} | {pr:.1%} |" for p, s, pr in por_prov]
L += ["", "Los cinco cuadrados con más días:", "", "| Provincia | Lat | Lon | Días | Primera | Última |",
      "|---|---|---|---|---|---|"]
L += [f"| {p} | {la:.3f} | {lo:.3f} | {d} | {a:%d/%m/%Y} | {b:%d/%m/%Y} |" for p, la, lo, d, a, b in top]
L += ["", f"- Cuadrados cuya primera detección es de 2026: {nuevos_2026}. Por eso el filtro se recalcula con cada "
      "actualización de datos.",
      f"- Catamarca: saca {miles(cat[1])} de {miles(cat[0])} focos ({cat[1] / cat[0]:.1%}).",
      "- Límite conocido: una fuente fija nueva pasa el filtro hasta que acumula 30 días.",
      "", "## Controles", "",
      "- Cada filtro solo saca: el embudo es decreciente.",
      "- `focos_limpios.parquet` tiene exactamente los focos que pasan, y ninguno en un cuadrado fijo."]
(REPORTES / "paso2_limpiar.md").write_text("\n".join(L) + "\n", encoding="utf-8")

print("\n".join(L[6:14]))
print(f"\nGuardado: data/derivados/fuentes_fijas.parquet, data/derivados/focos_limpios.parquet, reportes/paso2_limpiar.md")
