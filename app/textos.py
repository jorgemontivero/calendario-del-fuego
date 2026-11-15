"""Every text of the site, in Spanish and English (from textos_app.md). Code never writes loose text: always t()."""

T = {
    # general
    "app.nombre": ("Calendario del Fuego", "Calendario del Fuego"),
    "app.lema": ("Cuándo hay fuego en tu zona, con datos de satélite comparables desde 2003.",
                 "When fire happens where you live, from comparable satellite data since 2003."),
    "nav.app": ("App", "App"), "nav.metodologia": ("Metodología", "Methods"),
    "nav.equipo": ("Equipo", "Team"), "nav.contacto": ("Contacto", "Contact"),
    "idioma": ("Idioma", "Language"),
    "datos.actualizado": ("Datos al {fecha}.", "Data as of {fecha}."),
    "pie": ("Datos: NASA FIRMS, NASA POWER, IGN, Ministerio de Ambiente. Código abierto (MIT). **No es un sistema de alerta.** "
            "Este proyecto usa datos de la NASA, pero no está respaldado por la NASA.",
            "Data: NASA FIRMS, NASA POWER, IGN, Argentina's Ministry of Environment. Open code (MIT). **Not a warning system.** "
            "This project uses NASA data but is not endorsed by NASA."),
    # area
    "area.titulo": ("¿Qué zona querés mirar?", "Which area do you want to explore?"),
    "area.provincia": ("Provincia", "Province"), "area.departamento": ("Departamento (opcional)", "Department (optional)"),
    "area.todo_pais": ("Toda la Argentina", "All of Argentina"), "area.todos": ("Toda la provincia", "Whole province"),
    "area.anios": ("Años", "Years"),
    "area.anios.graficos": ("Años de los gráficos", "Years shown in the charts"),
    "kpi.ultimo": ("Último mes: {mes} {anio}", "Latest month: {mes} {anio}"),
    "area.aviso.chica": ("Esta área es chica: hay pocos focos por mes y los números varían mucho de un año a otro. "
                         "Miralos como orientación.",
                         "This area is small: few hot spots per month, and numbers vary a lot from year to year. "
                         "Treat them as a guide."),
    # calendar
    "cal.titulo": ("{area} · calendario de focos {desde}–{hasta}", "{area} · hot spot calendar {desde}–{hasta}"),
    "cal.modo": ("Ver", "Show"),
    "cal.modo.conteo": ("Cantidad de focos", "Number of hot spots"),
    "cal.modo.anomalia": ("Comparado con lo normal", "Compared with normal"),
    "cal.unidad": ("Focos por mes, en equivalente MODIS (celdas de 1 km con fuego en el día).",
                   "Hot spots per month, in MODIS equivalents (1 km cells with fire on a given day)."),
    "cal.leyenda.focos": ("focos", "hot spots"),
    "cal.leyenda.veces": ("veces lo normal", "times normal"),
    "cal.hover.valor": ("focos", "hot spots"), "cal.hover.normal": ("lo normal", "normal"),
    "cal.hover.puesto": ("puesto {k} de {n}", "rank {k} of {n}"),
    "cal.hover.rango": ("margen 90 %", "90 % range"),
    "cal.descripcion": ("Calendario de {area}: cada fila es un año y cada columna un mes; el color indica la "
                        "cantidad de focos en equivalente MODIS.",
                        "Calendar for {area}: each row is a year and each column a month; color shows the number of "
                        "hot spots in MODIS equivalents."),
    "como_leer": ("Cómo leer el calendario", "How to read the calendar"),
    "como_leer.texto": (
        "- **Cada fila es un año y cada columna un mes.** El color dice cuántos focos hubo: más oscuro, más fuego.\n"
        "- La escala es **logarítmica**: cada paso de color multiplica, no suma.\n"
        "- Con **\"Comparado con lo normal\"**, el color dice si el mes estuvo por encima (rojo) o por debajo (azul) "
        "de lo habitual para ese mes. Gris es normal.\n"
        "- **Lo normal** es la mediana de ese mes entre 2003 y 2022, los años que vio Aqua, la referencia. Usamos la "
        "mediana para que un año excepcional no la mueva.\n"
        "- Un **mes inusual** supera a 9 de cada 10 de los mismos meses de 2003–2022.\n"
        "- Desde 2023 los meses vienen de VIIRS convertido y tienen un **margen**: el valor real está, con 90 % de "
        "probabilidad, entre los dos números que se muestran.\n"
        "- Pasá el cursor (o tocá) cualquier mes para ver el detalle.",
        "- **Each row is a year and each column a month.** Color shows how many hot spots there were: darker means "
        "more fire.\n"
        "- The scale is **logarithmic**: each color step multiplies rather than adds.\n"
        "- With **\"Compared with normal\"**, color shows whether the month was above (red) or below (blue) what is "
        "usual for that month. Grey means normal.\n"
        "- **Normal** is the median of that month over 2003–2022, the years seen by Aqua, the reference. We use the "
        "median so one exceptional year doesn't shift it.\n"
        "- An **unusual month** is higher than 9 out of 10 of the same months in 2003–2022.\n"
        "- From 2023 on, months come from converted VIIRS and carry a **range**: the true value lies between the two "
        "numbers shown, with 90 % probability.\n"
        "- Hover (or tap) any month for details."),
    "foco.titulo": ("¿Qué es un foco de calor?", "What is a hot spot?"),
    "foco.texto": (
        "Es un punto donde un satélite detectó que la superficie estaba mucho más caliente que su entorno en el "
        "momento en que pasó. Casi siempre es fuego: un incendio forestal, una quema de pastizal o de rastrojo.\n\n"
        "- **No es un incendio.** Un incendio grande produce muchos focos; varias quemas chicas cercanas pueden "
        "aparecer como uno solo.\n- **No es superficie quemada.** Cuenta dónde había calor, no cuántas hectáreas "
        "se quemaron.\n- **No es todo el fuego.** El satélite pasa unas pocas veces por día: si el fuego empieza y "
        "termina entre pasadas, o si hay nubes o humo espeso, no se ve.\n\n"
        "Los focos vienen del sistema FIRMS de la NASA.",
        "A place where a satellite found the ground much hotter than its surroundings at the moment it flew over. "
        "It is almost always fire: a wildfire, or burning grassland or crop stubble.\n\n"
        "- **It is not a fire.** One large fire produces many hot spots; several small burns close together may "
        "show up as one.\n- **It is not burned area.** It counts where there was heat, not how many hectares "
        "burned.\n- **It is not all fire.** The satellite passes only a few times a day: a fire that starts and ends "
        "between passes, or is hidden by clouds or thick smoke, is missed.\n\n"
        "Hot spots come from NASA's FIRMS system."),
    "armon.corta": ("Desde 2012 hay satélites que ven fuegos más chicos. Para que los años se puedan comparar, "
                    "convertimos todo a una misma vara: la del satélite Aqua.",
                    "Since 2012, newer satellites detect smaller fires. To make years comparable, we convert "
                    "everything to one yardstick: the Aqua satellite's."),
    # last full month card
    "ultimo.titulo": ("Último mes completo · {mes} {anio}", "Last full month · {mes} {anio}"),
    "ultimo.focos": ("Focos (equivalente MODIS)", "Hot spots (MODIS equivalent)"),
    "ultimo.normal": ("Lo normal para {mes}", "Normal for {mes}"),
    "ultimo.puesto": ("Lugar entre los meses de {mes}", "Rank among {mes} months"),
    "ultimo.puesto.valor": ("{k} de {n}", "{k} of {n}"),
    "ultimo.rango": ("Convertido desde VIIRS. Con 90 % de probabilidad, entre {li} y {ls} focos.",
                     "Converted from VIIRS. With 90 % probability, between {li} and {ls} hot spots."),
    "ultimo.prob": ("Probabilidad de que sea un mes inusual: {p}.", "Probability of an unusual month: {p}."),
    "estado.inusual": ("Inusual", "Unusual"), "estado.arriba": ("Por encima de lo normal", "Above normal"),
    "estado.normal": ("Normal", "Normal"), "estado.abajo": ("Por debajo de lo normal", "Below normal"),
    "estado.en_curso": ("Mes en curso", "Month in progress"),
    "en_curso": ("Mes en curso: datos hasta el {fecha}. No se compara con lo normal hasta que termine.",
                 "Month in progress: data up to {fecha}. It is not compared with normal until it ends."),
    # season
    "temp.titulo": ("{area} · ¿cuándo hay fuego?", "{area} · when does fire happen?"),
    "temp.anio": ("Año a comparar", "Year to compare"),
    "temp.banda": ("Rango habitual (8 de cada 10 años, 2003–2022)", "Usual range (8 out of 10 years, 2003–2022)"),
    "temp.mediana": ("Mediana 2003–2022", "2003–2022 median"),
    "temp.en_curso.corto": ("en curso", "in progress"),
    "temp.en_curso": ("En curso (al {fecha})", "In progress (to {fecha})"),
    "temp.pico": ("Mes pico", "Peak month"),
    "temp.temporada": ("Temporada de fuego", "Fire season"),
    "temp.temporada.ayuda": ("Meses que juntan el 80 % de los focos de un año típico.",
                             "Months that hold 80 % of a typical year's hot spots."),
    "temp.tendencia": ("¿Hay más fuego que antes?", "Is there more fire than before?"),
    "temp.tendencia.sube": ("En 2003–2025 los focos de esta zona tienden a subir (prueba de Mann-Kendall, 5 %).",
                            "In 2003–2025 hot spots in this area tend to rise (Mann-Kendall test, 5 %)."),
    "temp.tendencia.baja": ("En 2003–2025 los focos de esta zona tienden a bajar (prueba de Mann-Kendall, 5 %).",
                            "In 2003–2025 hot spots in this area tend to fall (Mann-Kendall test, 5 %)."),
    "temp.tendencia.nada": ("En 2003–2025 no hay una tendencia clara en esta zona (prueba de Mann-Kendall, 5 %).",
                            "In 2003–2025 there is no clear trend in this area (Mann-Kendall test, 5 %)."),
    # downloads
    "desc.titulo": ("Descargar los datos de {area}", "Download data for {area}"),
    "desc.serie": ("Serie mensual armonizada (CSV)", "Harmonized monthly series (CSV)"),
    "desc.boton": ("Descargar los datos de {area} (CSV)", "Download the data for {area} (CSV)"),
    "area.pais_frase": ("la Argentina", "Argentina"),
    "desc.texto": ("Una planilla con un renglón por mes, de 2003 a hoy: focos en equivalente MODIS, lo normal, el puesto, el margen y la fuente. "
                   "Los nombres de columna van en inglés en los dos idiomas.",
                   "A spreadsheet with one row per month, 2003 to today: hot spots in MODIS equivalents, normal, rank, "
                   "range and source."),
    "desc.citar": ("Cómo citar", "How to cite"),
    "cita": ("Calendario del Fuego (2026). https://github.com/jorgemontivero/calendario-del-fuego. NASA Space Apps "
             "Challenge, Catamarca.", "Calendario del Fuego (2026). https://github.com/jorgemontivero/calendario-del-fuego. "
             "NASA Space Apps Challenge, Catamarca."),
    # dashboard
    "tab.filtros": ("Filtros", "Filters"),
    "nav.geo": ("Análisis geográfico", "Geographic analysis"),
    "nav.rep": ("Detectados vs. reportados", "Detected vs. reported"),
    "nav.ahora": ("Ahora vs. antes", "Now vs. before"),
    "nav.acerca": ("Acerca del proyecto", "About the project"),
    "ahora.periodo": ("Período", "Period"),
    "ahora.modo.7": ("Últimos 7 días", "Last 7 days"), "ahora.modo.30": ("Últimos 30 días", "Last 30 days"),
    "ahora.modo.anio": ("En lo que va del año", "Year to date"), "ahora.modo.fechas": ("Elegir fechas", "Pick dates"),
    "ahora.fechas": ("Fechas", "Dates"),
    "ahora.max_anio": ("El período puede ser de hasta un año.", "The period can be up to one year."),
    "ahora.focos.ayuda": ("Focos del período en equivalente MODIS (serie armonizada diaria), contra lo normal: la "
                          "mediana del mismo período en 2003–2022. El último día con datos todavía se está cargando, "
                          "así que los períodos terminan el día anterior. Los valores diarios convertidos no llevan "
                          "margen.", "Hot spots in the period in MODIS equivalents (daily harmonized series), against "
                          "normal: the median of the same period in 2003–2022. The last day with data is still being "
                          "loaded, so periods end the day before. Converted daily values carry no range."),
    "ahora.puesto": ("Puesto entre los años", "Rank among years"),
    "ahora.puesto.ayuda": ("Lugar de este período entre los mismos períodos de los {n} años desde 2003.",
                           "Rank of this period among the same periods of the {n} years since 2003."),
    "ahora.desde.alto": ("Último año así de alto", "Last year this high"),
    "ahora.desde.bajo": ("Último año así de bajo", "Last year this low"),
    "ahora.desde.ayuda": ("El último año anterior con un período igual o más fuerte (o igual o más débil, si este "
                          "período viene bajo).", "The last earlier year with an equal or stronger period (or equal "
                          "or weaker, if this period is low)."),
    "ahora.record": ("ninguno: récord", "none: a record"),
    "ahora.minimo": ("ninguno: mínimo", "none: a record low"),
    "ahora.dias": ("Días con fuego", "Days with fire"),
    "ahora.dias.valor": ("{k} (normal: {n})", "{k} (normal: {n})"),
    "ahora.dias.ayuda": ("Días del período con al menos un foco equivalente en la zona, contra la mediana de 2003–2022.",
                         "Days in the period with at least one equivalent hot spot in the area, against the 2003–2022 "
                         "median."),
    "ahora.titulo.barras": ("{p}, año por año", "{p}, year by year"),
    "ahora.ayuda.barras": ("El mismo período del calendario en cada año desde 2003, con la serie armonizada. El año "
                           "actual, en naranja fuerte; la línea punteada es lo normal (mediana 2003–2022).",
                           "The same calendar period in every year since 2003, from the harmonized series. The current "
                           "year in strong orange; the dashed line is normal (2003–2022 median)."),
    "ahora.normal": ("línea punteada: lo normal ({v})", "dashed line: normal ({v})"),
    "ahora.titulo.acum": ("Cómo se fue acumulando", "How it built up"),
    "ahora.ayuda.acum": ("Focos acumulados día por día dentro del período: el año actual contra la mediana y el rango "
                         "habitual (8 de cada 10 años) de 2003–2022. Si la línea naranja sale de la banda, el episodio "
                         "es fuera de lo común.", "Hot spots accumulated day by day within the period: the current "
                         "year against the 2003–2022 median and usual range (8 out of 10 years). If the orange line "
                         "leaves the band, the episode is out of the ordinary."),
    "ahora.eje.dia": ("día del período", "day of the period"),
    "ahora.eje.acum": ("focos acumulados", "cumulative hot spots"),
    "rep.depto": ("(datos oficiales por provincia; se muestra la de {dep})",
                  "(official data are by province; showing that of {dep})"),
    "rep.anios": ("Años comparados", "Years compared"),
    "rep.anios.ayuda": ("Años con superficie informada por la provincia (2003–2025). Hay provincias y años sin dato.",
                        "Years with burned area reported by the province (2003–2025). Some provinces and years have no "
                        "data."),
    "rep.rho": ("Coincidencia de rankings (ρ)", "Ranking agreement (ρ)"),
    "rep.rho.ayuda": ("Correlación de Spearman entre los focos armonizados y las hectáreas informadas, año por año: 1 "
                      "si ordenan los años igual, 0 si no tienen nada que ver. Compara órdenes, no valores. Para toda "
                      "la Argentina da bajo: el total oficial lo mueven unos pocos años de pastizal enormes en La Pampa "
                      "y Buenos Aires, y las provincias que informan cambian de un año a otro. Por provincia la "
                      "coincidencia es mayor (mediana 0,48, ver Metodología).",
                      "Spearman correlation between harmonized hot spots and reported hectares, year by year: 1 if they "
                      "rank the years the same way, 0 if unrelated. It compares rankings, not values. For all of "
                      "Argentina it is low: the national official total is driven by a few huge grassland years in La "
                      "Pampa and Buenos Aires, and the provinces that report change from year to year. By province "
                      "the agreement is higher (median 0.48, see Methods)."),
    "rep.picos": ("Año pico: focos · hectáreas", "Peak year: hot spots · hectares"),
    "rep.picos.ayuda": ("El año con más focos detectados y el año con más superficie informada.",
                        "The year with most detected hot spots and the year with most reported area."),
    "rep.top3": ("Años más fuertes en común", "Strongest years in common"),
    "rep.top3.valor": ("{k} de 3", "{k} of 3"),
    "rep.top3.ayuda": ("De los 3 años con más focos, cuántos están también entre los 3 con más superficie informada.",
                       "Of the 3 years with most hot spots, how many are also among the 3 with most reported area."),
    "rep.titulo.barras": ("Detectados y reportados, año por año", "Detected and reported, year by year"),
    "rep.ayuda.barras": ("Arriba, los focos detectados por satélite (serie armonizada, equivalente MODIS). Abajo, la "
                         "superficie quemada que la provincia informó al Ministerio de Ambiente (CIAM): hasta 2023, la "
                         "serie larga (dt 510); 2024–2025, en gris claro, la tabla de reportes (dt 416), que no siempre "
                         "coincide con la otra. Miden cosas distintas: calor visto desde el espacio y hectáreas "
                         "contadas en tierra.",
                         "Top: hot spots detected by satellite (harmonized series, MODIS equivalent). Bottom: burned area "
                         "the province reported to the Ministry of Environment (CIAM): up to 2023, the long series "
                         "(dt 510); 2024–2025, in light grey, the reports table (dt 416), which does not always agree "
                         "with the other. They measure different things: heat seen from space and hectares counted on "
                         "the ground."),
    "rep.sub.focos": ("Focos detectados (satélite)", "Detected hot spots (satellite)"),
    "rep.sub.ha": ("Hectáreas reportadas (provincias)", "Reported hectares (provinces)"),
    "rep.titulo.disp": ("¿Coinciden los años fuertes?", "Do the strong years match?"),
    "rep.ayuda.disp": ("Un punto por año (escala logarítmica en los dos ejes). Si los puntos suben de izquierda a "
                       "derecha, los años con más focos son también los de más superficie informada.",
                       "One point per year (log scale on both axes). If the points rise from left to right, the years "
                       "with more hot spots are also those with more reported area."),
    "rep.eje.focos": ("focos detectados", "detected hot spots"),
    "rep.eje.ha": ("hectáreas reportadas", "reported hectares"),
    "rank.titulo": ("¿Dónde hubo más fuego en {anio}?", "Where was there most fire in {anio}?"),
    "rank.provincias": ("top {n} provincias", "top {n} provinces"),
    "rank.mas": ("más que lo normal", "above normal"), "rank.menos": ("menos", "below"),
    "rank.departamentos": ("top {n} departamentos de {prov}", "top {n} departments of {prov}"),
    "rank.ayuda": ("Las 10 zonas con más focos en el año (equivalente MODIS). El color compara cada una con su propio "
                   "normal (mediana de sus totales 2003–2022 en los mismos meses): rojo, más fuego que lo habitual; "
                   "azul, menos. El mapa está en Análisis geográfico.",
                   "The 10 areas with the most hot spots in the year (MODIS equivalent). Color compares each with its own "
                   "normal (median of its 2003–2022 totals for the same months): red, more fire than usual; blue, "
                   "less. The map is in Geographic analysis."),
    "geo.titulo": ("Análisis geográfico", "Geographic analysis"),
    "geo.modo": ("Comparar", "Compare"),
    "geo.modo.anios": ("Una zona en dos años", "One area, two years"),
    "geo.modo.zonas": ("Dos zonas en un año", "Two areas, one year"),
    "geo.zona": ("Zona", "Area"), "geo.anio": ("Año", "Year"),
    "geo.resumen": ("{v} focos · {d} por 1.000 km²", "{v} hot spots · {d} per 1,000 km²"),
    "geo.ayuda": ("Focos por cada 1.000 km² con la serie armonizada: toda la Argentina por provincia, una provincia "
                  "por departamento. Los dos mapas usan la misma escala de colores, para que se puedan comparar. Para "
                  "el año en curso se cuentan los meses completos. Se puede acercar con la rueda del mouse.",
                  "Hot spots per 1,000 km² from the harmonized series: all of Argentina by province, a province by "
                  "department. Both maps share the same color scale so they can be compared. For the current year, "
                  "complete months are counted. Zoom with the mouse wheel."),
    "puesto.max": ("el más alto de {n}", "the highest of {n}"),
    "puesto.min": ("el más bajo de {n}", "the lowest of {n}"),
    "puesto.k": ("{k}.° más alto de {n}", "{k}{suf} highest of {n}"),
    "puesto.ayuda": ("Lugar entre los mismos meses de todos los años desde 2003, del más alto al más bajo.",
                     "Rank among the same month of every year since 2003, from highest to lowest."),
    "kpi.anio": ("Año {anio}", "Year {anio}"),
    "kpi.anio.parcial": ("{anio}, ene–{mes}", "{anio}, Jan–{mes}"),
    "kpi.anio.ayuda": ("Total del año en focos equivalentes MODIS, contra lo normal: la mediana de los totales de "
                       "2003–2022.", "Year total in MODIS-equivalent hot spots, against normal: the median of the "
                       "2003–2022 totals."),
    "kpi.puesto.anios": ("Puesto entre los años", "Rank among years"),
    "kpi.puesto.anios.ayuda": ("Lugar del total de este año entre los años completos desde 2003 (para el año en curso, "
                               "comparando los mismos meses).", "Rank of this year's total among the complete years "
                               "since 2003 (for the current year, comparing the same months)."),
    "kpi.pico": ("Mes pico de {anio}", "Peak month of {anio}"),
    "kpi.pico.ayuda": ("El mes con más focos de este año. El pico de un año típico está en el título de la temporada.",
                       "The month with the most hot spots this year. The peak of a typical year is in the season title."),
    "temp.corta": ("pico típico: {pico} · temporada: {temp}", "typical peak: {pico} · season: {temp}"),
    "kpi.inusuales": ("Fuera de lo habitual", "Outside the usual range"),
    "kpi.inusuales.valor": ("{bajos} bajos · {altos} altos", "{bajos} low · {altos} high"),
    "kpi.inusuales.ayuda": ("De los {n} meses completos del año, cuántos quedaron por debajo o por encima del rango "
                            "habitual (la banda gris del gráfico de temporada: 8 de cada 10 años de 2003–2022).",
                            "Of the year's {n} complete months, how many fell below or above the usual range (the grey "
                            "band of the season chart: 8 out of 10 years in 2003–2022)."),
    "estado.corto.inusual": ("Inusual", "Unusual"), "estado.corto.arriba": ("Sobre lo normal", "Above normal"),
    "estado.corto.normal": ("Normal", "Normal"), "estado.corto.abajo": ("Bajo lo normal", "Below normal"),
    "estado.corto.en_curso": ("En curso", "In progress"),
    "nav.ayuda": ("Ayuda", "Help"),
    "lateral.ayuda": ("No es un sistema de alerta. Cómo leer los gráficos: sección **Ayuda**.",
                      "Not a warning system. How to read the charts: **Help** section."),
    "area.aviso.corto": ("Área chica: números orientativos", "Small area: indicative numbers"),
    "tend.corta.sube": ("tendencia en alza", "upward trend"), "tend.corta.baja": ("tendencia en baja", "downward trend"),
    "tend.corta.nada": ("sin tendencia clara", "no clear trend"),
    "tab.serie": ("Serie histórica", "Historical series"),
    "tab.un_anio": ("Un año", "One year"),
    "tab.anio": ("Año del mapa y de la temporada", "Year for the map and season"),
    "kpi.mes": ("{mes} {anio}", "{mes} {anio}"),
    "kpi.mes.ayuda": ("Último mes completo, en focos equivalentes MODIS. La flecha compara con lo normal para ese mes "
                      "(mediana 2003–2022).", "Last full month, in MODIS-equivalent hot spots. The arrow compares with "
                      "normal for that month (2003–2022 median)."),
    "kpi.acum": ("{anio}, ene–{mes}", "{anio}, Jan–{mes}"),
    "kpi.acum.ayuda": ("Enero a {mes}, contra lo normal de esos meses.", "January to {mes}, against normal for those months."),
    "kpi.puesto": ("Puesto en {mes}", "Rank in {mes}"),
    "kpi.estado": ("Cómo viene", "How it looks"),
    "kpi.vs_normal": ("vs. lo normal", "vs. normal"),
    "anual.titulo": ("Focos por año", "Hot spots per year"),
    "anual.modo": ("Vista", "View"), "anual.modo.anio": ("Por año", "Per year"), "anual.modo.mes": ("Por mes", "Per month"),
    "mes.titulo": ("Tendencia por mes", "Trend by month"),
    "mes.eje": ("Cambio por año, 2003–2025", "Change per year, 2003–2025"),
    "mes.ayuda": ("Cuánto subió o bajó cada mes del año, por año, entre 2003 y 2025 (pendiente de Sen sobre el "
                  "logaritmo). Azul: baja; naranja: sube; gris: sin tendencia clara (Mann-Kendall, p ≥ 0,10). El "
                  "período es fijo y no sigue al filtro de años: con pocos años no hay tendencia que medir. Es "
                  "descriptivo: con 12 meses probados, alguno puede salir claro por azar, y en zonas con poco fuego "
                  "lo esperable es que casi todo salga gris.",
                  "How much each month of the year went up or down, per year, from 2003 to 2025 (Sen slope on the "
                  "logarithm). Blue: down; orange: up; grey: no clear trend (Mann-Kendall, p ≥ 0.10). The period is "
                  "fixed and does not follow the year range: a few years hold no trend to measure. It is "
                  "descriptive: with 12 months tested, one may look clear by chance, and in areas with little fire "
                  "most months will be grey."),
    "mes.hover": ("<b>{mes}</b>: {c} % por año (p = {p})<br>Mediana 2003–2011: {a} · 2014–2025: {b}",
                  "<b>{mes}</b>: {c} % per year (p = {p})<br>Median 2003–2011: {a} · 2014–2025: {b}"),
    "mes.hover.dudosa": ("Sin tendencia clara", "No clear trend"),
    "anual.ayuda": ("Barras: total del año; la línea fina es el margen del 90 % de los años convertidos. "
                    "{anio} está incompleto.", "Bars: yearly total; the thin line is the 90 % range of converted years. "
                    "{anio} is incomplete."),
    "mapa.titulo.dep": ("{area} · focos por cada 1.000 km², {anio}", "{area} · hot spots per 1,000 km², {anio}"),
    "mapa.ayuda": ("Serie armonizada por departamento, dividida por la superficie: así los departamentos grandes no "
                   "parecen los que más arden solo por su tamaño. Los departamentos no llevan margen todavía.",
                   "Harmonized series by department, divided by area, so large departments don't look like the most "
                   "burned just because of their size. Departments carry no range yet."),
    "mapa.leyenda": ("focos / 1.000 km²", "hot spots / 1,000 km²"),
    "panel.calendario": ("Calendario", "Calendar"), "panel.temporada": ("Temporada", "Season"),
    # emergency
    "emerg.boton": ("¿Ves fuego ahora?", "See a fire now?"),
    "emerg.titulo": ("Si ves un incendio, llamá ya", "If you see a fire, call now"),
    "emerg.texto": ("Esta página no recibe avisos de incendios. Para que llegue ayuda, llamá a los servicios de "
                    "emergencia:", "This site does not receive fire reports. To get help, call emergency services "
                    "(phone numbers for Argentina):"),
    "emerg.lista": ("- **100** · Bomberos\n- **911** · Emergencias (donde esté disponible)\n- **103** · Defensa Civil",
                    "- **100** · Fire department\n- **911** · Emergencies (where available)\n- **103** · Civil Defense"),
    "emerg.datos": ("Indicá dónde estás, qué ves (humo, llamas) y hacia dónde va el fuego.",
                    "Say where you are, what you see (smoke, flames) and which way the fire is moving."),
    "fuente.aqua": ("Aqua observado", "Aqua observed"), "fuente.snpp": ("Suomi NPP convertido", "Suomi NPP converted"),
    "fuente.noaa20": ("NOAA-20 convertido", "NOAA-20 converted"),
    # climate context card (Series view)
    "kpi.lluvia": ("Lluvia {m1}–{m2}", "Rain {m1}–{m2}"),
    "kpi.lluvia.seco": ("más seco", "drier"), "kpi.lluvia.normal": ("normal", "normal"),
    "kpi.lluvia.lluvioso": ("más lluvioso", "wetter"),
    "kpi.lluvia.ayuda": ("Lluvia acumulada de los últimos tres meses completos en la provincia (NASA POWER). Lo normal "
                         "para esos meses: {n} mm (mediana 2003–2022); «más seco» = entre el tercio de años más secos. "
                         "Humedad del último mes: {h} % (normal {hn} %). Contexto, no pronóstico.",
                         "Rain over the last three full months in the province (NASA POWER). Normal for those months: "
                         "{n} mm (2003–2022 median); “drier” = within the driest third of years. Humidity last month: "
                         "{h} % (normal {hn} %). Context, not a forecast."),
    # one-sentence summary (Series view); short, so it fits one line
    "res.mes.max": ("{mes} de {anio} fue el {m} con más focos en {n} años ({v}).",
                    "{mes} {anio} was the {m} with the most hot spots in {n} years ({v})."),
    "res.mes.min": ("{mes} de {anio} fue el {m} con menos focos en {n} años ({v}).",
                    "{mes} {anio} was the {m} with the fewest hot spots in {n} years ({v})."),
    "res.mes.arriba": ("{mes} de {anio}: {v} focos, {p} % más que lo normal.",
                       "{mes} {anio}: {v} hot spots, {p} % above normal."),
    "res.mes.abajo": ("{mes} de {anio}: {v} focos, {p} % menos que lo normal.",
                      "{mes} {anio}: {v} hot spots, {p} % below normal."),
    "res.mes.normal": ("{mes} de {anio}: {v} focos, dentro de lo habitual (mediana: {n}).",
                       "{mes} {anio}: {v} hot spots, within the usual range (median: {n})."),
    "res.mes.sin": ("{mes} de {anio}: sin focos, como es habitual.", "{mes} {anio}: no hot spots, as usual."),
    "res.anio.arriba": ("En el año, {p} % más que lo normal.", "Year so far: {p} % above normal."),
    "res.anio.abajo": ("En el año, {p} % menos que lo normal.", "Year so far: {p} % below normal."),
    "res.anio.cerca": ("En el año, cerca de lo normal.", "Year so far: close to normal."),
    # Climate and fire view
    "nav.datos": ("Datos abiertos", "Open data"),
    "nav.clima": ("Clima y fuego", "Climate and fire"),
    "clima.depto": ("clima de la provincia: {prov}", "climate of the province: {prov}"),
    "clima.variable": ("Variable de clima", "Climate variable"),
    "clima.var.humedad": ("Humedad del mes", "Humidity of the month"),
    "clima.var.lluvia3": ("Lluvia de los 3 meses previos", "Rain of the 3 previous months"),
    "clima.var.lluvia6": ("Lluvia de los 6 meses previos", "Rain of the 6 previous months"),
    "clima.var.temp": ("Temperatura máxima", "Maximum temperature"),
    "clima.ter.humedad.seco": ("Más seco", "Drier"), "clima.ter.humedad.humedo": ("Más húmedo", "More humid"),
    "clima.ter.lluvia3.seco": ("Menos lluvia", "Less rain"), "clima.ter.lluvia3.humedo": ("Más lluvia", "More rain"),
    "clima.ter.lluvia6.seco": ("Menos lluvia", "Less rain"), "clima.ter.lluvia6.humedo": ("Más lluvia", "More rain"),
    "clima.ter.temp.seco": ("Más calor", "Hotter"), "clima.ter.temp.humedo": ("Más fresco", "Cooler"),
    "clima.ter.medio": ("Normal", "Normal"),
    "clima.rho": ("Asociación (ρ de Spearman)", "Association (Spearman ρ)"),
    "clima.rho.ayuda": ("Entre −1 y 1. Negativo: cuanto más bajo el clima respecto de lo normal, más fuego respecto de "
                        "lo normal. Cerca de 0: sin relación. Es una asociación, no una causa.",
                        "Between −1 and 1. Negative: the lower the climate against normal, the more fire against "
                        "normal. Near 0: no relation. It is an association, not a cause."),
    "clima.n": ("Meses comparados", "Months compared"),
    "clima.n.meses": ("Temporada de esta zona: {m}.", "This area's season: {m}."),
    "clima.n.ayuda": ("Solo los meses de la temporada de fuego de la zona (los que juntan el 80 % del fuego de un año "
                      "típico), de 2003 al último mes completo. Fuera de temporada casi no hay fuego y la comparación no "
                      "dice nada.",
                      "Only the area's fire-season months (those holding 80 % of a typical year's fire), from 2003 to "
                      "the last full month. Off season there is hardly any fire and the comparison says nothing."),
    "clima.p": ("Fuego alto · {ter}", "Fire above normal · {ter}"),
    "clima.p.ayuda": ("De los meses del tercio «{ter}», qué parte tuvo más focos que lo normal para ese mes. Si el "
                      "clima no importara, rondaría el 50 %.",
                      "Of the months in the “{ter}” third, the share with more hot spots than normal for that month. If "
                      "climate did not matter it would be around 50 %."),
    "clima.titulo.disp": ("Clima contra fuego, cada mes de temporada", "Climate against fire, each season month"),
    "clima.ayuda.disp": ("Cada punto es un mes de temporada. Horizontal: cuánto se apartó el clima de lo normal para ese "
                         "mes del año. Vertical: cuántas veces lo normal fueron los focos (1 = normal, 2 = el doble). "
                         "Los puntos grandes son el último año; la línea negra, la tendencia (mediana móvil). Se usa la "
                         "diferencia con lo normal porque, si no, las dos series siguen las estaciones y la relación solo "
                         "diría que existe el invierno.",
                         "Each dot is a season month. Horizontal: how far climate was from normal for that month of the "
                         "year. Vertical: how many times normal the hot spots were (1 = normal, 2 = double). Large dots "
                         "are the last year; the black line, the trend (running median). The difference from normal is "
                         "used because otherwise both series follow the seasons and the relation would only say that "
                         "winter exists."),
    "clima.titulo.box": ("Fuego según el clima del mes", "Fire by the month's climate"),
    "clima.ayuda.box": ("Los meses de temporada partidos en tres grupos iguales según el clima. La caja va del 25 % al "
                        "75 % de los meses de cada grupo y la raya del medio es la mediana. Arriba, qué parte de esos "
                        "meses tuvo fuego sobre lo normal.",
                        "Season months split into three equal groups by climate. The box spans 25 % to 75 % of each "
                        "group's months and the middle line is the median. On top, the share of those months with fire "
                        "above normal."),
    "clima.sobre": ("{p} % sobre lo normal", "{p} % above normal"),
    "clima.tendencia": ("Tendencia", "Trend"),
    "clima.eje.fuego": ("Focos / lo normal", "Hot spots / normal"),
    "clima.eje.humedad": ("Humedad: diferencia con lo normal (puntos de %)", "Humidity: difference from normal (% points)"),
    "clima.eje.lluvia3": ("Lluvia de los 3 meses previos / lo normal", "Rain of the 3 previous months / normal"),
    "clima.eje.lluvia6": ("Lluvia de los 6 meses previos / lo normal", "Rain of the 6 previous months / normal"),
    "clima.eje.temp": ("Temperatura máxima: diferencia con lo normal (°C)", "Max temperature: difference from normal (°C)"),
}

MESES = {"es": ["ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic"],
         "en": ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]}
MESES_LARGOS = {"es": ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre",
                       "octubre", "noviembre", "diciembre"],
                "en": ["January", "February", "March", "April", "May", "June", "July", "August", "September",
                       "October", "November", "December"]}
