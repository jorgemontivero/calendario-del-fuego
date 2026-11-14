# Paso 2: limpiar

Generado por `pipeline/paso2_limpiar.py` el 14/11/2026 10:04. Datos del 31/10/2000 al 14/11/2026.

## El embudo

| Paso | Focos | Saca |
|---|---|---|
| Todo lo bajado (paso 1) | 7.082.002 | |
| 2.1 Tipo vegetación | 6.870.244 | 211.758 |
| 2.2 Confianza suficiente | 6.323.124 | 547.120 |
| 2.3 Sin fuentes fijas (974 cuadrados) | 6.190.465 | 132.659 |
| **Quedan** | **6.190.465** | **87.4% de lo bajado** |

## Por sensor

| Sensor | Bajado | Saca 2.1 | Saca 2.2 | Saca 2.3 | De día (lo que queda) |
|---|---|---|---|---|---|
| MODIS | 1.737.290 | 33.080 | 77.219 | 7.688 | 86% |
| VIIRS | 5.344.712 | 178.678 | 469.901 | 124.971 | 74% |

## 2.1 Tipos de FIRMS

| Tipo | Qué es | Focos |
|---|---|---|
| 0 | vegetación (se queda) | 6.870.244 |
| 1 | volcán | 4 |
| 2 | otra fuente fija | 195.857 |
| 3 | costa afuera | 15.897 |

## 2.3 Fuentes fijas: 974 cuadrados con VIIRS (Suomi NPP o NOAA-20) en 30 días distintos o más

Dónde más saca:

| Provincia | Focos que saca | Proporción de sus focos |
|---|---|---|
| Neuquén | 60.485 | 57.3% |
| Buenos Aires | 10.407 | 4.8% |
| Corrientes | 7.750 | 1.1% |
| Entre Ríos | 7.295 | 2.3% |
| Formosa | 7.154 | 0.8% |
| Santa Fe | 6.145 | 0.7% |
| Misiones | 5.886 | 3.1% |
| Mendoza | 5.474 | 5.1% |

Los cinco cuadrados con más días:

| Provincia | Lat | Lon | Días | Primera | Última |
|---|---|---|---|---|---|
| Neuquén | -38.085 | -68.705 | 484 | 31/08/2019 | 12/11/2026 |
| Mendoza | -37.085 | -69.475 | 482 | 04/03/2024 | 14/11/2026 |
| Neuquén | -38.335 | -69.055 | 445 | 05/08/2019 | 02/11/2026 |
| Neuquén | -38.745 | -68.835 | 400 | 22/02/2014 | 13/11/2026 |
| Neuquén | -38.275 | -68.695 | 373 | 06/09/2023 | 10/11/2026 |

- Cuadrados cuya primera detección es de 2026: 5. Por eso el filtro se recalcula con cada actualización de datos.
- Catamarca: saca 395 de 46.035 focos (0.9%).
- Límite conocido: una fuente fija nueva pasa el filtro hasta que acumula 30 días.

## Controles

- Cada filtro solo saca: el embudo es decreciente.
- `focos_limpios.parquet` tiene exactamente los focos que pasan, y ninguno en un cuadrado fijo.
