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
lim["geometry"] = lim.geometry.simplify(0.01, preserve_topology=True)
lim.to_parquet(SAL / "limites.parquet", index=False)

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
