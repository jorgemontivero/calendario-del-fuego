# Paso 3: contar parejo

Generado por `pipeline/paso3_contar.py` el 14/11/2026 10:07.

## Meses de servicio de cada satélite

| Satélite | Desde | Hasta | Meses |
|---|---|---|---|
| Terra (MODIS) | 01/11/2000 | 13/11/2026 | 313 |
| Aqua (MODIS) | 04/07/2002 | 14/11/2026 | 293 |
| Suomi NPP (VIIRS) | 20/01/2012 | 02/11/2026 | 179 |
| NOAA-20 (VIIRS) | 01/04/2018 | 14/11/2026 | 104 |
| NOAA-21 (VIIRS) | 01/03/2023 | 14/11/2026 | 45 |

Fuera de esas fechas la tabla no tiene filas ("sin dato"). Los meses de entrada, de salida y el mes en curso llevan `mes_completo = False` y `dias_servicio` con los días que cubren.

## 2025, todo el país

| Satélite | Focos | Celdas-día | Focos por celda-día |
|---|---|---|---|
| Aqua (MODIS) | 31.010 | 30.020 | 1.03 |
| NOAA-20 (VIIRS) | 142.960 | 89.791 | 1.59 |
| NOAA-21 (VIIRS) | 137.939 | 88.849 | 1.55 |
| Suomi NPP (VIIRS) | 144.134 | 88.831 | 1.62 |
| Terra (MODIS) | 12.586 | 12.192 | 1.03 |

## Cocientes anuales (celdas-día, meses completos)

| Año | Suomi NPP / Aqua | NOAA-20 / Suomi NPP | NOAA-21 / NOAA-20 |
|---|---|---|---|
| 2012 | 2.84 |  |  |
| 2013 | 3.21 |  |  |
| 2014 | 3.26 |  |  |
| 2015 | 3.22 |  |  |
| 2016 | 2.89 |  |  |
| 2017 | 2.95 |  |  |
| 2018 | 3.18 | 0.78 |  |
| 2019 | 3.00 | 1.01 |  |
| 2020 | 3.22 | 0.99 |  |
| 2021 | 3.24 | 1.02 |  |
| 2022 | 3.34 | 1.03 |  |
| 2023 | 3.16 | 0.98 | 0.80 |
| 2024 | 2.66 | 1.07 | 0.99 |
| 2025 | 2.96 | 1.01 | 0.99 |
| 2026 | 3.24 | 1.05 | 0.95 |

## Catamarca, septiembre de 2026

| Satélite | Momento | Celdas-día |
|---|---|---|
| Aqua (MODIS) | dia | 77 |
| Aqua (MODIS) | noche | 4 |
| NOAA-20 (VIIRS) | dia | 145 |
| NOAA-20 (VIIRS) | noche | 108 |
| NOAA-21 (VIIRS) | dia | 123 |
| NOAA-21 (VIIRS) | noche | 104 |
| Suomi NPP (VIIRS) | dia | 139 |
| Suomi NPP (VIIRS) | noche | 92 |
| Terra (MODIS) | dia | 28 |
| Terra (MODIS) | noche | 35 |

Meses más altos de Catamarca con NOAA-20 (día + noche): 08/2020: 502; 09/2026: 253; 10/2021: 247

## Tablas

| Tabla | Filas | Con fuego |
|---|---|---|
| `conteo_provincia.parquet` | 44.832 | 34.844 |
| `conteo_departamento.parquet` | 976.964 | 293.414 |
| `conteo_pais.parquet` | 1.868 | 1.867 |

## Controles

- OK — Nada se pierde al completar (provincia): 4,332,997 contadas - 22 de Terra 31/10/2000 = 4,332,975 en la tabla
- OK — Nada se pierde al completar (departamento): 4,341,649 contadas - 22 de Terra 31/10/2000 = 4,341,627 en la tabla
- OK — Nada se pierde al completar (pais): 4,340,323 contadas - 22 de Terra 31/10/2000 = 4,340,301 en la tabla
- OK — Las 24 provincias: 24
- OK — Sin huecos: cada provincia tiene todos los meses de servicio de cada satélite: 0 combinaciones incompletas
- OK — Sin ceros de más: NOAA-20 no aparece antes de abril de 2018: 0 filas
- OK — Focos por celda-día 2025: MODIS cerca de 1, VIIRS entre 1,4 y 2: Aqua 1.03, NOAA20 1.59, NOAA21 1.55, SNPP 1.62, Terra 1.03
- OK — Suomi NPP / Aqua estable, cerca de 3, en 2013-2022: 2.89 a 3.34
- OK — NOAA-20 / Suomi NPP cerca de 1 desde 2019: 0.98 a 1.07
- OK — NOAA-21 / NOAA-20 cerca de 1 (2024-2025): 0.99 a 0.99
- OK — Suma de provincias vs. país contado directo: diferencia chica: -0.17%
