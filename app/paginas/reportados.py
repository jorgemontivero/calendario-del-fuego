"""Detected vs reported: the harmonized hot spots of an area next to the burned area its province reported to the
Ministry of Environment, year by year (the challenge asks for it explicitly). They measure different things - heat
seen from space vs hectares counted on the ground - so they are never put on one axis: two aligned bar charts, and
a scatter that compares their rankings (Spearman)."""

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots

from comun import CONFIG_GRAFICO, DATOS, NARANJA, cabecera, num, serie, t
from tablero import _tarjeta, alto_graficos, barra_lateral_final, filtros

RESTO = 245  # everything on this view that is not a chart (no controls row here; measured on screen)
GRIS_AZUL = "#64748B"


@st.cache_data
def oficial():
    return pd.read_parquet(DATOS / "oficial.parquet")


cabecera()
d, nombre, prov_cod, prov_nom, dep_cod = filtros()
ALTO = alto_graficos(RESTO)
s = serie()

# the official data are by province: a chosen department is compared through its province
area_cod, area_nom = prov_cod, (t("area.todo_pais") if prov_cod == "00" else prov_nom)
nivel = "pais" if prov_cod == "00" else "provincia"
focos = s[(s.nivel == nivel) & (s.area_cod == area_cod) & s.anio.between(2003, 2025)].groupby("anio").valor.sum()
of = oficial()
of = of[of.prov_cod == area_cod].set_index("anio")
x = pd.DataFrame({"focos": focos}).join(of[["ha", "fuente", "n_prov"]], how="left")
comp = x.dropna(subset=["ha"])
comp = comp[comp.ha > 0]

# ---------------------------------------------------------------------------------------------- cards
rho = comp[["focos", "ha"]].rank().corr().iloc[0, 1] if len(comp) >= 5 else np.nan
pico_f, pico_h = (int(comp.focos.idxmax()), int(comp.ha.idxmax())) if len(comp) else (None, None)
top3_f = set(comp.focos.nlargest(3).index)
top3_h = set(comp.ha.nlargest(3).index)
tarjetas = "".join([
    _tarjeta(t("rep.anios"), f"{len(comp)} ({comp.index.min()}–{comp.index.max()})" if len(comp) else "—",
             ayuda=t("rep.anios.ayuda")),
    _tarjeta(t("rep.rho"), num(rho, 2) if not np.isnan(rho) else "—", ayuda=t("rep.rho.ayuda")),
    _tarjeta(t("rep.picos"), f"{pico_f} · {pico_h}" if pico_f else "—", ayuda=t("rep.picos.ayuda")),
    _tarjeta(t("rep.top3"), t("rep.top3.valor", k=len(top3_f & top3_h)), ayuda=t("rep.top3.ayuda")),
])
c0, c1 = st.columns([1, 3.2], vertical_alignment="center")
with c0:
    st.markdown(f'<div class="area-titulo">{area_nom}</div>'
                + (f'<div class="area-sub">{t("rep.depto", dep=nombre)}</div>' if dep_cod else ""),
                unsafe_allow_html=True)
with c1:
    # "Correlación (ρ)" is short and "Pico de focos vs. pico de reportes" long: on wide screens the second card lends
    # width to the third (phones keep two cards per row, see tablero.CSS)
    st.markdown('<style>@media (min-width: 641px) {.st-key-tarj_rep .tarjeta:nth-child(2) {flex-grow: 0.7;}'
                '.st-key-tarj_rep .tarjeta:nth-child(3) {flex-grow: 1.3;}}</style>', unsafe_allow_html=True)
    with st.container(key="tarj_rep"):
        st.markdown(f'<div class="tarjetas">{tarjetas}</div>', unsafe_allow_html=True)

# ---------------------------------------------------------------------------------------------- charts
def marcas(v):
    """Round tick marks (1-2-5 per decade) for a log axis, instead of plotly's loose minor digits."""
    lo, hi = float(np.nanmin(v)), float(np.nanmax(v))
    cand = [m * 10 ** e for e in range(0, 9) for m in (1, 2, 5)]
    vals = [c for c in cand if lo / 1.5 <= c <= hi * 1.5]
    return dict(tickvals=vals, ticktext=[num(c / 1e6, 0) + "M" if c >= 1e6 else (num(c / 1e3, 0) + "k" if c >= 1e3
                                         else num(c)) for c in vals])


sep = ",." if st.query_params.get("lang") != "en" else ".,"
izq, der = st.columns([3, 2])
with izq.container(border=True):
    st.markdown(f"**{t('rep.titulo.barras')}**", help=t("rep.ayuda.barras"))
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.08,
                        subplot_titles=(t("rep.sub.focos"), t("rep.sub.ha")))
    fig.add_trace(go.Bar(x=x.index, y=x.focos, marker_color=NARANJA, name=t("rep.sub.focos"),
                         hovertemplate="%{x}: %{y:,.0f}<extra></extra>"), row=1, col=1)
    colores = np.where(x.fuente == "dt416", "#94A3B8", GRIS_AZUL)
    fig.add_trace(go.Bar(x=x.index, y=x.ha, marker_color=colores, name=t("rep.sub.ha"),
                         hovertemplate="%{x}: %{y:,.0f} ha<extra></extra>"), row=2, col=1)
    fig.update_layout(dragmode=False, height=ALTO, margin=dict(l=0, r=0, t=25, b=0), showlegend=False,
                      separators=sep)
    fig.update_annotations(font_size=12)
    st.plotly_chart(fig, width="stretch", theme="streamlit", config=CONFIG_GRAFICO)

with der.container(border=True):
    st.markdown(f"**{t('rep.titulo.disp')}** · ρ = {num(rho, 2) if not np.isnan(rho) else '—'}",
                help=t("rep.ayuda.disp"))
    f2 = go.Figure(go.Scatter(
        x=comp.focos, y=comp.ha, mode="markers+text", text=[str(a)[2:] for a in comp.index],
        textposition="top center", textfont=dict(size=9),
        marker=dict(size=9, color=np.where(comp.fuente == "dt416", "#94A3B8", NARANJA),
                    line=dict(width=1, color="white")),
        customdata=comp.index, hovertemplate="%{customdata}<br>%{x:,.0f} " + t("cal.hover.valor") +
                                             "<br>%{y:,.0f} ha<extra></extra>"))
    f2.update_layout(dragmode=False, height=ALTO, margin=dict(l=0, r=0, t=5, b=0), separators=sep,
                     xaxis=dict(type="log", title=t("rep.eje.focos"), **marcas(comp.focos)),
                     yaxis=dict(type="log", title=t("rep.eje.ha"), **marcas(comp.ha)))
    st.plotly_chart(f2, width="stretch", theme="streamlit", config=CONFIG_GRAFICO)

barra_lateral_final(d, nombre)
