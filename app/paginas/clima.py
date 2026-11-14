"""Climate and fire: does a dry month come with more fire? Anomalies - how far each month was from normal for that
month of the year - of fire (harmonized series) and of climate (NASA POWER), fire-season months only. Without
anomalies both follow the seasons and the correlation only says that winter exists. Fits one screen."""

import numpy as np
import plotly.graph_objects as go
import streamlit as st

from comun import CONFIG_GRAFICO, NARANJA, cabecera, clima, meta, mes, num, oscuro, t
from tablero import _tarjeta, alto_graficos, barra_lateral_final, filtros

RESTO = 300  # everything on this view that is not a chart (measured on screen)
VARS = {  # variable -> (column, kind of anomaly, which side is "dry/hot")
    "humedad": ("humedad", "dif", "bajo"),
    "lluvia3": ("lluvia_prev3", "log", "bajo"),
    "lluvia6": ("lluvia_prev6", "log", "bajo"),
    "temp": ("temp_max", "dif", "alto"),
}
AZUL_T, GRIS_T = "#2563EB", "#9CA3AF"

cabecera()
d, nombre, prov_cod, prov_nom, dep_cod = filtros()
ALTO = alto_graficos(RESTO)
ua, um = meta()["ultimo_mes_completo"]

c_t, c_v = st.columns([1.1, 4.3], vertical_alignment="center")
with c_t:
    st.markdown(f'<div class="area-titulo">{nombre}</div>'
                + (f'<div class="area-sub">{t("clima.depto", prov=prov_nom)}</div>' if dep_cod else ""),
                unsafe_allow_html=True)
with c_v:
    var = st.segmented_control(t("clima.variable"), list(VARS), default="humedad", key="clima_var",
                               label_visibility="collapsed", format_func=lambda v: t(f"clima.var.{v}")) or "humedad"
col, tipo, lado = VARS[var]

# fire (the chosen area) and climate (its province, or the country)
f = d[d.mes_completo & d.anio.between(2003, ua)][["anio", "mes", "valor", "normal"]]
cl = clima()
cl = cl[cl.prov_cod == prov_cod][["anio", "mes", col]]
x = f.merge(cl, on=["anio", "mes"]).dropna(subset=[col])
ref = x[x.anio.between(2003, 2022)]
x = x.merge(ref.groupby("mes")[col].median().rename("clim_n"), on="mes")

# fire-season months: those holding 80 % of a typical year's fire
med = ref.groupby("mes").valor.median().sort_values(ascending=False)
acum = med.cumsum() / max(med.sum(), 1e-9)
temporada = set(med.index[: int((acum < 0.8).sum()) + 1])
x = x[x.mes.isin(temporada)].copy()
x["af"] = np.log((x.valor + 1) / (x.normal + 1))  # fire anomaly (log ratio to its normal)
x["ac"] = (np.log((x[col] + 1) / (x.clim_n + 1)) if tipo == "log" else x[col] - x.clim_n)
rho = x[["af", "ac"]].rank().corr().iloc[0, 1] if len(x) >= 10 else np.nan

# terciles of the climate anomaly; "dry" = low humidity/rain, "hot" = high temperature
q1, q2 = x.ac.quantile([1 / 3, 2 / 3])
x["tercil"] = np.where(x.ac <= q1, "bajo", np.where(x.ac >= q2, "alto", "medio"))
seco, humedo = (("bajo", "alto") if lado == "bajo" else ("alto", "bajo"))
p_seco = (x[x.tercil == seco].af > 0).mean() if (x.tercil == seco).any() else np.nan
p_hum = (x[x.tercil == humedo].af > 0).mean() if (x.tercil == humedo).any() else np.nan

et_seco, et_hum = t(f"clima.ter.{var}.seco"), t(f"clima.ter.{var}.humedo")
tarjetas = "".join([
    _tarjeta(t("clima.rho"), num(rho, 2) if not np.isnan(rho) else "—", ayuda=t("clima.rho.ayuda")),
    _tarjeta(t("clima.n"), num(len(x)),
             ayuda=t("clima.n.ayuda") + " " + t("clima.n.meses", m=", ".join(mes(m) for m in sorted(temporada)))),
    _tarjeta(t("clima.p", ter=et_seco), f"{num(100 * p_seco)} %" if not np.isnan(p_seco) else "—",
             ayuda=t("clima.p.ayuda", ter=et_seco)),
    _tarjeta(t("clima.p", ter=et_hum), f"{num(100 * p_hum)} %" if not np.isnan(p_hum) else "—",
             ayuda=t("clima.p.ayuda", ter=et_hum)),
])
st.markdown(f'<div class="tarjetas" style="margin-top:0.3rem">{tarjetas}</div>', unsafe_allow_html=True)

# ---------------------------------------------------------------------------------------------- charts
sep = ",." if st.query_params.get("lang") != "en" else ".,"
eje_x = t(f"clima.eje.{var}")
ticks_y = dict(tickvals=[np.log(v) for v in (0.25, 0.5, 1, 2, 4, 8)], ticktext=["¼", "½", "1", "2", "4", "8"])
izq, der = st.columns([3, 2])
with izq.container(border=True):
    st.markdown(f"**{t('clima.titulo.disp')}** · ρ = {num(rho, 2) if not np.isnan(rho) else '—'}",
                help=t("clima.ayuda.disp"))
    ultimo_anio = int(x.anio.max()) if len(x) else ua
    reciente = x.anio == ultimo_anio
    f1 = go.Figure()
    f1.add_trace(go.Scatter(x=x.ac[~reciente], y=x.af[~reciente], mode="markers", name="2003–" + str(ultimo_anio - 1),
                            marker=dict(size=6, color="rgba(251,146,60,0.55)" if oscuro() else "rgba(194,65,12,0.35)"),
                            customdata=np.stack([x.anio[~reciente], x.mes[~reciente].map(lambda m: mes(m))], axis=1),
                            hovertemplate="%{customdata[1]} %{customdata[0]}<extra></extra>"))
    f1.add_trace(go.Scatter(x=x.ac[reciente], y=x.af[reciente], mode="markers+text", name=str(ultimo_anio),
                            text=x.mes[reciente].map(lambda m: mes(m)), textposition="top center",
                            textfont=dict(size=10), marker=dict(size=10, color=NARANJA, line=dict(width=1, color="white")),
                            hoverinfo="skip"))
    if len(x) >= 15:  # running median of the fire anomaly along the climate anomaly
        o = x.sort_values("ac")
        k = max(7, len(o) // 4)
        f1.add_trace(go.Scatter(x=o.ac.rolling(k, center=True).median(), y=o.af.rolling(k, center=True).median(),
                                mode="lines", line=dict(color="#F3F4F6" if oscuro() else "#111827", width=2), name=t("clima.tendencia"),
                                hoverinfo="skip"))
    f1.add_hline(y=0, line=dict(color="gray", width=1, dash="dot"))
    f1.add_vline(x=0, line=dict(color="gray", width=1, dash="dot"))
    f1.update_layout(dragmode=False, height=ALTO, margin=dict(l=0, r=0, t=5, b=0), separators=sep,
                     legend=dict(orientation="h", y=1.02, yanchor="bottom", font=dict(size=10)),
                     xaxis=dict(title=eje_x, **(dict(tickvals=[np.log(v) for v in (1 / 8, 0.25, 0.5, 1, 2, 4, 8, 16)],
                                                     ticktext=["⅛", "¼", "½", "1", "2", "4", "8", "16"])
                                                if tipo == "log" else {})),
                     yaxis=dict(title=t("clima.eje.fuego"), **ticks_y))
    st.plotly_chart(f1, width="stretch", theme="streamlit", config=CONFIG_GRAFICO)

with der.container(border=True):
    st.markdown(f"**{t('clima.titulo.box')}**", help=t("clima.ayuda.box"))
    orden = [seco, "medio", humedo]
    nombres = {seco: et_seco, "medio": t("clima.ter.medio"), humedo: et_hum}
    colores = {seco: NARANJA, "medio": GRIS_T, humedo: AZUL_T}
    f2 = go.Figure()
    for ter in orden:
        g = x[x.tercil == ter]
        f2.add_trace(go.Box(y=g.af, name=nombres[ter], marker_color=colores[ter], boxpoints=False,
                            hoverinfo="skip"))
        if len(g):
            f2.add_annotation(x=nombres[ter], y=float(g.af.quantile(0.95)), yshift=12, showarrow=False,
                              text=t("clima.sobre", p=num(100 * (g.af > 0).mean())), font=dict(size=11))
    f2.add_hline(y=0, line=dict(color="gray", width=1, dash="dot"))
    f2.update_layout(dragmode=False, height=ALTO, margin=dict(l=0, r=0, t=5, b=0), showlegend=False,
                     separators=sep, yaxis=dict(title=t("clima.eje.fuego"), **ticks_y))
    st.plotly_chart(f2, width="stretch", theme="streamlit", config=CONFIG_GRAFICO)

barra_lateral_final(d, nombre)
