# Calendario del Fuego — Fire Calendar

**NASA Space Apps Challenge 2026 · Catamarca, Argentina**
Challenge: *Harmonization of MODIS and VIIRS Hot Spots*

Adding up every NASA FIRMS hot spot makes fire in Argentina look like it quadrupled since 2012. Following one
consistent sensor, it fell. The jump comes from new satellites (VIIRS on Suomi NPP, NOAA-20 and NOAA-21), not
from more fire. This project harmonizes MODIS and VIIRS into one comparable series (MODIS-equivalent units) and
shows it as a fire calendar (year × month) for any province or department since 2003.

> Work in progress during the hackathon (14–15 November 2026).

## Pipeline

| Step | Script | Output |
|---|---|---|
| 1. Gather | (data prepared before the event, see *Data*) | `data/focos.parquet` |
| 2. Clean | `pipeline/paso2_limpiar.py` | `data/derivados/focos_limpios.parquet`, `fuentes_fijas.parquet`, `reportes/paso2_limpiar.md` |
| 3. Count evenly | `pipeline/paso3_contar.py` | `data/derivados/conteo_{provincia,pais,departamento}.parquet`, `servicio_satelites.csv`, `reportes/paso3_contar.md` |
| 4. Convert | `pipeline/paso4_convertir.py`, `pipeline/modelo.py` | `data/derivados/serie_armonizada_{provincia,pais,departamento}.parquet`, `factores.parquet`, `reportes/paso4_convertir.md` |
| 5. Validate | *to do* | out-of-sample test and comparison with official statistics |
| App | *to do* | Streamlit app |

Step 2 keeps vegetation fires only: FIRMS type 0, enough confidence (MODIS ≥ 30, VIIRS nominal/high), and no
persistent heat sources (≈1 km cells where VIIRS saw heat on 30 or more distinct days: gas flares, industry).
The day count uses a fixed pair of satellites (Suomi NPP and NOAA-20), so the rule does not change when a new
satellite is added.

Step 3 counts **cell-days**: a ~1 km cell (0.01°) with at least one hot spot on a (local) date, per satellite and
separately for day and night. Satellites are never added together. Months a satellite was flying with no fire are 0;
months outside its service period are absent (no data). This removes the pixel-size effect (VIIRS sees ~1.6 hot
spots per cell-day, MODIS ~1.0) and repeated detections, leaving a stable VIIRS/MODIS ratio (~3) to convert in step 4.

Step 4 expresses everything in **Aqua cell-days**: Aqua observed for 2003–2022; Suomi NPP converted for 2023–2025
(Aqua's overpass drifted later from 2023); NOAA-20 converted for 2026. The conversion is learned on 2012–2022, when
Aqua and Suomi NPP flew at the same hour, per province × season × day/night, with small provinces shrunk toward
their INDEC region (empirical Bayes, DerSimonian–Laird). Each converted month has a 90 % interval (1,000 simulations:
factor uncertainty + negative binomial noise whose dispersion grows with month size) and a probability of being
unusual (above the 2003–2022 90th percentile for that month).

## Data

The data files are not in git (too large). Put them in `data/`:

| File | Source |
|---|---|
| `focos.parquet` | NASA FIRMS: MODIS Collection 6.1 (Terra, Aqua) and VIIRS 375 m (Suomi NPP, NOAA-20, NOAA-21), Argentina, 2000–2026. Annual country files up to 2025; FIRMS area API for 2026 and for NOAA-21 since March 2023 (FIRMS has no NOAA-21 country files) |
| `provincias.parquet`, `departamentos.parquet` | Instituto Geográfico Nacional (IGN), Argentina |
| `clima_provincia_mes.parquet`, `clima_grilla_mes.parquet` | NASA POWER (MERRA-2), monthly rainfall, maximum temperature and relative humidity |
| `estimaciones_agricolas.parquet` | Ministerio de Agricultura, Ganadería y Pesca, Estimaciones Agrícolas |
| `cobertura_provincia_anio.parquet` | MapBiomas Argentina, Collection 3 (CC BY 4.0) |

## Run

```
uv venv .venv
uv pip install -r requirements.txt
.venv/Scripts/python pipeline/paso2_limpiar.py
.venv/Scripts/python pipeline/paso3_contar.py
.venv/Scripts/python pipeline/paso4_convertir.py
```

## License

Code: MIT. Data: each source keeps its own terms (see *Data*).
