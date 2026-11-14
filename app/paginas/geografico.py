"""Geographic analysis: two maps side by side - one area in two years, or two areas in one year - with the same color
scale, so the comparison is fair. Fits one screen."""

import streamlit as st

from comun import cabecera, fecha_datos, meta, num, serie, t
from mapas import CONFIG, datos_mapa, figura_mapa
from tablero import CSS, alto_graficos

RESTO = 265  # everything on this view that is not a map (measured on screen)

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

c0, c1, c2, c3 = st.columns([1.6, 1.3, 1, 1], vertical_alignment="bottom")
with c0:
    st.markdown(f'<div class="area-titulo">{t("geo.titulo")}</div>', unsafe_allow_html=True)
    modo = st.segmented_control(t("geo.modo"), ["anios", "zonas"], key="geo_modo", label_visibility="collapsed",
                                format_func=lambda m: t(f"geo.modo.{m}")) or "anios"
if modo == "anios":
    with c1:
        z = st.selectbox(t("geo.zona"), codigos, index=codigos.index(base), format_func=nombre_de.get, key="geo_z")
    with c2:
        a1 = st.selectbox(t("geo.anio") + " A", anios, index=anios.index(2020), key="geo_a1")
    with c3:
        a2 = st.selectbox(t("geo.anio") + " B", anios, index=0, key="geo_a2")
    paneles = [(z, a1), (z, a2)]
else:
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
