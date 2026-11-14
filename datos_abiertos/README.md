# Datos abiertos · Calendario del Fuego

Las tablas que usa la aplicación, en CSV (UTF-8, separador coma, punto decimal). Los dos archivos grandes vienen como
un CSV dentro de un `.zip`: se abren con doble clic, o directo con `pandas.read_csv("archivo.zip")`.
Los genera `pipeline/paso7_datos_abiertos.py`. *English version: [README.en.md](README.en.md).*

**Unidad.** `hotspots` son **focos equivalentes MODIS**: celdas-día (un cuadrado de 1 km con al menos un foco en un
día) llevadas a lo que habría visto el satélite Aqua. No son incendios ni hectáreas. Los meses convertidos desde VIIRS
son estimaciones y pueden tener decimales.

**Lo normal.** Es la mediana de ese mes en 2003–2022, los años observados por Aqua.

## Archivos

### `serie_mensual_pais_provincias.csv`
Una fila por área, año y mes. Total país y 24 provincias, desde 2003.

| Columna | Qué es |
|---|---|
| `level` | `country` o `province` |
| `area_code` | Código de provincia del INDEC/IGN (2 dígitos); `00` es el país |
| `area` | Nombre |
| `year`, `month` | Año y mes |
| `hotspots` | Focos equivalentes MODIS del mes |
| `lo90`, `hi90` | Margen del 90 % (solo meses convertidos desde VIIRS; vacío en los observados por Aqua) |
| `median_month` | Lo normal para ese mes (mediana 2003–2022) |
| `p90_month` | Percentil 90 de ese mes en 2003–2022: por encima, el mes es inusual |
| `rank` | Puesto del mes entre todos los años (1 = el más alto) |
| `n_years` | Cuántos años se comparan en `rank` |
| `prob_unusual` | Probabilidad de que el mes supere el percentil 90, dado el margen (meses convertidos) |
| `unusual` | 1 si el mes se clasifica como inusual |
| `complete_month` | 0 si el mes está en curso (no comparar con lo normal) |
| `source` | `aqua_observed` (2003–2022), `snpp_converted` (2023–2025) o `noaa20_converted` (2026) |

### `serie_mensual_departamentos.zip`
Igual que la anterior, por departamento. Sin margen ni puesto: los departamentos usan el factor de su provincia.

| Columna | Qué es |
|---|---|
| `province_code`, `province` | Provincia |
| `department_code`, `department` | Código (5 dígitos) y nombre del departamento según el IGN |
| `year`, `month`, `hotspots`, `median_month`, `complete_month`, `source` | Como arriba |

### `serie_diaria.zip`
Serie armonizada por día. **Solo figuran los días con focos**: un día que no aparece vale cero.

| Columna | Qué es |
|---|---|
| `level` | `country`, `province` o `department` |
| `area_code` | `00`, código de provincia o código de departamento |
| `date` | Fecha (AAAA-MM-DD). El último día puede estar incompleto |
| `hotspots` | Focos equivalentes MODIS del día |

### `factores_conversion.csv`
Los factores del paso 4: cuántas celdas-día de Aqua corresponden a una de Suomi NPP, por provincia, estación y día o
noche. Se aprendieron con 2012–2022.

| Columna | Qué es |
|---|---|
| `province_code`, `province`, `region` | Provincia y región a la que se apoya cuando tiene pocos datos |
| `season` | Trimestre: `DEF` (dic–feb), `MAM`, `JJA`, `SON` |
| `day_night` | `day` o `night` |
| `aqua_cell_days`, `snpp_cell_days` | Celdas-día de cada satélite en el período de aprendizaje |
| `factor` | Factor usado: equivalente MODIS = celdas-día de VIIRS × `factor` |
| `viirs_per_modis` | Su inverso: cuántas veces más ve VIIRS |
| `weight_own_data` | Peso (0 a 1) de los datos propios de la provincia frente a su región |
| `viirs_per_modis_province_only`, `viirs_per_modis_region` | El cociente con datos solo de la provincia y el de la región |
| `noaa20_to_snpp` | Cociente para llevar NOAA-20 a Suomi NPP antes de aplicar el factor |
| `model` | Modelo elegido en la validación |

### `clima_mensual.csv`
Clima por provincia y total país (NASA POWER, reanálisis MERRA-2; promedio de los puntos de grilla del área).

| Columna | Qué es |
|---|---|
| `area_code`, `area`, `year`, `month` | Área y mes |
| `rain_mm` | Lluvia del mes (mm) |
| `humidity_pct` | Humedad relativa media a 2 m (%) |
| `tmax_c` | Temperatura máxima del mes: la más alta del mes (°C), promediada entre los puntos del área |
| `rain_prev3_mm`, `rain_prev6_mm` | Lluvia acumulada de los 3 y 6 meses **anteriores** |
| `complete_month` | 0 si el mes está en curso |

### `anual_pais_comparacion.csv`
El total anual del país de tres maneras, para ver por qué hay que armonizar.

| Columna | Qué es |
|---|---|
| `year` | Año (completos) |
| `harmonized` | Serie armonizada |
| `aqua_only` | Aqua solo, sin convertir (desde 2023 pasa más tarde y deja de ser comparable) |
| `all_sensors_summed` | Todos los focos de todos los satélites, sumados tal cual |

## Uso y cita
Datos de libre uso citando la fuente. Los datos de origen son de NASA FIRMS y NASA POWER (uso libre), límites del
Instituto Geográfico Nacional (CC BY 4.0).

> Calendario del Fuego (2026). Serie armonizada de focos de calor MODIS-VIIRS para la Argentina.
> NASA Space Apps Challenge 2026. https://github.com/jorgemontivero/calendario-del-fuego

No es un sistema de alerta. Este proyecto usa datos de la NASA, pero no está respaldado por la NASA.
