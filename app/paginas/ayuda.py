"""Help: how to use the dashboard, how to read each chart, what a hot spot is, downloads and how to cite."""

import streamlit as st

from comun import cabecera, pie, t, tr

cabecera()
st.title(tr("Ayuda", "Help"))

c1, c2 = st.columns(2, gap="large")
with c1:
    st.subheader(tr("Cómo se usa", "How to use it"))
    st.markdown(tr(
        "1. **Elegí la zona** en la barra lateral: toda la Argentina, una provincia o un departamento. La elección se "
        "mantiene al cambiar de vista.\n"
        "2. **Serie histórica**: cómo viene el fuego en toda la serie. Arriba podés acotar los años y cambiar entre "
        "*cantidad de focos* y *comparado con lo normal*.\n"
        "3. **Un año**: elegí un año y mirá su temporada contra un año típico, y dónde se concentró el fuego (las "
        "zonas con más focos, coloreadas según su propio normal).\n"
        "4. **Ahora vs. antes**: elegí un período (los últimos 7 o 30 días, lo que va del año o fechas a medida) y "
        "compará ese mismo período en cada año desde 2003: en qué puesto queda y cuál fue el último año así de alto "
        "o de bajo.\n"
        "5. **Análisis geográfico**: dos mapas lado a lado, con la misma escala de colores: una zona en dos años, o "
        "dos provincias en el mismo año.\n"
        "6. **Detectados vs. reportados**: los focos que ven los satélites al lado de la superficie quemada que "
        "informa la provincia, año por año, y cuánto coinciden los años fuertes.\n"
        "7. **Clima y fuego**: si los meses más secos (menos humedad o menos lluvia en los meses previos) vienen con "
        "más fuego que lo normal. Compara diferencias con lo normal de cada mes, solo en la temporada de fuego. Es una "
        "asociación, no una causa: buena parte del fuego es quema agrícola, que depende de decisiones y no solo del "
        "clima. El clima es un reanálisis (NASA POWER, MERRA-2, celdas de unos 50 km), los meses recientes son "
        "provisorios y un departamento usa el clima de su provincia.\n"
        "8. **Las tarjetas de arriba** resumen el último mes completo: cuántos focos hubo, cuánto es lo normal, en qué "
        "puesto queda y si es un mes normal o inusual. Pasá el cursor para ver el margen y la probabilidad.\n"
        "9. **El ícono ⓘ** al lado de cada título explica ese gráfico.\n"
        "10. **Descargá** los datos de la zona elegida con el botón de la barra lateral, o todas las tablas completas "
        "en **Datos abiertos**.",
        "1. **Pick the area** in the sidebar: all of Argentina, a province or a department. The choice is kept when "
        "you switch views.\n"
        "2. **Historical series**: how fire has behaved over the whole series. On top you can narrow the years and "
        "switch between *number of hot spots* and *compared with normal*.\n"
        "3. **One year**: pick a year and see its season against a typical year, and where fire concentrated (the "
        "areas with most hot spots, colored against their own normal).\n"
        "4. **Now vs. before**: pick a period (the last 7 or 30 days, the year so far or custom dates) and compare "
        "the same period in every year since 2003: its rank and the last year that was this high or low.\n"
        "5. **Geographic analysis**: two maps side by side on the same color scale: one area in two years, or two "
        "provinces in the same year.\n"
        "6. **Detected vs. reported**: hot spots seen by satellites next to the burned area the province reports, "
        "year by year, and how well the strong years match.\n"
        "7. **Climate and fire**: whether drier months (lower humidity or less rain in the previous months) come with "
        "more fire than normal. It compares differences from each month's normal, fire-season months only. It is an "
        "association, not a cause: much of the fire is agricultural burning, which depends on decisions and not only "
        "on climate. Climate is a reanalysis (NASA POWER, MERRA-2, cells of about 50 km), recent months are "
        "provisional and a department uses its province's climate.\n"
        "8. **The cards on top** sum up the last full month: how many hot spots, what is normal, its rank, and whether "
        "it is a normal or unusual month. Hover to see the range and the probability.\n"
        "9. **The ⓘ icon** next to each title explains that chart.\n"
        "10. **Download** the data of the chosen area with the button in the sidebar, or every full table in "
        "**Open data**."))

    st.subheader(t("como_leer"))
    st.markdown(t("como_leer.texto"))

with c2:
    st.subheader(t("foco.titulo"))
    st.markdown(t("foco.texto"))

    st.subheader(tr("Los otros gráficos", "The other charts"))
    st.markdown(tr(
        "- **Focos por año**: el total de cada año en la misma vara (focos equivalentes MODIS). Las barras más "
        "oscuras son años convertidos desde VIIRS; la línea fina es su margen del 90 %. El año en curso está incompleto.\n"
        "- **¿Dónde se concentró el fuego?**: las zonas con más focos del año; rojo si estuvieron por encima de su "
        "propio normal, azul si por debajo.\n"
        "- **Temporada**: la línea naranja es el año elegido; la gris punteada, la mediana de 2003–2022; la banda gris, "
        "el rango habitual (8 de cada 10 años). Lo que sale de la banda es un mes fuera de lo habitual.\n"
        "- **Mapas** (Análisis geográfico): focos por cada 1.000 km² en cada departamento, para que los departamentos grandes no parezcan los "
        "que más arden solo por su tamaño. Con toda la Argentina elegida, muestra las provincias.",
        "- **Hot spots per year**: each year's total on the same yardstick (MODIS-equivalent hot spots). Darker bars "
        "are years converted from VIIRS; the thin line is their 90 % range. The current year is incomplete.\n"
        "- **Where did fire concentrate?**: the areas with most hot spots that year; red if above their own normal, "
        "blue if below.\n"
        "- **Season**: the orange line is the chosen year; the dotted grey line, the 2003–2022 median; the grey band, "
        "the usual range (8 out of 10 years). Anything outside the band is an unusual month.\n"
        "- **Maps** (Geographic analysis): hot spots per 1,000 km² in each department, so large departments don't look like the most burned "
        "just because of their size. With all of Argentina chosen, it shows the provinces."))

    st.subheader(tr("Descargas y cómo citar", "Downloads and how to cite"))
    st.markdown(t("desc.texto"))
    st.code(t("cita"), language=None)

pie()
