"""Spatial analysis: two maps side by side - one area in two years, or two areas in one year - with the same color
scale, so the comparison is fair; or the hot spots themselves as points, one satellite at a time. Fits one screen."""

import calendar
from datetime import date

import streamlit as st

from comun import cabecera, fecha_datos, mes, meta, num, serie, t
from mapas import CONFIG, SATELITES, datos_mapa, figura_focos, figura_mapa, focos_puntos, servicio_satelites
from tablero import CSS, alto_graficos

RESTO = 265  # everything on this view that is not a map (measured on screen)
EXTRA_FOCOS = 100  # hot spots map: no panel title above it nor note below it (they sit beside it)

cabecera()
st.markdown(CSS, unsafe_allow_html=True)
s = serie()
anio_max = int(s.anio.max())
anios = list(range(anio_max, 2002, -1))
provs = s[s.nivel == "provincia"].drop_duplicates("area_cod").sort_values("area")
zonas = [("00", t("area.todo_pais"))] + list(zip(provs.area_cod, provs.area))
codigos = [c for c, _ in zonas]
nombre_de = dict(zonas)
ALTO = alto_graficos(RESTO)
with st.sidebar:
    st.caption(t("geo.ayuda"))
    st.caption(t("datos.actualizado", fecha=fecha_datos()))

# defaults: the area chosen in the other views, and a contrast that tells a story (2020, the record year, vs. now)
base = st.session_state.get("prov_sel", "00")
st.session_state.setdefault("geo_modo", "anios")

c0, c1, c2, c3, c4 = st.columns([1.7, 1.3, 0.9, 1, 1.1], vertical_alignment="bottom")
with c0:
    st.markdown(f'<div class="area-titulo">{t("geo.titulo")}</div>', unsafe_allow_html=True)
    modo = st.segmented_control(t("geo.modo"), ["anios", "zonas", "focos"], key="geo_modo", label_visibility="collapsed",
                                format_func=lambda m: t(f"geo.modo.{m}")) or "anios"
if modo == "anios":
    with c1:
        z = st.selectbox(t("geo.zona"), codigos, index=codigos.index(base), format_func=nombre_de.get, key="geo_z")
    with c2:
        a1 = st.selectbox(t("geo.anio") + " A", anios, index=anios.index(2020), key="geo_a1")
    with c3:
        a2 = st.selectbox(t("geo.anio") + " B", anios, index=0, key="geo_a2")
    paneles = [(z, a1), (z, a2)]
elif modo == "zonas":
    with c1:
        a = st.selectbox(t("geo.anio"), anios, index=anios.index(anio_max - 1), key="geo_a")
    otra = "46" if base != "46" else "10"
    with c2:
        z1 = st.selectbox(t("geo.zona") + " A", codigos, index=codigos.index(base if base != "00" else "10"),
                          format_func=nombre_de.get, key="geo_z1")
    with c3:
        z2 = st.selectbox(t("geo.zona") + " B", codigos, index=codigos.index(otra), format_func=nombre_de.get,
                          key="geo_z2")
    paneles = [(z1, a), (z2, a)]

if modo == "focos":
    # one satellite at a time: raw detections are not harmonized (VIIRS sees ~5 times more than MODIS).
    # Controls, summary and note go in a side column: Argentina is tall and narrow, so the map is limited by height
    # and the width beside it was empty; the map gets the height of the panel title and the note.
    ua, um = meta()["ultimo_mes_completo"]
    serv = servicio_satelites()
    lado, der = st.columns([1, 3.3])
    with lado:
        zf = st.selectbox(t("geo.zona"), codigos, index=codigos.index(base), format_func=nombre_de.get, key="geo_zf")
        af = st.selectbox(t("geo.anio"), anios, index=0, key="geo_af")
        mf = st.selectbox(t("geo.mes"), list(range(0, 13)), index=um, key="geo_mf",
                          format_func=lambda m: t("geo.mes.todo") if m == 0 else mes(m, True).capitalize())
        sat = st.selectbox(t("geo.satelite"), list(SATELITES), index=0, format_func=SATELITES.get, key="geo_sat")
    ini = date(af, mf or 1, 1)
    fin = date(af, 12, 31) if mf == 0 else date(af, mf, calendar.monthrange(af, mf)[1])
    periodo = str(af) if mf == 0 else f"{mes(mf, True)} {af}"
    desde_s, hasta_s = serv.get(sat, (None, None))
    sin_datos = desde_s is None or fin < desde_s or ini > hasta_s
    with der.container(border=True):
        if sin_datos:
            otros = [SATELITES[p] for p, (a, b) in serv.items() if not (fin < a or ini > b)]
            st.info(t("geo.focos.sin", sat=SATELITES[sat], otros=", ".join(otros) if otros else "—"))
        else:
            f = focos_puntos(zf, ini, fin, sat)
            fig, densidad = figura_focos(zf, f, ini, ALTO + EXTRA_FOCOS, ancho_px=760)
            st.plotly_chart(fig, width="stretch", theme="streamlit", config=CONFIG, key="mapa_focos")
    with lado:
        st.markdown(f"**{nombre_de[zf]} · {periodo}**" + ("" if sin_datos else
                    f"<br>{SATELITES[sat]} · " + t("geo.focos.n", n=num(len(f)))), unsafe_allow_html=True,
                    help=t("geo.focos.ayuda"))
        if not sin_datos and densidad:
            st.caption(t("geo.focos.densidad").capitalize() + ".")
        st.caption(t("geo.focos.nota"))
else:
    datos = [datos_mapa(zc, an) for zc, an in paneles]
    zr = (min(g.zl.min() for g in datos), max(g.zl.max() for g in datos))  # one color scale for both maps
    cols = st.columns(2)
    for i, (col, (zc, an), g) in enumerate(zip(cols, paneles, datos)):
        with col.container(border=True):
            # the total comes from the area's own series (the same number as the cards in the other views); the map's
            # areas are converted one by one, so their sum differs slightly
            ua, um = meta()["ultimo_mes_completo"]
            nivel = "pais" if zc == "00" else "provincia"
            tot = s[(s.nivel == nivel) & (s.area_cod == zc) & (s.anio == an) & (s.mes <= (um if an == ua else 12))].valor.sum()
            st.markdown(f"**{nombre_de[zc]} · {an}** · " + t("geo.resumen", v=num(tot), d=num(1000 * tot / g.km2.sum(), 1)))
            st.plotly_chart(figura_mapa(g, ALTO, ancho_px=520, zrango=zr, barra=(i == 1)), width="stretch",
                            theme="streamlit", config=CONFIG, key=f"mapa_{i}")
