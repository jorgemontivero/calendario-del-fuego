"""App: choose an area and years; calendar, last full month, season, downloads."""

import math

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from comun import AZUL, NARANJA, cabecera, fecha_datos, meta, mes, num, pct, pie, serie, t

cabecera()
s = serie()

# ------------------------------------------------------------------------------------------------ area
st.subheader(t("area.titulo"))
c1, c2, c3 = st.columns([3, 3, 4])
provincias = s[s.nivel == "provincia"].drop_duplicates("area_cod").sort_values("area")
opciones_p = [("00", t("area.todo_pais"))] + list(zip(provincias.area_cod, provincias.area))
qp_prov = st.query_params.get("prov", "10")  # Catamarca by default: the local case
idx_p = next((i for i, (c, _) in enumerate(opciones_p) if c == qp_prov), 0)
with c1:
    prov_cod, prov_nom = st.selectbox(t("area.provincia"), opciones_p, index=idx_p, format_func=lambda o: o[1])
dep_cod, dep_nom = None, None
with c2:
    if prov_cod != "00":
        deps = s[(s.nivel == "departamento") & (s.prov_cod == prov_cod)].drop_duplicates("area_cod").sort_values("area")
        opciones_d = [(None, t("area.todos"))] + list(zip(deps.area_cod, deps.area))
        dep_cod, dep_nom = st.selectbox(t("area.departamento"), opciones_d, format_func=lambda o: o[1])
with c3:
    anio_max = int(s.anio.max())
    desde, hasta = st.slider(t("area.anios"), 2003, anio_max, (2003, anio_max))
st.query_params["prov"] = prov_cod

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
chica = d.mediana_anual.iloc[0] < 50
if chica:
    st.warning(t("area.aviso.chica"))

# ------------------------------------------------------------------------------------------------ last full month
ua, um = meta()["ultimo_mes_completo"]
u = d[(d.anio == ua) & (d.mes == um)].iloc[0]
COLOR_ESTADO = {"inusual": "red", "arriba": "orange", "normal": "gray", "abajo": "blue", "en_curso": "gray"}
with st.container(border=True):
    st.markdown(f"#### {t('ultimo.titulo', mes=mes(um, True).capitalize(), anio=ua)}")
    k1, k2, k3, k4 = st.columns(4)
    k1.metric(t("ultimo.focos"), num(u.valor))
    k2.metric(t("ultimo.normal", mes=mes(um, True)), num(u.normal))
    k3.metric(t("ultimo.puesto", mes=mes(um, True)), t("ultimo.puesto.valor", k=num(u.puesto), n=num(u.n_anios)))
    with k4:
        st.markdown(f"<br>:{COLOR_ESTADO[u.estado]}-badge[{t('estado.' + u.estado)}]", unsafe_allow_html=True)
    notas = []
    if not np.isnan(u.min90):
        notas.append(t("ultimo.rango", li=num(u.min90), ls=num(u.max90)))
    if not np.isnan(u.prob_inusual):
        notas.append(t("ultimo.prob", p=pct(u.prob_inusual)))
    if notas:
        st.caption(" ".join(notas))

# ------------------------------------------------------------------------------------------------ calendar
st.subheader(t("cal.titulo", area=nombre, desde=desde, hasta=hasta))
modo = st.segmented_control(t("cal.modo"), ["conteo", "anomalia"], default="conteo",
                            format_func=lambda m: t(f"cal.modo.{m}"), key="modo_cal")
dd = d[d.anio.between(desde, hasta)]
anios = list(range(hasta, desde - 1, -1))  # most recent on top
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
                                ticktext=[num(v) for v in ticks]))
else:
    tv = [-3, -2, -1, 0, 1, 2, 3]
    escala = dict(colorscale="RdBu_r", zmid=0, zmin=-3, zmax=3,
                  colorbar=dict(title=t("cal.leyenda.veces"), tickvals=tv,
                                ticktext=["≤⅛", "¼", "½", "1", "2", "4", "≥8"]))
fig = go.Figure(go.Heatmap(z=Z, x=[mes(m).capitalize() for m in range(1, 13)], y=[str(a) for a in anios],
                           text=H, hoverinfo="text", xgap=2, ygap=2, **escala))
fig.update_layout(height=max(320, 22 * len(anios) + 80), margin=dict(l=10, r=10, t=10, b=10),
                  yaxis=dict(type="category", autorange="reversed"), xaxis=dict(side="top"))
st.plotly_chart(fig, use_container_width=True, theme="streamlit")
st.caption(t("cal.unidad") + " " + t("armon.corta"))
c1, c2 = st.columns(2)
with c1.expander(t("como_leer")):
    st.markdown(t("como_leer.texto"))
with c2.expander(t("foco.titulo")):
    st.markdown(t("foco.texto"))
en_curso = d[~d.mes_completo]
if len(en_curso):
    st.caption(t("en_curso", fecha=fecha_datos()))

# ------------------------------------------------------------------------------------------------ season
st.subheader(t("temp.titulo", area=nombre))
ref = d[d.anio.between(2003, 2022)]
q = ref.groupby("mes").valor.quantile([0.1, 0.5, 0.9]).unstack()
anio_c = st.selectbox(t("temp.anio"), list(range(anio_max, 2002, -1)), key="anio_temp")
ac = d[d.anio == anio_c].sort_values("mes")
x = [mes(m).capitalize() for m in range(1, 13)]
f2 = go.Figure()
f2.add_trace(go.Scatter(x=x, y=q[0.9], mode="lines", line=dict(width=0), showlegend=False, hoverinfo="skip"))
f2.add_trace(go.Scatter(x=x, y=q[0.1], fill="tonexty", mode="lines", line=dict(width=0), fillcolor="rgba(128,128,128,0.25)",
                        name=t("temp.banda"), hoverinfo="skip"))
f2.add_trace(go.Scatter(x=x, y=q[0.5], mode="lines", line=dict(color="gray", dash="dash"), name=t("temp.mediana")))
xa = [mes(m).capitalize() for m in ac.mes]
if ac.min90.notna().any():
    f2.add_trace(go.Scatter(x=xa, y=ac.max90, mode="lines", line=dict(width=0), showlegend=False, hoverinfo="skip"))
    f2.add_trace(go.Scatter(x=xa, y=ac.min90, fill="tonexty", mode="lines", line=dict(width=0), fillcolor="rgba(194,65,12,0.2)",
                            showlegend=False, hoverinfo="skip"))
f2.add_trace(go.Scatter(x=xa, y=ac.valor, line=dict(color=NARANJA, width=3), mode="lines+markers", name=str(anio_c)))
f2.update_layout(height=340, margin=dict(l=10, r=10, t=10, b=10), legend=dict(orientation="h", y=-0.15),
                 yaxis_title=t("cal.leyenda.focos"))
st.plotly_chart(f2, use_container_width=True, theme="streamlit")

med = q[0.5]
orden = med.sort_values(ascending=False)
acum = orden.cumsum() / max(orden.sum(), 1e-9)
temporada = sorted(orden.index[: int((acum < 0.8).sum()) + 1])
anual = d[d.anio.between(2003, 2025)].groupby("anio").valor.sum()


def mann_kendall_z(x):
    x = np.asarray(x, float)
    n = len(x)
    S = sum(np.sign(x[j] - x[i]) for i in range(n - 1) for j in range(i + 1, n))
    return (S - np.sign(S)) / math.sqrt(n * (n - 1) * (2 * n + 5) / 18) if S else 0.0


z = mann_kendall_z(anual.to_numpy())
tend = "temp.tendencia.sube" if z > 1.96 else "temp.tendencia.baja" if z < -1.96 else "temp.tendencia.nada"
m1, m2, m3 = st.columns(3)
m1.metric(t("temp.pico"), mes(int(med.idxmax()), True).capitalize())
m2.metric(t("temp.temporada"), ", ".join(mes(m) for m in temporada), help=t("temp.temporada.ayuda"))
m3.metric(t("temp.tendencia"), t(tend).split(":")[0])
st.caption(t(tend))

# ------------------------------------------------------------------------------------------------ downloads
st.subheader(t("desc.titulo", area=nombre))
csv = pd.DataFrame({
    "area": nombre, "year": d.anio, "month": d.mes, "hotspots": d.valor, "lo90": d.min90, "hi90": d.max90,
    "median_month": d.normal, "p90_month": d.p90, "rank": d.puesto, "n_years": d.n_anios,
    "unusual": (d.estado == "inusual").astype(int), "status": d.estado, "complete_month": d.mes_completo.astype(int),
    "source": d.origen})
st.download_button(t("desc.serie"), csv.to_csv(index=False).encode("utf-8"),
                   file_name=f"calendario_del_fuego_{nombre.replace(' ', '_')}.csv", mime="text/csv")
st.caption(t("desc.texto"))
with st.expander(t("desc.citar")):
    st.code(t("cita"), language=None)
pie()
