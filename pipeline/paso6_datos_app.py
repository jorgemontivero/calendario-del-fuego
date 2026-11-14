"""Step 6 - Data for the website: small files the app only reads (it never computes the harmonization).

Input:  data/derivados/serie_armonizada_{provincia,pais,departamento}.parquet, validacion_metricas.json,
        focos_limpios.parquet; data/departamentos.parquet, provincias.parquet
Output: app/datos/serie.parquet       area x month 2003-today: value, 90 % range, normal, p90, rank, status
        app/datos/anual_pais.parquet  national yearly totals: naive sum, Aqua alone, harmonized (Methods chart)
        app/datos/limites.parquet     provinces and departments (simplified) for the map
        app/datos/meta.json           data date, validation numbers

"Normal" (median) and "unusual" (90th percentile) use 2003-2022, the years observed by Aqua (the reference):
from 2023 on, months are estimates with a range, so they are compared against the reference, not part of it.

Usage: python pipeline/paso6_datos_app.py
"""

import json
from pathlib import Path

import duckdb
import geopandas as gpd
import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parents[1]
DERIV = RAIZ / "data" / "derivados"
SAL = RAIZ / "app" / "datos"
SAL.mkdir(parents=True, exist_ok=True)

prov = pd.read_parquet(DERIV / "serie_armonizada_provincia.parquet")
pais = pd.read_parquet(DERIV / "serie_armonizada_pais.parquet")
dep = pd.read_parquet(DERIV / "serie_armonizada_departamento.parquet")
deptos = gpd.read_parquet(RAIZ / "data" / "departamentos.parquet")
provs = gpd.read_parquet(RAIZ / "data" / "provincias.parquet")

ORIGEN = {"Aqua observado": "aqua", "Suomi NPP convertido": "snpp_converted", "NOAA-20 convertido": "noaa20_converted"}


def base(s, nivel, area_cod, area):
    return pd.DataFrame({"nivel": nivel, "area_cod": area_cod, "area": area, "prov_cod": s.prov_cod.values,
                         "anio": s.anio.values, "mes": s.mes.values, "valor": s.valor.values,
                         "min90": np.where(s.origen.values == "Aqua observado", np.nan, s.min90.values),
                         "max90": np.where(s.origen.values == "Aqua observado", np.nan, s.max90.values),
                         "prob_inusual": s.prob_inusual.values, "origen": s.origen.map(ORIGEN).values,
                         "mes_completo": s.mes_completo.astype(bool).values})


partes = [base(prov, "provincia", prov.prov_cod.values, prov.provincia.values),
          base(pais, "pais", "00", "Argentina")]

# departments: zero-filled over every month of the national series (the department table only lists months with fire)
meses = pais[["anio", "mes", "mes_completo", "origen"]].copy()
lista = deptos[["depto_cod", "depto", "prov_cod"]].drop_duplicates()
g = lista.merge(meses, how="cross")
d = g.merge(dep[["depto_cod", "anio", "mes", "valor"]], on=["depto_cod", "anio", "mes"], how="left")
d["valor"] = d.valor.fillna(0.0)
partes.append(pd.DataFrame({"nivel": "departamento", "area_cod": d.depto_cod, "area": d.depto, "prov_cod": d.prov_cod,
                            "anio": d.anio, "mes": d.mes, "valor": d.valor, "min90": np.nan, "max90": np.nan,
                            "prob_inusual": np.nan, "origen": d.origen.map(ORIGEN), "mes_completo": d.mes_completo.astype(bool)}))
s = pd.concat(partes, ignore_index=True)
s = s[s.anio >= 2003]

# normal, p90 and rank, per area and month of the year
ref = s[s.anio.between(2003, 2022)]
norm = ref.groupby(["nivel", "area_cod", "mes"]).valor.agg(normal="median", p90=lambda x: x.quantile(0.9)).reset_index()
s = s.merge(norm, on=["nivel", "area_cod", "mes"], how="left")
comp = s.mes_completo
s.loc[comp, "puesto"] = s[comp].groupby(["nivel", "area_cod", "mes"]).valor.rank(ascending=False, method="min")
s["n_anios"] = s[comp].groupby(["nivel", "area_cod", "mes"]).valor.transform("size")
s["n_anios"] = s.groupby(["nivel", "area_cod", "mes"]).n_anios.transform("max")
# yearly median of the area (2003-2022) to flag small areas
anual_area = ref.groupby(["nivel", "area_cod", "anio"]).valor.sum().groupby(["nivel", "area_cod"]).median().rename("mediana_anual")
s = s.merge(anual_area.reset_index(), on=["nivel", "area_cod"], how="left")


def estado(r):
    """Label of a month. Months converted from VIIRS carry a 90 % range: they are only "above" or "below" normal
    if the whole range is on that side, and "unusual" if the simulated probability of exceeding p90 is >= 50 %."""
    if not r.mes_completo:
        return "en_curso"
    hay_rango = not np.isnan(r.min90)
    if (r.prob_inusual >= 0.5) if hay_rango and not np.isnan(r.prob_inusual) else r.valor > r.p90:
        return "inusual"
    alto, bajo = (r.min90, r.max90) if hay_rango else (r.valor, r.valor)
    if r.normal > 0 and alto > 1.15 * r.normal:
        return "arriba"
    if r.normal == 0 and alto > 0 and not hay_rango:
        return "arriba"
    if bajo < 0.85 * r.normal:
        return "abajo"
    return "normal"


s["estado"] = [estado(r) for r in s[["mes_completo", "valor", "p90", "normal", "min90", "max90", "prob_inusual"]].itertuples()]
for c in ["valor", "min90", "max90"]:
    s[c] = s[c].round(1)
s = s.sort_values(["nivel", "area_cod", "anio", "mes"])
s.to_parquet(SAL / "serie.parquet", index=False)

# Methods chart: naive sum vs Aqua vs harmonized, national, complete years
con = duckdb.connect()
ing = con.execute(f"select anio, count(*) n from '{(DERIV / 'focos_limpios.parquet').as_posix()}' group by 1").df()
an = pais.groupby("anio").agg(armonizada=("valor", "sum"), aqua=("aqua", "sum")).reset_index().merge(
    ing.rename(columns={"n": "ingenua"}), on="anio")
an = an[an.anio.between(2003, 2025)]
an.to_parquet(SAL / "anual_pais.parquet", index=False)

# boundaries, simplified (~1 km tolerance) for a light map
lim = pd.concat([provs.assign(nivel="provincia", area_cod=provs.prov_cod, area=provs.provincia)[["nivel", "area_cod", "area", "prov_cod", "geometry"]],
                 deptos.assign(nivel="departamento", area_cod=deptos.depto_cod, area=deptos.depto)[["nivel", "area_cod", "area", "prov_cod", "geometry"]]])
lim = gpd.GeoDataFrame(lim, geometry="geometry", crs=provs.crs)
# Albers equal-area (South America): fire per 1,000 km2 in the map. Clipped north of 60 S: the Antarctic sector
# makes the area of Tierra del Fuego invalid (and it has no hot spots).
from shapely.geometry import box  # noqa: E402

lim["km2"] = lim.geometry.make_valid().intersection(box(-80, -60, -50, -20)).to_crs("ESRI:102033").area / 1e6
# For drawing, the same clip (the Antarctic sector and the South Atlantic islands made every map of the country fit
# down to the South Pole, leaving mainland Argentina as a thin strip). Malvinas stay (they are north of 56 S).
lim["geometry"] = lim.geometry.make_valid().intersection(box(-75, -56, -53, -21))
lim = lim[~lim.geometry.is_empty]
lim["geometry"] = lim.geometry.simplify(0.01, preserve_topology=True)
lim.to_parquet(SAL / "limites.parquet", index=False)

# "Detected vs reported": burned area that the provinces report to the Ministry of Environment (CIAM).
# dt 510 (1993-2023, the longest table) for 2003-2023; dt 416 (reports 2017-2026) only for the years 510 lacks
# (2024-2025; 2026 is still being loaded). The two tables don't always agree (Catamarca 2017: 45,170 vs 17,385 ha),
# so each value keeps its source. The national value is the sum of the provinces with data, with their count.
OFICIAL = RAIZ / "data" / "oficial"
nom_cod = dict(zip(provs.provincia, provs.prov_cod))
nom_cod.update({"Tierra del Fuego": nom_cod["Tierra del Fuego, Antártida e Islas del Atlántico Sur"],
                "CABA": nom_cod["Ciudad Autónoma de Buenos Aires"]})
o510 = pd.read_csv(OFICIAL / "ciam_dt510.csv", sep=";", na_values=["-", "s/d", ""])
o510.columns = ["anio", "jur", "unidad", "ha", "ha_bosque"]
o510 = o510[o510.anio.between(2003, 2023)].assign(fuente="dt510")
o416 = pd.read_csv(OFICIAL / "ciam_dt416.csv", sep=";", na_values=["-", "s/d", ""])
o416 = o416.melt(id_vars="jurisdicción", var_name="anio", value_name="ha").rename(columns={"jurisdicción": "jur"})
o416["anio"] = o416.anio.str[-4:].astype(int)
o416["ha"] = pd.to_numeric(o416.ha, errors="coerce")
o416 = o416[o416.anio.between(2024, 2025)].assign(fuente="dt416")
of = pd.concat([o510[["jur", "anio", "ha", "fuente"]], o416[["jur", "anio", "ha", "fuente"]]], ignore_index=True)
of = of[of.jur != "Total"]
of["prov_cod"] = of.jur.map(nom_cod)
assert of.prov_cod.notna().all(), of[of.prov_cod.isna()].jur.unique()
of = of.dropna(subset=["ha"])
nac = of.groupby(["anio", "fuente"]).agg(ha=("ha", "sum"), n_prov=("prov_cod", "nunique")).reset_index().assign(prov_cod="00")
of = pd.concat([of.assign(n_prov=1)[["prov_cod", "anio", "ha", "fuente", "n_prov"]], nac[["prov_cod", "anio", "ha", "fuente", "n_prov"]]])
of.to_parquet(SAL / "oficial.parquet", index=False)

# "Now vs before": the harmonized series by DAY, for any date window. Same rule as the monthly series:
# Aqua observed up to 2022; Suomi NPP converted 2023-2025; NOAA-20 (x k) converted 2026, with the step-4 factor of
# the province x season x day/night (the expected value: daily values carry no 90 % range). Departments use their
# province's factor. Country: Aqua counted directly; converted years as the sum of the provinces (as the monthly
# country series). Only days with fire are stored.
ESTACION = {12: "DEF", 1: "DEF", 2: "DEF", 3: "MAM", 4: "MAM", 5: "MAM", 6: "JJA", 7: "JJA", 8: "JJA",
            9: "SON", 10: "SON", 11: "SON"}
fac = pd.read_parquet(DERIV / "factores.parquet")[["prov_cod", "estacion", "momento", "factor_M2", "k_noaa20"]]
lim_sql = (DERIV / "focos_limpios.parquet").as_posix()
diar = con.execute(f"""
select plataforma, fecha, mes, case when dia then 'dia' else 'noche' end momento, prov_cod, depto_cod,
       count(distinct (ci, cj)) n
from '{lim_sql}'
where provincia is not null and ((plataforma = 'Aqua' and anio between 2003 and 2022)
   or (plataforma = 'SNPP' and anio between 2023 and 2025) or (plataforma = 'NOAA20' and anio = 2026))
group by all""").df()
pais_aqua = con.execute(f"""
select fecha, sum(n) n from (
  select fecha, dia, count(distinct (ci, cj)) n from '{lim_sql}'
  where plataforma = 'Aqua' and anio between 2003 and 2022 group by all)
group by 1""").df()  # day and night counted separately, as in the monthly series
diar["estacion"] = diar.mes.map(ESTACION)
diar = diar.merge(fac, on=["prov_cod", "estacion", "momento"], how="left")
conv = diar.plataforma != "Aqua"
diar["valor"] = np.where(conv, diar.n * diar.factor_M2 * np.where(diar.plataforma == "NOAA20", diar.k_noaa20, 1.0),
                         diar.n)
assert diar.loc[conv, "factor_M2"].notna().all()
partes_d = [
    diar.groupby(["prov_cod", "fecha"]).valor.sum().reset_index().rename(columns={"prov_cod": "area_cod"})
        .assign(nivel="provincia"),
    diar.dropna(subset=["depto_cod"]).groupby(["depto_cod", "fecha"]).valor.sum().reset_index()
        .rename(columns={"depto_cod": "area_cod"}).assign(nivel="departamento"),
    pd.concat([pais_aqua.rename(columns={"n": "valor"}),
               diar[conv].groupby("fecha").valor.sum().reset_index()]).assign(area_cod="00", nivel="pais"),
]
dia_df = pd.concat(partes_d, ignore_index=True)
dia_df["fecha"] = pd.to_datetime(dia_df.fecha)
dia_df["valor"] = dia_df.valor.astype("float32").round(2)
dia_df[["nivel", "area_cod", "fecha", "valor"]].sort_values(["nivel", "area_cod", "fecha"]).to_parquet(
    SAL / "diaria.parquet", index=False)
# check: the daily series adds up to the monthly one (country, complete months)
chk = dia_df[dia_df.nivel == "pais"].groupby([dia_df.fecha.dt.year, dia_df.fecha.dt.month]).valor.sum()
mens = pais.set_index(["anio", "mes"]).valor
comun_idx = chk.index.intersection(mens.index)
dif = (chk.loc[comun_idx] / mens.loc[comun_idx] - 1).abs()
print(f"diaria: {len(dia_df):,} filas | diferencia con la serie mensual del país: mediana {dif.median():.2%}, "
      f"máx. Aqua {dif[[a <= 2022 for a, _ in comun_idx]].max():.2%}")

# Climate (NASA POWER, MERRA-2) by province and month, plus Argentina as the mean of the provinces weighted by their
# number of grid points (~ their area). Rain of the 3 and 6 PREVIOUS months (t-n .. t-1) for the "Climate and fire"
# view, as in the preparation's test. Departments use their province (the 0.5 deg grid is coarser than most of them).
cl = pd.read_parquet(RAIZ / "data" / "clima_provincia_mes.parquet")
cl["prov_cod"] = cl.provincia.map(nom_cod)
assert cl.prov_cod.notna().all()
var = ["lluvia_mm", "humedad", "temp_max"]
pesos = cl.puntos
nac_cl = (cl.assign(**{v: cl[v] * pesos for v in var}).groupby(["anio", "mes"])
          .agg(**{v: (v, "sum") for v in var}, puntos=("puntos", "sum"), completo=("completo", "all")).reset_index())
for v in var:
    nac_cl[v] = nac_cl[v] / nac_cl.puntos
cl = pd.concat([cl[["prov_cod", "anio", "mes", *var, "completo"]], nac_cl.assign(prov_cod="00")[["prov_cod", "anio", "mes", *var, "completo"]]])
cl = cl.sort_values(["prov_cod", "anio", "mes"])
for n in (3, 6):
    cl[f"lluvia_prev{n}"] = cl.groupby("prov_cod").lluvia_mm.transform(lambda x: x.shift(1).rolling(n).sum())
cl.to_parquet(SAL / "clima.parquet", index=False)
print("clima:", len(cl), "filas,", cl.prov_cod.nunique(), "áreas,", f"{cl.anio.min()}-{cl.anio.max()}")

fecha = con.execute(f"select max(fecha) from '{(DERIV / 'focos_limpios.parquet').as_posix()}'").fetchone()[0]
meta = {"fecha_datos": str(fecha), "ultimo_mes_completo": None,
        "validacion": json.loads((DERIV / "validacion_metricas.json").read_text(encoding="utf-8"))}
um = pais[pais.mes_completo.astype(bool)].sort_values(["anio", "mes"]).iloc[-1]
meta["ultimo_mes_completo"] = [int(um.anio), int(um.mes)]
(SAL / "meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=1, default=float), encoding="utf-8")

for f in sorted(SAL.iterdir()):
    print(f"{f.name:22s} {f.stat().st_size / 1e6:6.2f} MB")
print("filas serie:", len(s), "| áreas:", s.groupby("nivel").area_cod.nunique().to_dict(), "| datos al", fecha,
      "| último mes completo", meta["ultimo_mes_completo"])
