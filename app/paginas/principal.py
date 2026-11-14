"""App, as a one-screen dashboard: the area in the sidebar, a row of indicators, and two tabs that each fit
without scrolling - the whole series (calendar | yearly totals) and one year (season | map)."""

import json
import math

import geopandas as gpd
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from comun import DATOS, NARANJA, cabecera, fecha_datos, meta, mes, num, pct, pie, serie, t

ALTO = 390  # height of every chart in the tabs, so each tab fits on one screen
st.markdown("""<style>
div[data-testid="stMetricValue"] {font-size: 1.7rem;}
div[data-testid="stMetric"] {padding: 0;}
.block-container h2 {margin-bottom: 0;}
</style>""", unsafe_allow_html=True)


@st.cache_data
def limites():
    return gpd.read_parquet(DATOS / "limites.parquet")


cabecera()
s = serie()
ua, um = meta()["ultimo_mes_completo"]
anio_max = int(s.anio.max())

# ================================================================================================ sidebar: the area
with st.sidebar:
    st.markdown(f"### {t('tab.filtros')}")
    provincias = s[s.nivel == "provincia"].drop_duplicates("area_cod").sort_values("area")
    opciones_p = [("00", t("area.todo_pais"))] + list(zip(provincias.area_cod, provincias.area))
    qp_prov = st.query_params.get("prov", "10")  # Catamarca by default: the local case
    idx_p = next((i for i, (c, _) in enumerate(opciones_p) if c == qp_prov), 0)
    prov_cod, prov_nom = st.selectbox(t("area.provincia"), opciones_p, index=idx_p, format_func=lambda o: o[1])
    dep_cod, dep_nom = None, None
    if prov_cod != "00":
        deps = s[(s.nivel == "departamento") & (s.prov_cod == prov_cod)].drop_duplicates("area_cod").sort_values("area")
        opciones_d = [(None, t("area.todos"))] + list(zip(deps.area_cod, deps.area))
        dep_cod, dep_nom = st.selectbox(t("area.departamento"), opciones_d, format_func=lambda o: o[1])
    st.query_params["prov"] = prov_cod
    st.divider()
    with st.expander(t("como_leer")):
        st.markdown(t("como_leer.texto"))
    with st.expander(t("foco.titulo")):
        st.markdown(t("foco.texto"))

if dep_cod:
    d = s[(s.nivel == "departamento") & (s.area_cod == dep_cod)]
    nombre = f"{dep_nom} ({prov_nom})"
elif prov_cod == "00":
    d = s[s.nivel == "pais"]
    nombre = t("area.todo_pais")
else:
    d = s[(s.nivel == "provincia") & (s.area_cod == prov_cod)]
    nombre = prov_nom
d = d.copy()

# ================================================================================================ title + KPI row
u = d[(d.anio == ua) & (d.mes == um)].iloc[0]
acum = d[(d.anio == ua) & (d.mes <= um)]
acum_v, acum_n = acum.valor.sum(), acum.normal.sum()
ICONO = {"inusual": "🔴", "arriba": "🟠", "normal": "⚪", "abajo": "🔵", "en_curso": "⏳"}


def delta(v, n):
    return None if not n else f"{num(100 * (v / n - 1))} % {t('kpi.vs_normal')}"


ayuda_mes = t("kpi.mes.ayuda")
if not np.isnan(u.min90):
    ayuda_mes += " " + t("ultimo.rango", li=num(u.min90), ls=num(u.max90))
t0, k1, k2, k3, k4 = st.columns([1.3, 1, 1, 1, 1], vertical_alignment="center")
with t0:
    st.markdown(f"## {nombre}")
    if d.mediana_anual.iloc[0] < 50:
        st.caption("⚠️ " + t("area.aviso.chica"))
with k1.container(border=True):
    st.metric(t("kpi.mes", mes=mes(um, True).capitalize(), anio=ua), num(u.valor), delta(u.valor, u.normal),
              delta_color="inverse", help=ayuda_mes)
with k2.container(border=True):
    st.metric(t("kpi.acum", anio=ua, mes=mes(um)), num(acum_v), delta(acum_v, acum_n), delta_color="inverse",
              help=t("kpi.acum.ayuda", mes=mes(um, True)))
with k3.container(border=True):
    st.metric(t("kpi.puesto", mes=mes(um)), t("ultimo.puesto.valor", k=num(u.puesto), n=num(u.n_anios)))
with k4.container(border=True):
    st.metric(t("kpi.estado"), f"{ICONO[u.estado]} {t('estado.' + u.estado)}",
              help=(t("ultimo.prob", p=pct(u.prob_inusual)) if not np.isnan(u.prob_inusual) else None))

tab_serie, tab_anio = st.tabs([f"📅 {t('tab.serie', desde=2003, hasta=anio_max)}", f"🗓️ {t('tab.un_anio')}"])

# ================================================================================================ tab 1: the whole series
with tab_serie:
    c1, c2 = st.columns([3, 2], vertical_alignment="bottom")
    with c1:
        desde, hasta = st.slider(t("area.anios"), 2003, anio_max, (2003, anio_max), label_visibility="collapsed")
    with c2:
        modo = st.segmented_control(t("cal.modo"), ["conteo", "anomalia"], default="conteo", label_visibility="collapsed",
                                    format_func=lambda m: t(f"cal.modo.{m}"), key="modo_cal") or "conteo"
    izq, der = st.columns([3, 2])
    with izq.container(border=True):
        st.markdown(f"**{t('panel.calendario')}** · {desde}–{hasta} · {t('cal.modo.' + modo).lower()}",
                    help=t("cal.unidad") + " " + t("armon.corta"))
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
            vmax = max(1.0, np.nanmax(Z))
            ticks = [v for v in [0, 1, 3, 10, 30, 100, 300, 1000, 3000, 10000, 30000] if math.log10(v + 1) <= vmax + 0.01]
            escala = dict(colorscale="YlOrRd", zmin=0, zmax=vmax,
                          colorbar=dict(title=t("cal.leyenda.focos"), tickvals=[math.log10(v + 1) for v in ticks],
                                        ticktext=[num(v) for v in ticks], thickness=10))
        else:
            escala = dict(colorscale="RdBu_r", zmid=0, zmin=-3, zmax=3,
                          colorbar=dict(title=t("cal.leyenda.veces"), tickvals=[-3, -2, -1, 0, 1, 2, 3],
                                        ticktext=["≤⅛", "¼", "½", "1", "2", "4", "≥8"], thickness=10))
        fig = go.Figure(go.Heatmap(z=Z, x=[mes(m).capitalize() for m in range(1, 13)], y=[str(a) for a in anios],
                                   text=H, hoverinfo="text", xgap=1.5, ygap=1.5, **escala))
        fig.update_layout(height=ALTO, margin=dict(l=0, r=0, t=5, b=0),
                          yaxis=dict(type="category", autorange="reversed", tickfont=dict(size=10)), xaxis=dict(side="top"))
        st.plotly_chart(fig, width="stretch", theme="streamlit")

    with der.container(border=True):
        anual_s = d[d.anio.between(2003, 2025)].groupby("anio").valor.sum().to_numpy()
        n = len(anual_s)
        S = sum(np.sign(anual_s[j] - anual_s[i]) for i in range(n - 1) for j in range(i + 1, n))
        z = (S - np.sign(S)) / math.sqrt(n * (n - 1) * (2 * n + 5) / 18) if S else 0.0
        tend = "temp.tendencia.sube" if z > 1.96 else "temp.tendencia.baja" if z < -1.96 else "temp.tendencia.nada"
        corta = {"temp.tendencia.sube": "tend.corta.sube", "temp.tendencia.baja": "tend.corta.baja"}.get(tend, "tend.corta.nada")
        st.markdown(f"**{t('anual.titulo')}** · {t(corta)}",
                    help=t(tend) + " " + t("anual.ayuda", anio=anio_max) + " " + t("armon.corta"))
        an = d[d.anio.between(desde, hasta)].groupby("anio").agg(
            v=("valor", "sum"), lo=("min90", "sum"), hi=("max90", "sum"), o=("origen", "first")).reset_index()
        conv = an.o != "aqua"
        colores = np.where(an.anio == anio_max, NARANJA, np.where(conv, "#FB923C", "#FDBA74"))
        f3 = go.Figure(go.Bar(x=an.anio, y=an.v, marker_color=colores, hovertemplate="%{x}: %{y:,.0f}<extra></extra>",
                              error_y=dict(type="data", symmetric=False, array=np.where(conv, an.hi - an.v, 0),
                                           arrayminus=np.where(conv, an.v - an.lo, 0), thickness=1.2, width=0)))
        f3.update_layout(height=ALTO, margin=dict(l=0, r=0, t=5, b=0), yaxis_title=t("cal.leyenda.focos"),
                         separators=",." if st.query_params.get("lang") != "en" else ".,")
        st.plotly_chart(f3, width="stretch", theme="streamlit")

# ================================================================================================ tab 2: one year
with tab_anio:
    c1, c2 = st.columns([1, 4], vertical_alignment="center")
    with c1:
        anio_sel = st.selectbox(t("tab.anio"), list(range(anio_max, 2002, -1)), key="anio_sel", label_visibility="collapsed")
    izq, der = st.columns(2)
    with izq.container(border=True):
        ref = d[d.anio.between(2003, 2022)]
        q = ref.groupby("mes").valor.quantile([0.1, 0.5, 0.9]).unstack()
        med = q[0.5]
        orden = med.sort_values(ascending=False)
        cum = orden.cumsum() / max(orden.sum(), 1e-9)
        temporada = sorted(orden.index[: int((cum < 0.8).sum()) + 1])
        # the season as a range (jul–nov) when its months are consecutive, also across December
        cons = [m for m in temporada]
        inicio = next((m for m in cons if (m - 2) % 12 + 1 not in cons), cons[0])
        corrido = len(cons) == len({(inicio - 1 + k) % 12 + 1 for k in range(len(cons))} & set(cons))
        temp_txt = f"{mes(inicio)}–{mes((inicio - 1 + len(cons) - 1) % 12 + 1)}" if corrido and len(cons) > 1             else ", ".join(mes(m) for m in cons)
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
        st.plotly_chart(f4, width="stretch", theme="streamlit")

# ================================================================================================ below the fold
csv = pd.DataFrame({
    "area": nombre, "year": d.anio, "month": d.mes, "hotspots": d.valor, "lo90": d.min90, "hi90": d.max90,
    "median_month": d.normal, "p90_month": d.p90, "rank": d.puesto, "n_years": d.n_anios,
    "unusual": (d.estado == "inusual").astype(int), "status": d.estado, "complete_month": d.mes_completo.astype(int),
    "source": d.origen})
with st.sidebar:
    st.download_button("⬇️ " + t("desc.serie"), csv.to_csv(index=False).encode("utf-8"),
                       file_name=f"calendario_del_fuego_{nombre.replace(' ', '_')}.csv", mime="text/csv", width="stretch")
    st.caption(t("desc.texto"))
    with st.expander(t("desc.citar")):
        st.code(t("cita"), language=None)
if len(d[~d.mes_completo]):
    st.caption(t("en_curso", fecha=fecha_datos()))
pie()
