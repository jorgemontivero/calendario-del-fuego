# Validación (paso 5)

Generado por `pipeline/paso5_comprobar.py` el 14/11/2026 10:54. Criterios de aprobación fijados antes de correr las pruebas (presentacion/paso5_comprobar.pdf).

## Resultado

| Prueba | Resultado |
|---|---|
| a) El examen (aprender 2012-2018, probar 2019-2022) | APRUEBA: modelo elegido **M2** |
| b) Sin escalones y misma dirección que Aqua | APRUEBA |
| c) Fuente oficial (superficie incendiada, Ministerio de Ambiente) | APRUEBA EN PARTE: rankings sí; tendencia nacional no (la oficial es plana; ver el detalle por provincia) |

## a) El examen

Se aprende con 2012-2018 y se convierte Suomi NPP 2019-2022 (incluye 2020, año extremo). Se compara con lo que Aqua vio de verdad. Unidad: provincia × mes, día + noche.

| Modelo | Error total | De día | De noche | Peor región | Error típico (A ≥ 10) | Error típico, 12 provincias chicas | Acierto del margen 90 % | Catamarca dentro | Catamarca escondida |
|---|---|---|---|---|---|---|---|---|---|
| M0 | +3.6% | -13.0% | +221.3% | 16.5% | 21.7% | 20.6% | 93.2% | 20.4% | 22.5% |
| M1 | -1.1% | -1.7% | +6.3% | 7.4% | 19.5% | 22.4% | 86.5% | 25.5% | — |
| M2 ← | -1.6% | -1.4% | -4.5% | 7.0% | 18.7% | 21.4% | 86.5% | 19.6% | 27.8% |
| M3 | +14.1% | +15.4% | -2.9% | 20.3% | 24.1% | 27.4% | 88.1% | 31.1% | 20.9% |

- Error total: suma convertida / suma de Aqua − 1. Error típico: mediana de |convertido − Aqua| / Aqua en los provincia-meses con 10 o más celdas-día de Aqua. Acierto del margen: proporción de provincia-meses en que Aqua cae dentro del intervalo del 90 % (aprueba entre 85 % y 95 %).
- Catamarca escondida: se ajusta sin Catamarca y se la predice con el valor de su región (M2), el nacional (M0) o el efecto poblacional (M3). M1 no puede predecir una provincia que no vio.
- Regla de elección (escrita antes): margen entre 85 % y 95 % y error total menor que 5 %; entre esos, el menor error típico en las provincias chicas; y tiene que ganarle a M0. **Elegido: M2.** Se vuelve a ajustar con 2012-2022 para la serie final.

## b) Sin escalones

Cociente contra Aqua, año por año (tiene que ser plano, cerca de 1):

| Año | Suomi NPP convertido / Aqua | NOAA-20 convertido / Aqua | Serie ingenua / Aqua |
|---|---|---|---|
| 2003 |  |  | 1.6 |
| 2004 |  |  | 1.6 |
| 2005 |  |  | 1.7 |
| 2006 |  |  | 1.6 |
| 2007 |  |  | 1.6 |
| 2008 |  |  | 1.6 |
| 2009 |  |  | 1.6 |
| 2010 |  |  | 1.7 |
| 2011 |  |  | 1.7 |
| 2012 | 0.94 |  | 6.3 |
| 2013 | 1.00 |  | 7.1 |
| 2014 | 1.04 |  | 7.0 |
| 2015 | 1.05 |  | 6.7 |
| 2016 | 0.97 |  | 6.5 |
| 2017 | 0.99 |  | 6.8 |
| 2018 | 1.02 |  | 10.5 |
| 2019 | 1.01 | 1.01 | 11.2 |
| 2020 | 0.99 | 0.98 | 12.5 |
| 2021 | 1.03 | 1.04 | 12.1 |
| 2022 | 0.97 | 0.99 | 13.6 |

Tendencia (logaritmo de los totales anuales):

| Serie | Año del cambio (Pettitt) | Cambio de nivel | p | Mann-Kendall z | p |
|---|---|---|---|---|---|
| Aqua solo (2003-2022) | 2010 | -34% | 0.044 | -2.56 | 0.010 |
| Armonizada (2003-2025) | 2012 | -35% | 0.018 | -3.43 | 0.001 |
| Ingenua: todos los focos sumados (2003-2025) | 2012 | +305% | 0.001 | +4.44 | 0.000 |

- Control 2023-2025: ver `reportes/paso4_convertir.md` (Aqua observado de día queda por encima de la conversión: es la huella de su cambio de horario).

## c) Contra la fuente oficial

Superficie incendiada por provincia y año, 2003-2023 (CIAM, dt 510; 492 provincia-años con dato). Se comparan rankings (Spearman), no valores: hectáreas y celdas-día miden cosas distintas.

| Serie | Spearman, todos los provincia-años | Mediana dentro de cada provincia (ranking de años) |
|---|---|---|
| Aqua solo | 0.35 | 0.47 (24 provincias) |
| Armonizada | 0.35 | 0.48 (24 provincias) |
| Ingenua (todos los focos) | 0.32 | 0.12 (24 provincias) |

Tendencia 2003-2023 en las 15 provincias con dato todos los años (Buenos Aires, Catamarca, Chubut, Córdoba, Entre Ríos, Jujuy, La Pampa, La Rioja, Mendoza, Misiones, Río Negro, Salta, San Juan, Santa Fe, Tierra del Fuego, Antártida e Islas del Atlántico Sur):

| Serie | Mann-Kendall z | p |
|---|---|---|
| Superficie oficial | +0.39 | 0.695 |
| Armonizada | -2.99 | 0.003 |
| Ingenua | +3.96 | 0.000 |

La suma oficial nacional no tiene tendencia, y el criterio fijado ("va para el mismo lado que la armonizada") **no se cumple**. Pero la suma la dominan La Pampa, Buenos Aires y Córdoba (mediana 44% del total), con años de pastizal enormes. Provincia por provincia (Kendall τ contra el año, provincias con 15 años o más de dato):

| Provincia | Años | τ oficial | p | τ armonizada | τ ingenua |
|---|---|---|---|---|---|
| Buenos Aires | 21 | -0.20 | 0.22 | -0.43 | +0.69 |
| Catamarca | 21 | +0.10 | 0.53 | -0.32 | +0.58 |
| Chaco | 20 | -0.21 | 0.21 | -0.44 | +0.60 |
| Chubut | 21 | -0.22 | 0.18 | +0.20 | +0.53 |
| Ciudad Autónoma de Buenos Aires | 19 | -0.36 | 0.04 | -0.05 | +0.49 |
| Corrientes | 20 | +0.06 | 0.72 | -0.22 | +0.65 |
| Córdoba | 21 | +0.03 | 0.88 | -0.42 | +0.45 |
| Entre Ríos | 21 | +0.25 | 0.12 | -0.05 | +0.43 |
| Formosa | 20 | +0.06 | 0.72 | +0.20 | +0.72 |
| Jujuy | 21 | +0.10 | 0.57 | -0.34 | +0.65 |
| La Pampa | 21 | +0.03 | 0.88 | +0.05 | +0.45 |
| La Rioja | 21 | -0.09 | 0.61 | +0.16 | +0.64 |
| Mendoza | 21 | -0.04 | 0.83 | -0.09 | +0.68 |
| Misiones | 21 | -0.20 | 0.22 | -0.67 | +0.52 |
| Neuquén | 20 | -0.18 | 0.29 | -0.25 | +0.55 |
| Río Negro | 21 | -0.50 | 0.00 | +0.11 | +0.47 |
| Salta | 21 | -0.37 | 0.02 | -0.43 | +0.69 |
| San Juan | 21 | +0.09 | 0.61 | -0.39 | +0.64 |
| San Luis | 20 | +0.23 | 0.16 | -0.18 | +0.58 |
| Santa Cruz | 20 | -0.31 | 0.06 | -0.07 | +0.63 |
| Santa Fe | 21 | -0.53 | 0.00 | -0.28 | +0.63 |
| Santiago del Estero | 20 | -0.19 | 0.26 | -0.59 | +0.63 |
| Tierra del Fuego, Antártida e Islas del Atlántico Sur | 21 | +0.13 | 0.40 | -0.02 | +0.48 |
| Tucumán | 18 | +0.08 | 0.65 | -0.36 | +0.62 |

**De las 5 provincias con tendencia oficial clara (p < 0,10), todas bajan; la armonizada coincide en 4 y la ingenua en 0.** La fuente oficial no confirma una baja nacional, pero desmiente el aumento de la serie ingenua.

Años récord:

| Provincia | Año | Puesto en la armonizada (2003-2025) | Puesto en la superficie oficial (2003-2023) |
|---|---|---|---|
| Córdoba | 2020 | 2 de 23 | 1 de 21 |
| Corrientes | 2022 | 2 de 23 | 1 de 20 |
| Entre Ríos | 2020 | 2 de 23 | 1 de 21 |

Estacionalidad: incendios reportados por mes (dt 427, 2017-2025) contra el promedio mensual armonizado: Spearman 0.97. Meses pico, oficial: [8, 9, 10]; armonizada: [8, 9, 10].
- Jurisdicciones de la tabla oficial que no son provincias (quedan afuera): ninguna.
- Cuidados: hay provincias y años sin dato, el esfuerzo de registro cambia entre provincias, y dos tablas oficiales no coinciden entre sí (Catamarca 2017: 45.170 ha en dt 510 y 17.385 en dt 416). Se usa la más larga (dt 510).

## Catamarca, septiembre de 2026

- Serie armonizada (NOAA-20 convertido): **64** celdas-día de Aqua (intervalo 90 %: 39–99).
- Septiembres 2003-2022: mediana 58, percentil 90 92, máximo 164 (2003); 6 de 20 fueron más altos.
- Probabilidad de mes inusual: **9%**. No es un récord: es un septiembre típico en la serie larga.
- Departamentos con más celdas-día (NOAA-20): La Paz 72 (01/09–30/09); Andalgalá 52 (16/09–29/09); Capayán 40 (01/09–27/09); Santa Rosa 26 (02/09–24/09); El Alto 10 (01/09–17/09).
- La Paz (VIIRS): 569 focos en 73 cuadrados distintos y 16 días; el cuadrado que más se repite tuvo 6 días; los focos ocupan unos 95 × 36 km. Ningún cuadrado se acerca a los 30 días que definen una fuente fija y los focos están repartidos en 73 cuadrados: es fuego que se mueve, no una instalación. No aparece en la prensa: puede ser quema agrícola o de pastizal.
