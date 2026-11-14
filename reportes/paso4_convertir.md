# Paso 4: convertir

Generado por `pipeline/paso4_convertir.py` el 14/11/2026 10:31. Modelo: **M2** (elegido en el paso 5, ver `validacion.md`). Ajuste: Aqua contra Suomi NPP, 2012-2022, meses completos.

- Inflación de la varianza de muestreo `c` = 5.82; varianza real entre provincias τ² = 0.017 (día) y 0.068 (noche).
- Dispersión de la binomial negativa, creciente con el tamaño del mes: φ = 1.32·μ^0.56 (día), 2.68·μ^0.28 (noche).
- NOAA-20 → Suomi NPP: k = 0.989 (día), 0.999 (noche).
- M0, un solo número para todo: Suomi NPP ve 3.15 veces más que Aqua.

## Cuántas veces más ve Suomi NPP que Aqua (M2)

| Región | Estación | Día | Noche |
|---|---|---|---|
| Cuyo | DEF | 2.45 | 5.90 |
| Cuyo | JJA | 2.46 | 11.91 |
| Cuyo | MAM | 3.40 | 12.75 |
| Cuyo | SON | 2.42 | 9.17 |
| NEA | DEF | 3.24 | 7.38 |
| NEA | JJA | 2.49 | 12.38 |
| NEA | MAM | 3.07 | 12.85 |
| NEA | SON | 2.60 | 10.28 |
| NOA | DEF | 2.77 | 6.59 |
| NOA | JJA | 2.14 | 10.41 |
| NOA | MAM | 3.32 | 12.69 |
| NOA | SON | 2.26 | 9.42 |
| Pampeana | DEF | 3.04 | 7.99 |
| Pampeana | JJA | 2.74 | 12.97 |
| Pampeana | MAM | 3.40 | 15.49 |
| Pampeana | SON | 3.23 | 11.39 |
| Patagonia | DEF | 2.19 | 5.24 |
| Patagonia | JJA | 2.79 | 13.48 |
| Patagonia | MAM | 2.78 | 12.79 |
| Patagonia | SON | 2.80 | 12.43 |

## Catamarca

| Estación | Momento | Celdas-día Aqua | Celdas-día SNPP | Propio | NOA | M2 | Peso propio |
|---|---|---|---|---|---|---|---|
| DEF | dia | 89 | 453 | 5.07 | 2.77 | 3.09 | 0.18 |
| DEF | noche | 17 | 236 | 13.51 | 6.59 | 7.38 | 0.16 |
| JJA | dia | 754 | 2.047 | 2.71 | 2.14 | 2.48 | 0.62 |
| JJA | noche | 109 | 995 | 9.09 | 10.41 | 9.68 | 0.53 |
| MAM | dia | 61 | 340 | 5.54 | 3.32 | 3.56 | 0.13 |
| MAM | noche | 12 | 147 | 11.80 | 12.69 | 12.59 | 0.12 |
| SON | dia | 985 | 2.804 | 2.85 | 2.26 | 2.65 | 0.69 |
| SON | noche | 163 | 1.515 | 9.27 | 9.42 | 9.32 | 0.63 |

## Serie armonizada del país (celdas-día de Aqua por año)

| Año | Valor | Intervalo 90 % | Origen | Aqua observado | Suma ingenua de todos los satélites |
|---|---|---|---|---|---|
| 2003 | 70.059 | 70.059–70.059 | Aqua observado | 70.059 | 106.455 |
| 2004 | 58.464 | 58.464–58.464 | Aqua observado | 58.464 | 91.110 |
| 2005 | 40.198 | 40.198–40.198 | Aqua observado | 40.198 | 64.323 |
| 2006 | 49.176 | 49.176–49.176 | Aqua observado | 49.176 | 76.680 |
| 2007 | 46.428 | 46.428–46.428 | Aqua observado | 46.428 | 70.883 |
| 2008 | 61.446 | 61.446–61.446 | Aqua observado | 61.446 | 94.793 |
| 2009 | 47.752 | 47.752–47.752 | Aqua observado | 47.752 | 74.519 |
| 2010 | 35.739 | 35.739–35.739 | Aqua observado | 35.739 | 56.895 |
| 2011 | 43.795 | 43.795–43.795 | Aqua observado | 43.795 | 69.853 |
| 2012 | 35.719 | 35.719–35.719 | Aqua observado | 35.719 | 160.395 |
| 2013 | 38.124 | 38.124–38.124 | Aqua observado | 38.124 | 182.571 |
| 2014 | 20.021 | 20.021–20.021 | Aqua observado | 20.021 | 98.239 |
| 2015 | 26.307 | 26.307–26.307 | Aqua observado | 26.307 | 125.441 |
| 2016 | 32.935 | 32.935–32.935 | Aqua observado | 32.935 | 145.764 |
| 2017 | 34.286 | 34.286–34.286 | Aqua observado | 34.286 | 155.820 |
| 2018 | 31.010 | 31.010–31.010 | Aqua observado | 31.010 | 223.084 |
| 2019 | 28.520 | 28.520–28.520 | Aqua observado | 28.520 | 215.892 |
| 2020 | 71.295 | 71.295–71.295 | Aqua observado | 71.295 | 565.185 |
| 2021 | 31.759 | 31.759–31.759 | Aqua observado | 31.759 | 256.710 |
| 2022 | 43.943 | 43.943–43.943 | Aqua observado | 43.943 | 364.501 |
| 2023 | 25.076 | 22.659–27.721 | Suomi NPP convertido | 26.312 | 271.898 |
| 2024 | 24.716 | 22.377–27.230 | Suomi NPP convertido | 29.916 | 291.762 |
| 2025 | 26.736 | 24.122–29.584 | Suomi NPP convertido | 29.980 | 309.302 |
| 2026 | 15.262 | 13.622–17.145 | NOAA-20 convertido | 15.666 | 170.848 |

2026 llega hasta el 14/11: el año está incompleto.

## Controles rápidos

- OK — Un factor para cada estrato, sin vacíos ni infinitos: 192 estratos
- OK — Factores razonables: de día entre 2 y 5; de noche más altos: día 2.00-4.53 (mediana 2.78); noche 4.22-18.04 (mediana 12.23)
- OK — Catamarca queda entre su propio número y el del NOA: DEF dia: 5.1 → 3.1 (NOA 2.8, peso 0.18); DEF noche: 13.5 → 7.4 (NOA 6.6, peso 0.16); JJA dia: 2.7 → 2.5 (NOA 2.1, peso 0.62); JJA noche: 9.1 → 9.7 (NOA 10.4, peso 0.53); MAM dia: 5.5 → 3.6 (NOA 3.3, peso 0.13); MAM noche: 11.8 → 12.6 (NOA 12.7, peso 0.12); SON dia: 2.8 → 2.6 (NOA 2.3, peso 0.69); SON noche: 9.3 → 9.3 (NOA 9.4, peso 0.63)
- OK — 2012-2022: Suomi NPP convertido se parece a Aqua en el total del país: sesgo total -0.3%; por año -6.0% a +4.6%
- OK — 2023-2025, de día: Aqua observado por encima de la conversión (deriva de horario): Aqua 80,757 contra convertido 70,520 (+14.5%)
- OK — Vista previa: cobertura del intervalo del 90 % en 2012-2022 (dentro de muestra): 91.4% de 3,168 provincia-meses
