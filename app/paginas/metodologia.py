"""Methods: from simple to technical, with the validation results (step 5)."""

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from comun import CONFIG_GRAFICO, AZUL, NARANJA, anual_pais, cabecera, meta, num, pie, t, tr

cabecera()
st.title(tr("Metodología", "Methods"))

st.caption(tr("Qué es un foco de calor y cómo se leen los gráficos: sección **Ayuda**.",
              "What a hot spot is and how to read the charts: **Help** section."))

# ------------------------------------------------------------------------------------------------ why
st.header(tr("¿Por qué hay que armonizar?", "Why harmonize?"))
st.markdown(tr(
    "Desde 2003 los focos de la Argentina vienen de dos instrumentos MODIS, en los satélites Terra y Aqua. Desde "
    "2012 se sumaron los VIIRS (Suomi NPP, NOAA-20 desde 2018 y NOAA-21 desde 2023), que miran con más detalle "
    "(píxeles de 375 m en vez de 1 km) y ven fuegos más chicos. **Cada satélite nuevo hace que FIRMS publique más "
    "focos, aunque no haya más fuego.** Sumados tal cual, parece que el fuego se multiplicó; con un solo "
    "instrumento que mira siempre igual, el resultado es el contrario.",
    "Since 2003, Argentina's hot spots come from two MODIS instruments, on the Terra and Aqua satellites. Since "
    "2012, VIIRS instruments joined (Suomi NPP, NOAA-20 from 2018 and NOAA-21 from 2023): they see in more detail "
    "(375 m pixels instead of 1 km) and detect smaller fires. **Every new satellite makes FIRMS publish more hot "
    "spots, even if there is no more fire.** Added up as they are, fire seems to have multiplied; with one "
    "instrument that always looks the same way, the result is the opposite."))
an = anual_pais()
base = an[an.anio.between(2003, 2011)].mean()
fig = go.Figure()
fig.add_trace(go.Scatter(x=an.anio, y=100 * an.ingenua / base.ingenua, name=tr("Todos los focos sumados", "All hot spots added up"),
                         line=dict(color=NARANJA, width=3)))
aq = an[an.anio <= 2022]
fig.add_trace(go.Scatter(x=an.anio, y=100 * an.armonizada / base.armonizada, name=tr("Serie armonizada", "Harmonized series"),
                         line=dict(color=AZUL, width=4)))
fig.add_trace(go.Scatter(x=aq.anio, y=100 * aq.aqua / base.aqua, name=tr("Aqua solo (hasta 2022)", "Aqua alone (to 2022)"),
                         line=dict(color="#9CA3AF", width=2, dash="dot")))
for a, n in [(2012, "Suomi NPP"), (2018, "NOAA-20"), (2023, "NOAA-21")]:
    fig.add_vline(x=a - 0.5, line=dict(color="gray", width=1, dash="dash"), annotation_text=n, annotation_position="top left")
fig.update_layout(dragmode=False, height=380, margin=dict(l=10, r=10, t=30, b=10), legend=dict(orientation="h", y=-0.15),
                  yaxis_title=tr("Índice (promedio 2003–2011 = 100)", "Index (2003–2011 average = 100)"))
st.plotly_chart(fig, width="stretch", theme="streamlit", config=CONFIG_GRAFICO)
v = meta()["validacion"]["tendencia"]
st.caption(tr(
    f"Cambio de nivel (prueba de Pettitt): todos los focos sumados {'+' + num(100 * v['Ingenua: todos los focos sumados (2003-2025)']['cambio_pct'])} %; "
    f"Aqua solo {num(100 * v['Aqua solo (2003-2022)']['cambio_pct'])} %; serie armonizada {num(100 * v['Armonizada (2003-2025)']['cambio_pct'])} %.",
    f"Level change (Pettitt test): all hot spots added up {'+' + num(100 * v['Ingenua: todos los focos sumados (2003-2025)']['cambio_pct'])} %; "
    f"Aqua alone {num(100 * v['Aqua solo (2003-2022)']['cambio_pct'])} %; harmonized series {num(100 * v['Armonizada (2003-2025)']['cambio_pct'])} %."))

# ------------------------------------------------------------------------------------------------ how
st.header(tr("Cómo lo hacemos, en cuatro pasos", "How we do it, in four steps"))
pasos = [
    (tr("1. Limpiar", "1. Clean"), tr(
        "Solo focos de vegetación (tipo 0 de FIRMS) con confianza suficiente. Fuera las fuentes fijas: cuadrados de "
        "1 km donde VIIRS vio calor en 30 días distintos o más, como las antorchas de gas de Vaca Muerta. Queda el 87 %.",
        "Only vegetation hot spots (FIRMS type 0) with enough confidence. Fixed sources are removed: 1 km cells where "
        "VIIRS saw heat on 30 or more distinct days, such as Vaca Muerta's gas flares. 87 % remains.")),
    (tr("2. Contar parejo", "2. Count evenly"), tr(
        "Una grilla común de 1 km: cada cuadrado cuenta una vez por día (celda-día), por satélite y separando día y "
        "noche. Así desaparece la diferencia de tamaño de píxel.",
        "A common 1 km grid: each cell counts once per day (cell-day), per satellite and separating day and night. "
        "This removes the pixel-size difference.")),
    (tr("3. Convertir", "3. Convert"), tr(
        "Todo se lleva a \"cuántas celdas-día habría visto Aqua\". El factor se aprende con 2012–2022, cuando Aqua y "
        "Suomi NPP pasaban a la misma hora, por provincia, estación y día o noche; las provincias con pocos datos se "
        "apoyan en su región. Cada mes convertido trae su margen del 90 %.",
        "Everything is expressed as \"how many cell-days Aqua would have seen\". The factor is learned on 2012–2022, "
        "when Aqua and Suomi NPP passed at the same hour, per province, season and day or night; provinces with few "
        "data borrow strength from their region. Each converted month carries its 90 % range.")),
    (tr("4. Comprobar", "4. Validate"), tr(
        "Examen con años que el modelo no vio, búsqueda de escalones y comparación con la superficie quemada que "
        "informa el Ministerio de Ambiente. Resultados abajo.",
        "An exam with years the model never saw, a search for steps, and a comparison with the burned area reported "
        "by Argentina's Ministry of Environment. Results below.")),
]
cols = st.columns(4)
for c, (tit, txt) in zip(cols, pasos):
    with c.container(border=True):
        st.markdown(f"**{tit}**")
        st.write(txt)
st.markdown(tr(
    "**De dónde sale cada año:** 2003–2022, Aqua observado (2012–2022 controlado contra Suomi NPP convertido). "
    "2023–2025, Suomi NPP convertido: Aqua empezó a pasar más tarde, a una hora con más fuego, y dejó de ser una vara "
    "fija. 2026, NOAA-20 convertido (equivale a Suomi NPP: cociente 0,99).",
    "**Where each year comes from:** 2003–2022, Aqua observed (2012–2022 checked against converted Suomi NPP). "
    "2023–2025, converted Suomi NPP: Aqua began passing later, at an hour with more fire, and stopped being a fixed "
    "yardstick. 2026, converted NOAA-20 (equivalent to Suomi NPP: ratio 0.99)."))

# ------------------------------------------------------------------------------------------------ validation
st.header(tr("¿Cómo sabemos que funciona?", "How do we know it works?"))
val = meta()["validacion"]
st.markdown(tr("**a) El examen.** Aprendimos con 2012–2018 y convertimos 2019–2022 (incluye 2020, un año extremo), "
               "sin mirarlos. Comparamos con lo que Aqua vio de verdad. Los criterios se fijaron antes de correr la prueba.",
               "**a) The exam.** We learned on 2012–2018 and converted 2019–2022 (including 2020, an extreme year) "
               "without looking at it. We compared with what Aqua really saw. Criteria were set before running the test."))
nombres = {"M0": tr("M0 · un número para todo", "M0 · one number for everything"),
           "M1": tr("M1 · un número por estrato", "M1 · one number per stratum"),
           "M2": tr("M2 · apoyado en la región (elegido)", "M2 · borrowing from the region (chosen)"),
           "M3": tr("M3 · modelo mixto binomial negativo", "M3 · negative binomial mixed model")}
ex = pd.DataFrame(val["examen"])
tabla = pd.DataFrame({
    tr("Modelo", "Model"): ex.modelo.map(nombres),
    tr("Error total", "Total bias"): [f"{num(100 * x, 1)} %" for x in ex.sesgo],
    tr("Error de noche", "Night bias"): [f"{num(100 * x)} %" for x in ex.sesgo_noche],
    tr("Error típico por mes", "Typical monthly error"): [f"{num(100 * x)} %" for x in ex.error_tipico],
    tr("Acierto del margen del 90 %", "90 % range coverage"): [f"{num(100 * x, 1)} %" for x in ex.cobertura],
})
st.dataframe(tabla, hide_index=True, width="stretch")
st.caption(tr("Error típico: mediana del error relativo en provincia-meses con 10 celdas-día de Aqua o más. Acierto del "
              "margen: tiene que estar entre 85 % y 95 %. M0 parece bien en el total solo porque compensa dos errores "
              "grandes (de día da de menos y de noche, tres veces de más).",
              "Typical error: median relative error in province-months with 10 or more Aqua cell-days. Range coverage "
              "must be between 85 % and 95 %. M0 looks fine in total only because two large errors cancel out (too "
              "low by day, three times too high at night)."))
st.markdown(tr(
    "**b) Sin escalones.** Suomi NPP convertido dividido por Aqua da entre 0,94 y 1,05 todos los años de 2012 a 2022, "
    "sin saltos cuando llegan los satélites nuevos. NOAA-20 convertido, entre 0,98 y 1,04.",
    "**b) No steps.** Converted Suomi NPP divided by Aqua stays between 0.94 and 1.05 every year from 2012 to 2022, "
    "with no jump when new satellites arrive. Converted NOAA-20: 0.98 to 1.04."))
tp = val["tend_provincias"]
sd = val["spearman_dentro"]
st.markdown(tr(
    f"**c) Contra una fuente que no es satelital** (superficie incendiada que informan las provincias, 2003–2023). "
    f"Hectáreas y focos miden cosas distintas, así que comparamos rankings: dentro de cada provincia, la serie "
    f"armonizada ordena los años con una correlación de {num(sd['arm'], 2)}, como Aqua ({num(sd['aqua'], 2)}) y muy por "
    f"encima de la suma de todos los focos ({num(sd['ingenua'], 2)}). La época del año coincide (correlación "
    f"{num(val['estacionalidad'], 2)}; pico en agosto–octubre). **Lo que no se cumplió:** la superficie oficial del país "
    f"no muestra una tendencia clara. Pero en las {tp['n_sig']} provincias donde sí la hay, todas bajan, y la serie "
    f"armonizada coincide en {tp['arm']}; la suma de todos los focos, en {tp['ing']}.",
    f"**c) Against a non-satellite source** (burned area reported by the provinces, 2003–2023). Hectares and hot spots "
    f"measure different things, so we compare rankings: within each province, the harmonized series orders the years "
    f"with a correlation of {num(sd['arm'], 2)}, like Aqua ({num(sd['aqua'], 2)}) and far above the sum of all hot spots "
    f"({num(sd['ingenua'], 2)}). The time of year matches (correlation {num(val['estacionalidad'], 2)}; peak in "
    f"August–October). **What did not hold:** the official national burned area shows no clear trend. But in the "
    f"{tp['n_sig']} provinces where it does, all go down, and the harmonized series agrees in {tp['arm']}; the sum of all "
    f"hot spots, in {tp['ing']}."))
st.caption(tr("Resultados completos: reportes/validacion.md en el repositorio.",
              "Full results: reportes/validacion.md in the repository."))

# ------------------------------------------------------------------------------------------------ limits, sources
st.header(tr("Lo que hay que tener en cuenta", "Things to keep in mind"))
st.markdown(tr(
    "- Un foco es calor detectado, no un incendio ni una superficie quemada.\n"
    "- Las nubes y el humo esconden focos: un mes muy nublado puede parecer tranquilo.\n"
    "- Los meses convertidos desde VIIRS son una estimación: por eso llevan un margen.\n"
    "- En áreas chicas hay pocos focos y los números saltan mucho de un año a otro.\n"
    "- Los departamentos usan el factor de su provincia y no llevan margen todavía.\n"
    "- Una antorcha que cae entre dos cuadrados de 1 km puede escaparse del filtro de fuentes fijas (afecta sobre "
    "todo a Neuquén).\n"
    "- La intensidad del fuego (FRP) no se compara entre sensores; la app no la usa.\n"
    "- Esta herramienta no reemplaza a los sistemas oficiales de alerta.",
    "- A hot spot is detected heat, not a fire or a burned area.\n"
    "- Clouds and smoke hide hot spots: a very cloudy month may look calm.\n"
    "- Months converted from VIIRS are estimates, which is why they carry a range.\n"
    "- Small areas have few hot spots, and numbers jump a lot from year to year.\n"
    "- Departments use their province's factor and carry no range yet.\n"
    "- A gas flare falling between two 1 km cells may escape the fixed-source filter (mostly in Neuquén).\n"
    "- Fire intensity (FRP) is not comparable across sensors; the app does not use it.\n"
    "- This tool does not replace official warning systems."))
st.header(tr("Fuentes", "Sources"))
st.markdown(tr(
    "- **NASA FIRMS**: MODIS Colección 6.1 (Terra, Aqua) y VIIRS 375 m (Suomi NPP, NOAA-20, NOAA-21).\n"
    "- **Instituto Geográfico Nacional**: límites de provincias y departamentos.\n"
    "- **Ministerio de Ambiente de la Nación** (CIAM): estadísticas de incendios forestales, para validar.\n"
    "- Código: https://github.com/jorgemontivero/calendario-del-fuego",
    "- **NASA FIRMS**: MODIS Collection 6.1 (Terra, Aqua) and VIIRS 375 m (Suomi NPP, NOAA-20, NOAA-21).\n"
    "- **Instituto Geográfico Nacional** (Argentina): province and department boundaries.\n"
    "- **Argentina's Ministry of Environment** (CIAM): wildfire statistics, for validation.\n"
    "- Code: https://github.com/jorgemontivero/calendario-del-fuego"))
with st.expander(tr("Glosario", "Glossary")):
    st.markdown(tr(
        "- **Celda-día**: un cuadrado de 1 km con al menos un foco en un día. Es la unidad del calendario.\n"
        "- **Equivalente MODIS**: cuántas celdas-día habría visto Aqua, estimado a partir de VIIRS.\n"
        "- **Mediana**: el valor del medio cuando se ordenan todos los años.\n"
        "- **Percentil 90**: lo superan solo 1 de cada 10 años.\n"
        "- **Intervalo del 90 %**: el rango donde está el valor real con 90 % de probabilidad.",
        "- **Cell-day**: a 1 km cell with at least one hot spot on a given day. The calendar's unit.\n"
        "- **MODIS equivalent**: how many cell-days Aqua would have seen, estimated from VIIRS.\n"
        "- **Median**: the middle value when all years are sorted.\n"
        "- **90th percentile**: only 1 year in 10 is higher.\n"
        "- **90 % interval**: the range that contains the true value with 90 % probability."))
pie()
