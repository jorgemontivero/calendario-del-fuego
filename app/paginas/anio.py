"""View 2 - one year chosen by the user: the season (that year against a typical year) and the map of fire per
1,000 km2, side by side, on one screen."""

import json
import math

import geopandas as gpd
import numpy as np
import plotly.graph_objects as go
import streamlit as st

from comun import DATOS, NARANJA, cabecera, mes, num, serie, t
from tablero import alto_graficos, barra_lateral_final, encabezado, filtros

RESTO = 300  # everything on this view that is not a chart (measured on screen)


@st.cache_data
def limites():
    return gpd.read_parquet(DATOS / "limites.parquet")


cabecera()
s = serie()
d, nombre, prov_cod, prov_nom, dep_cod = filtros()
ALTO = alto_graficos(RESTO)
anio_max = int(s.anio.max())
encabezado(d, nombre)

anios = list(range(anio_max, 2002, -1))
if "anio_sel_v" not in st.session_state:
    st.session_state["anio_sel_v"] = anio_max
c1, _ = st.columns([1, 5], vertical_alignment="center")
with c1:
    anio_sel = st.selectbox(t("tab.anio"), anios, index=anios.index(st.session_state["anio_sel_v"]),
                            label_visibility="collapsed")
st.session_state["anio_sel_v"] = anio_sel

izq, der = st.columns(2)
with izq.container(border=True):
    ref = d[d.anio.between(2003, 2022)]
    q = ref.groupby("mes").valor.quantile([0.1, 0.5, 0.9]).unstack()
    med = q[0.5]
    orden = med.sort_values(ascending=False)
    cum = orden.cumsum() / max(orden.sum(), 1e-9)
    temporada = sorted(orden.index[: int((cum < 0.8).sum()) + 1])
    # the season as a range (jul–nov) when its months are consecutive, also across December
    inicio = next((m for m in temporada if (m - 2) % 12 + 1 not in temporada), temporada[0])
    corrido = set(temporada) == {(inicio - 1 + k) % 12 + 1 for k in range(len(temporada))}
    temp_txt = (f"{mes(inicio)}–{mes((inicio - 1 + len(temporada) - 1) % 12 + 1)}" if corrido and len(temporada) > 1
                else ", ".join(mes(m) for m in temporada))
    st.markdown(f"**{t('panel.temporada')} · {anio_sel}** · {t('temp.corta', pico=mes(int(med.idxmax())), temp=temp_txt)}",
                help=t("temp.temporada.ayuda"))
    ac = d[d.anio == anio_sel].sort_values("mes")
    x = [mes(m).capitalize() for m in range(1, 13)]
    f2 = go.Figure()
    f2.add_trace(go.Scatter(x=x, y=q[0.9], mode="lines", line=dict(width=0), showlegend=False, hoverinfo="skip"))
    f2.add_trace(go.Scatter(x=x, y=q[0.1], mode="lines", fill="tonexty", line=dict(width=0),
                            fillcolor="rgba(128,128,128,0.25)", name=t("temp.banda"), hoverinfo="skip"))
    f2.add_trace(go.Scatter(x=x, y=med, mode="lines", line=dict(color="gray", dash="dash"), name=t("temp.mediana")))
    xa = [mes(m).capitalize() for m in ac.mes]
    if ac.min90.notna().any():
        f2.add_trace(go.Scatter(x=xa, y=ac.max90, mode="lines", line=dict(width=0), showlegend=False, hoverinfo="skip"))
        f2.add_trace(go.Scatter(x=xa, y=ac.min90, mode="lines", fill="tonexty", line=dict(width=0),
                                fillcolor="rgba(194,65,12,0.2)", showlegend=False, hoverinfo="skip"))
    f2.add_trace(go.Scatter(x=xa, y=ac.valor, line=dict(color=NARANJA, width=3), mode="lines+markers", name=str(anio_sel)))
    f2.update_layout(height=ALTO, margin=dict(l=0, r=0, t=5, b=0),
                     legend=dict(orientation="h", y=1.02, yanchor="bottom", font=dict(size=10)),
                     yaxis_title=t("cal.leyenda.focos"))
    st.plotly_chart(f2, width="stretch", theme="streamlit")

with der.container(border=True):
    lim = limites()
    if prov_cod == "00":
        geo = lim[lim.nivel == "provincia"]
        val = s[(s.nivel == "provincia") & (s.anio == anio_sel)].groupby("area_cod").valor.sum()
        titulo_area = t("area.todo_pais")
    else:
        geo = lim[(lim.nivel == "departamento") & (lim.prov_cod == prov_cod)]
        val = s[(s.nivel == "departamento") & (s.prov_cod == prov_cod) & (s.anio == anio_sel)].groupby("area_cod").valor.sum()
        titulo_area = prov_nom
    geo = geo[geo.km2 > 0].copy()
    geo["valor"] = geo.area_cod.map(val).fillna(0)
    geo["dens"] = 1000 * geo.valor / geo.km2
    st.markdown(f"**{t('mapa.titulo.dep', area=titulo_area, anio=anio_sel)}**", help=t("mapa.ayuda"))
    gj = json.loads(geo[["area_cod", "geometry"]].to_json())
    zl = np.log10(geo.dens + 0.1)
    ticks = [v for v in [0.1, 0.3, 1, 3, 10, 30, 100, 300] if zl.min() - 0.3 <= math.log10(v + 0.1) <= zl.max() + 0.3]
    f4 = go.Figure(go.Choropleth(
        geojson=gj, featureidkey="properties.area_cod", locations=geo.area_cod, z=zl, colorscale="YlOrRd",
        marker_line_width=[2.5 if c == dep_cod else 0.4 for c in geo.area_cod],
        marker_line_color=["#111827" if c == dep_cod else "white" for c in geo.area_cod],
        customdata=np.stack([geo["area"], geo.valor.round(0), geo.dens.round(1)], axis=1),
        hovertemplate="<b>%{customdata[0]}</b><br>%{customdata[1]} " + t("cal.hover.valor") +
                      "<br>%{customdata[2]} " + t("mapa.leyenda") + "<extra></extra>",
        colorbar=dict(title=t("mapa.leyenda"), tickvals=[math.log10(v + 0.1) for v in ticks],
                      ticktext=[num(v, 1 if v < 1 else 0) for v in ticks], thickness=10)))
    f4.update_geos(fitbounds="locations", visible=False)
    f4.update_layout(height=ALTO, margin=dict(l=0, r=0, t=0, b=0), geo=dict(bgcolor="rgba(0,0,0,0)"))
    st.plotly_chart(f4, width="stretch", theme="streamlit", config={"displayModeBar": False})

barra_lateral_final(d, nombre)
