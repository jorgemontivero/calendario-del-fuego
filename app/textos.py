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
    "pie": ("Datos: NASA FIRMS, IGN, Ministerio de Ambiente. Código abierto (MIT). **No es un sistema de alerta.** "
            "Este proyecto usa datos de la NASA, pero no está respaldado por la NASA.",
            "Data: NASA FIRMS, IGN, Argentina's Ministry of Environment. Open code (MIT). **Not a warning system.** "
            "This project uses NASA data but is not endorsed by NASA."),
    # area
    "area.titulo": ("¿Qué zona querés mirar?", "Which area do you want to explore?"),
    "area.provincia": ("Provincia", "Province"), "area.departamento": ("Departamento (opcional)", "Department (optional)"),
    "area.todo_pais": ("Toda la Argentina", "All of Argentina"), "area.todos": ("Toda la provincia", "Whole province"),
    "area.anios": ("Años", "Years"),
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
    "temp.pico": ("Mes pico", "Peak month"),
    "temp.temporada": ("Temporada de fuego", "Fire season"),
    "temp.temporada.ayuda": ("Meses que juntan el 80 % de los focos de un año típico.",
                             "Months that hold 80 % of a typical year's hot spots."),
    "temp.tendencia": ("¿Hay más fuego que antes?", "Is there more fire than before?"),
    "temp.tendencia.sube": ("Sí: la tendencia 2003–2025 es creciente.", "Yes: the 2003–2025 trend is upward."),
    "temp.tendencia.baja": ("No: la tendencia 2003–2025 es decreciente.", "No: the 2003–2025 trend is downward."),
    "temp.tendencia.nada": ("No hay una tendencia clara en 2003–2025.", "There is no clear trend in 2003–2025."),
    # downloads
    "desc.titulo": ("Descargar los datos de {area}", "Download data for {area}"),
    "desc.serie": ("Serie mensual armonizada (CSV)", "Harmonized monthly series (CSV)"),
    "desc.texto": ("Focos por mes en equivalente MODIS, 2003–hoy, con lo normal, el puesto, el margen y la fuente. "
                   "Los nombres de columna van en inglés en los dos idiomas.",
                   "Monthly hot spots in MODIS equivalents, 2003–today, with normal, rank, range and source."),
    "desc.citar": ("Cómo citar", "How to cite"),
    "cita": ("Calendario del Fuego (2026). https://github.com/jorgemontivero/calendario-del-fuego. NASA Space Apps "
             "Challenge, Catamarca.", "Calendario del Fuego (2026). https://github.com/jorgemontivero/calendario-del-fuego. "
             "NASA Space Apps Challenge, Catamarca."),
    # dashboard
    "tab.filtros": ("Filtros", "Filters"),
    "estado.corto.inusual": ("Inusual", "Unusual"), "estado.corto.arriba": ("Sobre lo normal", "Above normal"),
    "estado.corto.normal": ("Normal", "Normal"), "estado.corto.abajo": ("Bajo lo normal", "Below normal"),
    "estado.corto.en_curso": ("En curso", "In progress"),
    "nav.ayuda": ("Ayuda", "Help"),
    "lateral.ayuda": ("No es un sistema de alerta. Cómo leer los gráficos: sección **Ayuda**.",
                      "Not a warning system. How to read the charts: **Help** section."),
    "area.aviso.corto": ("Área chica: números orientativos", "Small area: indicative numbers"),
    "tend.corta.sube": ("tendencia en alza", "upward trend"), "tend.corta.baja": ("tendencia en baja", "downward trend"),
    "tend.corta.nada": ("sin tendencia clara", "no clear trend"),
    "temp.corta": ("pico: {pico} · temporada: {temp}", "peak: {pico} · season: {temp}"),
    "tab.serie": ("Serie {desde}–{hasta}", "Series {desde}–{hasta}"),
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
}

MESES = {"es": ["ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic"],
         "en": ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]}
MESES_LARGOS = {"es": ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre",
                       "octubre", "noviembre", "diciembre"],
                "en": ["January", "February", "March", "April", "May", "June", "July", "August", "September",
                       "October", "November", "December"]}
