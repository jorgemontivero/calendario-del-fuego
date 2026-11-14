"""Step 7 - open data: the tables behind the app, as plain CSV files with a dictionary, in datos_abiertos/.
Run after step 6:  python pipeline/paso7_datos_abiertos.py
Small tables go as .csv; the two big ones (departments, daily) as a .csv inside a .zip, which Windows, macOS and
pandas (pd.read_csv("x.zip")) open directly. Column names are in English so the files work anywhere."""

import json
import zipfile
from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parents[1]
APP, DER, SAL = RAIZ / "app" / "datos", RAIZ / "data" / "derivados", RAIZ / "datos_abiertos"
SAL.mkdir(exist_ok=True)
meta = json.loads((APP / "meta.json").read_text(encoding="utf-8"))
indice = []


def guardar(df: pd.DataFrame, nombre: str, es: str, en: str, comprimir: bool = False):
    """Write the table and note it in the index the app's page reads."""
    if comprimir:
        archivo = f"{nombre}.zip"
        with zipfile.ZipFile(SAL / archivo, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
            z.writestr(f"{nombre}.csv", df.to_csv(index=False, float_format="%.6g"))
    else:
        archivo = f"{nombre}.csv"
        df.to_csv(SAL / archivo, index=False, float_format="%.6g", encoding="utf-8")
    indice.append(dict(archivo=archivo, filas=len(df), kb=round((SAL / archivo).stat().st_size / 1024),
                       columnas=list(df.columns), es=es, en=en))
    print(f"{archivo:38s} {len(df):>8,d} rows {indice[-1]['kb']:>6,d} KB")


s = pd.read_parquet(APP / "serie.parquet")
ORIGEN = {"aqua": "aqua_observed", "snpp_converted": "snpp_converted", "noaa20_converted": "noaa20_converted"}
s["source"] = s.origen.map(ORIGEN)
s["complete_month"] = s.mes_completo.astype(int)
s["unusual"] = (s.estado == "inusual").astype(int)

# 1. monthly, country and provinces (with the 90 % range of converted months)
pp = s[s.nivel.isin(["pais", "provincia"])].sort_values(["nivel", "area_cod", "anio", "mes"])
guardar(pd.DataFrame({
    "level": pp.nivel.map({"pais": "country", "provincia": "province"}), "area_code": pp.area_cod, "area": pp["area"],
    "year": pp.anio, "month": pp.mes, "hotspots": pp.valor, "lo90": pp.min90, "hi90": pp.max90,
    "median_month": pp.normal, "p90_month": pp.p90, "rank": pp.puesto, "n_years": pp.n_anios,
    "prob_unusual": pp.prob_inusual, "unusual": pp.unusual, "complete_month": pp.complete_month, "source": pp.source}),
    "serie_mensual_pais_provincias",
    "Serie armonizada por mes, total país y 24 provincias, 2003 a hoy, con margen del 90 % y comparación con lo normal.",
    "Harmonized monthly series, country total and 24 provinces, 2003 to date, with 90 % range and comparison with normal.")

# 2. monthly, departments (no range yet: they use their province's factor)
dp = s[s.nivel == "departamento"].sort_values(["area_cod", "anio", "mes"])
nom_prov = s[s.nivel == "provincia"].drop_duplicates("area_cod").set_index("area_cod")["area"]
guardar(pd.DataFrame({
    "province_code": dp.prov_cod, "province": dp.prov_cod.map(nom_prov), "department_code": dp.area_cod,
    "department": dp["area"], "year": dp.anio, "month": dp.mes, "hotspots": dp.valor, "median_month": dp.normal,
    "complete_month": dp.complete_month, "source": dp.source}),
    "serie_mensual_departamentos",
    "Serie armonizada por mes y departamento (códigos del IGN), 2003 a hoy. Sin margen: usan el factor de su provincia.",
    "Harmonized monthly series by department (IGN codes), 2003 to date. No range: they use their province's factor.",
    comprimir=True)

# 3. daily (only days with at least one hot spot; missing days are zeros)
di = pd.read_parquet(APP / "diaria.parquet").sort_values(["nivel", "area_cod", "fecha"])
guardar(pd.DataFrame({
    "level": di.nivel.map({"pais": "country", "provincia": "province", "departamento": "department"}),
    "area_code": di.area_cod, "date": pd.to_datetime(di.fecha).dt.strftime("%Y-%m-%d"), "hotspots": di.valor}),
    "serie_diaria",
    "Serie armonizada por día, para país, provincias y departamentos. Solo figuran los días con focos; el resto es cero.",
    "Harmonized daily series for country, provinces and departments. Only days with hot spots are listed; the rest are zero.",
    comprimir=True)

# 4. conversion factors (step 4)
f = pd.read_parquet(DER / "factores.parquet")
guardar(pd.DataFrame({
    "province_code": f.prov_cod, "province": f.provincia, "region": f.region, "season": f.estacion,
    "day_night": f.momento.map({"dia": "day", "noche": "night"}).fillna(f.momento),
    "aqua_cell_days": f.A, "snpp_cell_days": f.V, "factor": f.factor_M2, "viirs_per_modis": f.veces_M2,
    "weight_own_data": f.w, "viirs_per_modis_province_only": f.veces_propio, "viirs_per_modis_region": f.veces_region,
    "noaa20_to_snpp": f.k_noaa20, "model": f.modelo}),
    "factores_conversion",
    "Factores para llevar VIIRS a equivalente MODIS (Aqua), por provincia, estación y día o noche.",
    "Factors that take VIIRS to MODIS (Aqua) equivalent, by province, season and day or night.")

# 5. climate (NASA POWER), provinces and country
c = pd.read_parquet(APP / "clima.parquet").sort_values(["prov_cod", "anio", "mes"])
guardar(pd.DataFrame({
    "area_code": c.prov_cod, "area": c.prov_cod.map(nom_prov).fillna("Argentina"), "year": c.anio, "month": c.mes,
    "rain_mm": c.lluvia_mm, "humidity_pct": c.humedad, "tmax_c": c.temp_max, "rain_prev3_mm": c.lluvia_prev3,
    "rain_prev6_mm": c.lluvia_prev6, "complete_month": c.completo.astype(int)}),
    "clima_mensual",
    "Lluvia, humedad y temperatura máxima por mes (NASA POWER), por provincia y total país.",
    "Monthly rain, humidity and maximum temperature (NASA POWER), by province and country total.")

# 6. naive sum against the harmonized series (the chart that opens the Methodology page)
a = pd.read_parquet(APP / "anual_pais.parquet")
guardar(a.rename(columns={"anio": "year", "armonizada": "harmonized", "aqua": "aqua_only", "ingenua": "all_sensors_summed"}),
        "anual_pais_comparacion",
        "Total anual del país de tres maneras: serie armonizada, Aqua solo y la suma de todos los sensores.",
        "Country yearly total three ways: harmonized series, Aqua only and the sum of all sensors.")

(SAL / "indice.json").write_text(json.dumps(dict(fecha_datos=meta["fecha_datos"], archivos=indice), ensure_ascii=False,
                                            indent=1), encoding="utf-8")
print("indice.json")
