"""View 2 - one year chosen by the user: the season (that year against a typical year) and where fire concentrated
(areas ranked, colored against their own normal), side by side, on one screen."""

import numpy as np
import plotly.graph_objects as go
import streamlit as st

from comun import CONFIG_GRAFICO, NARANJA, cabecera, mes, num, serie, t
from mapas import ranking
from tablero import alto_graficos, barra_lateral_final, encabezado, filtros

RESTO = 300  # everything on this view that is not a chart (measured on screen)


cabecera()
s = serie()
d, nombre, prov_cod, prov_nom, dep_cod = filtros()
ALTO = alto_graficos(RESTO)
anio_max = int(s.anio.max())
# The chosen year lives in session_state (kept across views) and is updated by the selector's callback, which runs
# before the page is drawn: the cards above the selector and the charts below always show the same year.
anios = list(range(anio_max, 2002, -1))
if "anio_sel_v" not in st.session_state:
    st.session_state["anio_sel_v"] = anio_max


def _cambiar_anio():
    st.session_state["anio_sel_v"] = st.session_state["anio_sel_w"]


anio_sel = st.session_state["anio_sel_v"]
encabezado(d, nombre, anio=anio_sel)
c1, _ = st.columns([1, 5], vertical_alignment="center")
with c1:
    st.selectbox(t("tab.anio"), anios, index=anios.index(anio_sel), key="anio_sel_w", on_change=_cambiar_anio,
                 label_visibility="collapsed")

izq, der = st.columns(2)
with izq.container(border=True):
    ref = d[d.anio.between(2003, 2022)]
    q = ref.groupby("mes").valor.quantile([0.1, 0.5, 0.9]).unstack()
    med = q[0.5]
    orden = med.sort_values(ascending=False)
    cum = orden.cumsum() / max(orden.sum(), 1e-9)
    temporada = sorted(orden.index[: int((cum < 0.8).sum()) + 1])
    # the season as runs of consecutive months ("ene, jul–nov"; a run can cross December), so the title fits one line
    resto = set(temporada)
    tramos = []
    for m0 in sorted(temporada, key=lambda m: ((m - 2) % 12 + 1) in temporada):  # run starts first
        if m0 not in resto or ((m0 - 2) % 12 + 1) in resto:
            continue
        fin = m0
        while (fin % 12 + 1) in resto and (fin % 12 + 1) != m0:
            fin = fin % 12 + 1
        k = m0
        while True:
            resto.discard(k)
            if k == fin:
                break
            k = k % 12 + 1
        tramos.append((m0, fin))
    if resto:  # all twelve months: no run start
        tramos = [(1, 12)]
    temp_txt = ", ".join(mes(a) if a == b else f"{mes(a)}–{mes(b)}" for a, b in sorted(tramos))
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
    f2.update_layout(dragmode=False, height=ALTO, margin=dict(l=0, r=0, t=5, b=0),
                     legend=dict(orientation="h", y=1.02, yanchor="bottom", font=dict(size=10)),
                     yaxis_title=t("cal.leyenda.focos"))
    st.plotly_chart(f2, width="stretch", theme="streamlit", config=CONFIG_GRAFICO)

with der.container(border=True):
    # Where fire concentrated in the chosen year: the areas with most hot spots, each colored by how far it was from
    # its own normal (median of its 2003-2022 totals for the same months). The map moved to Geographic analysis.
    r = ranking(prov_cod, anio_sel).iloc[::-1]  # largest on top
    st.markdown(f"**{t('rank.titulo', anio=anio_sel)}** · "
                f"{t('rank.provincias', n=len(r)) if prov_cod == '00' else t('rank.departamentos', n=len(r), prov=prov_nom)}",
                help=t("rank.ayuda"))
    lr = np.clip(np.log2(r.razon), -2, 2)
    etiquetas = [f"{num(v)} ({'+' if v >= n else '−'}{num(abs(100 * (v / n - 1)))} %)" if n > 0 else num(v)
                 for v, n in zip(r.valor, r.normal)]
    nombres = [f"<b>{a}</b>" if c == dep_cod else a for a, c in zip(r.area, r.area_cod)]
    f4 = go.Figure(go.Bar(
        x=r.valor, y=nombres, orientation="h", text=etiquetas, textposition="outside", cliponaxis=False,
        marker=dict(color=lr, colorscale="RdBu_r", cmin=-2, cmax=2, showscale=False),
        customdata=np.stack([r.normal.round(0)], axis=1),
        hovertemplate="<b>%{y}</b><br>%{x:,.0f} " + t("cal.hover.valor") + "<br>" + t("cal.hover.normal") +
                      ": %{customdata[0]:,.0f}<extra></extra>"))
    f4.update_layout(dragmode=False, height=ALTO, margin=dict(l=0, r=10, t=5, b=0), xaxis_title=t("cal.leyenda.focos"),
                     xaxis=dict(range=[0, float(r.valor.max()) * 1.45]),
                     separators=",." if st.query_params.get("lang") != "en" else ".,")
    st.plotly_chart(f4, width="stretch", theme="streamlit", config=CONFIG_GRAFICO)

barra_lateral_final(d, nombre)
