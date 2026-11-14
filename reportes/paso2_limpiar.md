# Paso 2: limpiar

Generado por `pipeline/paso2_limpiar.py` el 14/11/2026 09:39. Datos del 31/10/2000 al 14/11/2026.

## El embudo

| Paso | Focos | Saca |
|---|---|---|
| Todo lo bajado (paso 1) | 6.635.153 | |
| 2.1 Tipo vegetación | 6.444.377 | 190.776 |
| 2.2 Confianza suficiente | 5.938.844 | 505.533 |
| 2.3 Sin fuentes fijas (1.021 cuadrados) | 5.814.954 | 123.890 |
| **Quedan** | **5.814.954** | **87.6% de lo bajado** |

## Por sensor

| Sensor | Bajado | Saca 2.1 | Saca 2.2 | Saca 2.3 | De día (lo que queda) |
|---|---|---|---|---|---|
| MODIS | 1.737.290 | 33.080 | 77.219 | 8.025 | 86% |
| VIIRS | 4.897.863 | 157.696 | 428.314 | 115.865 | 74% |

## 2.1 Tipos de FIRMS

| Tipo | Qué es | Focos |
|---|---|---|
| 0 | vegetación (se queda) | 6.444.377 |
| 1 | volcán | 4 |
| 2 | otra fuente fija | 175.886 |
| 3 | costa afuera | 14.886 |

## 2.3 Fuentes fijas: 1.021 cuadrados con VIIRS en 30 días distintos o más

Dónde más saca:

| Provincia | Focos que saca | Proporción de sus focos |
|---|---|---|
| Neuquén | 55.768 | 58.2% |
| Buenos Aires | 9.708 | 4.7% |
| Corrientes | 7.172 | 1.1% |
| Formosa | 6.995 | 0.8% |
| Entre Ríos | 6.876 | 2.3% |
| Santa Fe | 6.374 | 0.8% |
| Misiones | 5.690 | 3.2% |
| Mendoza | 4.742 | 4.7% |

Los cinco cuadrados con más días:

| Provincia | Lat | Lon | Días | Primera | Última |
|---|---|---|---|---|---|
| Neuquén | -38.085 | -68.705 | 492 | 31/08/2019 | 12/11/2026 |
| Mendoza | -37.085 | -69.475 | 489 | 04/03/2024 | 14/11/2026 |
| Neuquén | -38.335 | -69.055 | 447 | 05/08/2019 | 02/11/2026 |
| Neuquén | -38.745 | -68.835 | 411 | 22/02/2014 | 14/11/2026 |
| Neuquén | -38.275 | -68.695 | 383 | 06/09/2023 | 10/11/2026 |

- Cuadrados cuya primera detección es de 2026: 6. Por eso el filtro se recalcula con cada actualización de datos.
- Catamarca: saca 401 de 43.879 focos (0.9%).
- Límite conocido: una fuente fija nueva pasa el filtro hasta que acumula 30 días.

## Controles

- Cada filtro solo saca: el embudo es decreciente.
- `focos_limpios.parquet` tiene exactamente los focos que pasan, y ninguno en un cuadrado fijo.
