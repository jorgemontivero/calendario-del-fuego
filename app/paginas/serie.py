"""View 1 - the whole series: calendar (year x month) and yearly totals, side by side, on one screen."""

import math

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from comun import CONFIG_GRAFICO, NARANJA, cabecera, fecha_datos, mes, num, serie, t
import html

from tablero import alto_graficos, barra_lateral_final, encabezado, filtros, frase_resumen

RESTO = 345  # everything on this view that is not a chart (measured on screen)

cabecera()
d, nombre, prov_cod, prov_nom, dep_cod = filtros()
ALTO = alto_graficos(RESTO)
ALTO_SELECTOR = 23  # the calendar title row also holds the count / vs-normal switch: that much taller (measured)
anio_max = int(serie().anio.max())
encabezado(d, nombre)
_frase = html.escape(frase_resumen(d))
st.markdown(f'<div class="resumen" title="{_frase}">{_frase}</div>', unsafe_allow_html=True)

c1, _ = st.columns([3, 2], vertical_alignment="center")
with c1:
    # The range zooms both charts below; the cards above always describe the latest months. The label sits beside
    # the slider (not above it) so the view keeps its height.
    e1, e2 = st.columns([1, 3.2], vertical_alignment="center")
    e1.markdown(f'<div class="area-sub" style="opacity:0.85">{html.escape(t("area.anios.graficos"))}</div>',
                unsafe_allow_html=True)
    with e2:
        desde, hasta = st.slider(t("area.anios.graficos"), 2003, anio_max, (2003, anio_max), label_visibility="collapsed")

izq, der = st.columns([3, 2])
with izq.container(border=True):
    # count / compared-with-normal only changes the calendar, so it lives in the calendar's own title row
    t1, t2 = st.columns([1, 1.7], vertical_alignment="center")
    # compact buttons, so this title row is no taller than the bar chart's and both panels stay aligned
    st.markdown("<style>.st-key-modo_cal {margin-left: auto;}"
                ".st-key-modo_cal button {min-height: 0; padding: 0.1rem 0.65rem; font-size: 0.85rem;}</style>",
                unsafe_allow_html=True)
    with t2:
        modo = st.segmented_control(t("cal.modo"), ["conteo", "anomalia"], default="conteo", label_visibility="collapsed",
                                    format_func=lambda m: t(f"cal.modo.{m}"), key="modo_cal", width="content") or "conteo"
    t1.markdown(f"**{t('panel.calendario')}** · {desde}–{hasta}",
                help=t("cal.unidad") + " " + t("armon.corta") + " " + t("en_curso", fecha=fecha_datos()))
    dd = d[d.anio.between(desde, hasta)]
    anios = list(range(hasta, desde - 1, -1))
    Z = np.full((len(anios), 12), np.nan)
    H = np.full((len(anios), 12), "", dtype=object)
    for r in dd.itertuples():
        i, j = anios.index(r.anio), r.mes - 1
        if modo == "conteo":
            Z[i, j] = math.log10(r.valor + 1)
        else:
            Z[i, j] = np.clip(math.log2((r.valor + 1) / (r.normal + 1)), -3, 3) if r.mes_completo else np.nan
        partes = [f"<b>{mes(r.mes, True).capitalize()} {r.anio}</b>", f"{num(r.valor)} {t('cal.hover.valor')}"]
        if not np.isnan(r.min90):
            partes.append(f"{t('cal.hover.rango')}: {num(r.min90)}–{num(r.max90)}")
        partes.append(f"{t('cal.hover.normal')}: {num(r.normal)}")
        if r.mes_completo and not np.isnan(r.puesto):
            partes.append(t("cal.hover.puesto", k=num(r.puesto), n=num(r.n_anios)))
        partes.append(t("estado." + r.estado))
        partes.append(t({"aqua": "fuente.aqua", "snpp_converted": "fuente.snpp", "noaa20_converted": "fuente.noaa20"}[r.origen]))
        H[i, j] = "<br>".join(partes)
    if modo == "conteo":
        # the color range follows the area: from its lowest months to its highest (all of Argentina never goes
        # below a few hundred a month; starting at 0 painted every month red)
        vmax = max(1.0, np.nanmax(Z))
        vmin = min(max(0.0, np.nanpercentile(Z, 2)), vmax - 0.5)
        ticks = [v for v in [0, 1, 3, 10, 30, 100, 300, 1000, 3000, 10000, 30000]
                 if vmin - 0.01 <= math.log10(v + 1) <= vmax + 0.01]
        escala = dict(colorscale="YlOrRd", zmin=vmin, zmax=vmax,
                      colorbar=dict(title=t("cal.leyenda.focos"), tickvals=[math.log10(v + 1) for v in ticks],
                                    ticktext=[num(v) for v in ticks], thickness=10))
    else:
        escala = dict(colorscale="RdBu_r", zmid=0, zmin=-3, zmax=3,
                      colorbar=dict(title=t("cal.leyenda.veces"), tickvals=[-3, -2, -1, 0, 1, 2, 3],
                                    ticktext=["≤⅛", "¼", "½", "1", "2", "4", "≥8"], thickness=10))
    fig = go.Figure(go.Heatmap(z=Z, x=[mes(m).capitalize() for m in range(1, 13)], y=[str(a) for a in anios],
                               text=H, hoverinfo="text", xgap=1.5, ygap=1.5, **escala))
    fig.update_layout(dragmode=False, height=ALTO - ALTO_SELECTOR, margin=dict(l=0, r=0, t=5, b=0),
                      yaxis=dict(type="category", autorange="reversed", tickfont=dict(size=10)), xaxis=dict(side="top"))
    st.plotly_chart(fig, width="stretch", theme="streamlit", config=CONFIG_GRAFICO)

with der.container(border=True):
    a1, a2 = st.columns([1, 1], vertical_alignment="center")
    st.markdown("<style>.st-key-modo_anual {margin-left: auto;}"
                ".st-key-modo_anual button {min-height: 0; padding: 0.1rem 0.65rem; font-size: 0.85rem;}</style>",
                unsafe_allow_html=True)
    with a2:
        vista = st.segmented_control(t("anual.modo"), ["anio", "mes"], default="anio", label_visibility="collapsed",
                                     format_func=lambda v: t(f"anual.modo.{v}"), key="modo_anual", width="content") or "anio"
    sep = ",." if st.query_params.get("lang") != "en" else ".,"
    if vista == "mes":
        # the yearly chart's twin: average hot spots of each month of the year, over the years in the range
        # (complete months only: the month in progress would pull its average down)
        dm = d[d.anio.between(desde, hasta) & d.mes_completo]
        g = dm.groupby("mes").valor
        pm = pd.DataFrame({"media": g.mean(), "mediana": g.median(), "n": g.size(),
                           "maximo": g.max(), "anio_max": dm.loc[g.idxmax(), "anio"].to_numpy()}).reindex(range(1, 13))
        a1.markdown(f"**{t('mes.titulo')}**", help=t("mes.ayuda") + " " + t("armon.corta"))
        pico = pm.media.idxmax() if pm.media.notna().any() else None
        colores = [NARANJA if m == pico else "#FB923C" for m in pm.index]
        def _hover(m, r):
            if not r.n == r.n or r.n == 0:  # no complete month in the range (Nov-Dec of the current year)
                return f"<b>{mes(m, True).capitalize()}</b><br>{t('mes.sin')}"
            if desde == hasta:  # one year: its own count, nothing to average
                return f"<b>{mes(m, True).capitalize()} {desde}</b><br>{num(r.media)} {t('cal.hover.valor')}"
            return t("mes.hover", mes=mes(m, True).capitalize(), v=num(r.media), md=num(r.mediana), n=num(r.n),
                     mx=num(r.maximo), a=int(r.anio_max))
        hover = [_hover(m, r) for m, r in pm.iterrows()]
        f3 = go.Figure(go.Bar(x=[mes(m).capitalize() for m in pm.index], y=pm.media, marker_color=colores,
                              hovertext=hover, hoverinfo="text"))
        f3.add_annotation(text=t("mes.nota", d=desde, h=hasta) if desde < hasta else str(desde), xref="paper", yref="paper", x=1, y=1,
                          xanchor="right", yanchor="top", showarrow=False, font=dict(size=12), opacity=0.8)
        f3.update_layout(dragmode=False, height=ALTO - ALTO_SELECTOR, margin=dict(l=0, r=0, t=5, b=0),
                         yaxis_title=t("mes.eje"), separators=sep)
        st.plotly_chart(f3, width="stretch", theme="streamlit", config=CONFIG_GRAFICO)
    else:
        anual_s = d[d.anio.between(2003, 2025)].groupby("anio").valor.sum().to_numpy()
        n = len(anual_s)
        S = sum(np.sign(anual_s[j] - anual_s[i]) for i in range(n - 1) for j in range(i + 1, n))
        z = (S - np.sign(S)) / math.sqrt(n * (n - 1) * (2 * n + 5) / 18) if S else 0.0
        tend = "temp.tendencia.sube" if z > 1.96 else "temp.tendencia.baja" if z < -1.96 else "temp.tendencia.nada"
        corta = {"temp.tendencia.sube": "tend.corta.sube", "temp.tendencia.baja": "tend.corta.baja"}.get(tend, "tend.corta.nada")
        a1.markdown(f"**{t('anual.titulo')}**",
                    help=t(tend) + " " + t("anual.ayuda", anio=anio_max) + " " + t("armon.corta"))
        an = d[d.anio.between(desde, hasta)].groupby("anio").agg(
            v=("valor", "sum"), lo=("min90", "sum"), hi=("max90", "sum"), o=("origen", "first")).reset_index()
        conv = an.o != "aqua"
        colores = np.where(an.anio == anio_max, NARANJA, np.where(conv, "#FB923C", "#FDBA74"))
        f3 = go.Figure(go.Bar(x=an.anio, y=an.v, marker_color=colores, hovertemplate="%{x}: %{y:,.0f}<extra></extra>",
                              error_y=dict(type="data", symmetric=False, array=np.where(conv, an.hi - an.v, 0),
                                           arrayminus=np.where(conv, an.v - an.lo, 0), thickness=1.2, width=0)))
        # the trend goes inside the chart: next to the switch, the title row has room for a short title only
        f3.add_annotation(text=t(corta).capitalize() + " · 2003–2025", xref="paper", yref="paper", x=1, y=1,
                          xanchor="right", yanchor="top", showarrow=False, font=dict(size=12), opacity=0.8)
        f3.update_layout(dragmode=False, height=ALTO - ALTO_SELECTOR, margin=dict(l=0, r=0, t=5, b=0), yaxis_title=t("cal.leyenda.focos"),
                         separators=sep)
        st.plotly_chart(f3, width="stretch", theme="streamlit", config=CONFIG_GRAFICO)

barra_lateral_final(d, nombre)
