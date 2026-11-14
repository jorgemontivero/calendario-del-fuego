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
| 3. Count evenly | *to do* | 1 km cell-days by province and month |
| 4. Convert | *to do* | VIIRS → MODIS-equivalent, hierarchical model |
| 5. Validate | *to do* | out-of-sample test and comparison with official statistics |
| App | *to do* | Streamlit app |

Step 2 keeps vegetation fires only: FIRMS type 0, enough confidence (MODIS ≥ 30, VIIRS nominal/high), and no
persistent heat sources (≈1 km cells where VIIRS saw heat on 30 or more distinct days: gas flares, industry).
The day count uses a fixed pair of satellites (Suomi NPP and NOAA-20), so the rule does not change when a new
satellite is added.

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
```

## License

Code: MIT. Data: each source keeps its own terms (see *Data*).
