"""Now vs before ("how a current fire compares with previous ones", challenge objectives): the hot spots of a date
window - the last 7 or 30 days, the year so far, or chosen dates - against the same window in every year since 2003,
from the daily harmonized series. Fits one screen."""

from datetime import date, timedelta

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from comun import CONFIG_GRAFICO, DATOS, NARANJA, cabecera, idioma, meta, num, t
from tablero import _pct_txt, _tarjeta, alto_graficos, barra_lateral_final, filtros, puesto_txt

RESTO = 300  # everything on this view that is not a chart (measured on screen)


@st.cache_data
def diaria():
    return pd.read_parquet(DATOS / "diaria.parquet")


cabecera()
d, nombre, prov_cod, prov_nom, dep_cod = filtros()
ALTO = alto_graficos(RESTO)

nivel, area_cod = ("departamento", dep_cod) if dep_cod else (("pais", "00") if prov_cod == "00" else ("provincia", prov_cod))
dd = diaria()
serie_dia = dd[(dd.nivel == nivel) & (dd.area_cod == area_cod)].set_index("fecha").valor
# the last day is still being loaded (near real time): windows end on the day before
ultimo = date.fromisoformat(meta()["fecha_datos"]) - timedelta(days=1)

# ---------------------------------------------------------------------------------------------- window
c_t, c_m, c_f = st.columns([1.1, 2.9, 1.4], vertical_alignment="center")
with c_t:
    st.markdown(f'<div class="area-titulo">{nombre}</div>', unsafe_allow_html=True)
with c_m:
    modo = st.segmented_control(t("ahora.periodo"), ["7", "30", "anio", "fechas"], default="30", key="ahora_modo",
                                label_visibility="collapsed", format_func=lambda m: t(f"ahora.modo.{m}")) or "30"
if modo == "fechas":
    with c_f:
        rango = st.date_input(t("ahora.fechas"), value=(ultimo - timedelta(days=13), ultimo), min_value=date(2003, 1, 1),
                              max_value=ultimo, format="DD/MM/YYYY", label_visibility="collapsed", key="ahora_rango")
    ini, fin = (rango if isinstance(rango, tuple) and len(rango) == 2 else (ultimo - timedelta(days=13), ultimo))
    if (fin - ini).days > 365:
        ini = fin - timedelta(days=365)
        st.toast(t("ahora.max_anio"))
elif modo == "anio":
    ini, fin = date(ultimo.year, 1, 1), ultimo
else:
    fin = ultimo
    ini = fin - timedelta(days=int(modo) - 1)
anio_ref = fin.year


def ventana(desplazamiento: int) -> pd.Series:
    """Daily values of the window moved `desplazamiento` years back (29 February falls on the 28th)."""
    a = pd.Timestamp(ini) - pd.DateOffset(years=desplazamiento)
    b = pd.Timestamp(fin) - pd.DateOffset(years=desplazamiento)
    return serie_dia.reindex(pd.date_range(a, b, freq="D"), fill_value=0.0)


anios = [a for a in range(2003, anio_ref + 1) if pd.Timestamp(ini) - pd.DateOffset(years=anio_ref - a) >= pd.Timestamp(2003, 1, 1)]
ven = {a: ventana(anio_ref - a) for a in anios}
tot = pd.Series({a: v.sum() for a, v in ven.items()})
ref = tot[[a for a in tot.index if a <= 2022 and a != anio_ref]]
normal = float(ref.median()) if len(ref) else np.nan
actual = float(tot.loc[anio_ref])
puesto = int(tot.rank(ascending=False, method="min").loc[anio_ref])

# "the highest since ...": the last earlier year that reached the current value
previos = tot[tot.index < anio_ref]
alto = actual >= normal
iguales = previos[previos >= actual] if alto else previos[previos <= actual]
desde_et = t("ahora.desde.alto") if alto else t("ahora.desde.bajo")
desde = str(int(iguales.index.max())) if len(iguales) else (t("ahora.record") if alto else t("ahora.minimo"))
dias_fuego = int((ven[anio_ref] >= 0.5).sum())
dias_normal = float(np.median([(ven[a] >= 0.5).sum() for a in ref.index])) if len(ref) else np.nan

etiqueta = (f"{ini:%d/%m}–{fin:%d/%m/%Y}" if idioma() == "es" else f"{ini:%b %d}–{fin:%b %d, %Y}")
da, sa = _pct_txt(actual, normal)
tarjetas = "".join([
    _tarjeta(etiqueta, num(actual), da, sa, t("ahora.focos.ayuda")),
    _tarjeta(t("ahora.puesto"), puesto_txt(puesto, len(tot)), ayuda=t("ahora.puesto.ayuda", n=len(tot))),
    _tarjeta(desde_et, desde, ayuda=t("ahora.desde.ayuda")),
    _tarjeta(t("ahora.dias"), t("ahora.dias.valor", k=dias_fuego, n=num(dias_normal)), ayuda=t("ahora.dias.ayuda")),
])
st.markdown(f'<div class="tarjetas" style="margin-top:0.3rem">{tarjetas}</div>', unsafe_allow_html=True)

# ---------------------------------------------------------------------------------------------- charts
sep = ",." if st.query_params.get("lang") != "en" else ".,"
izq, der = st.columns([3, 2])
with izq.container(border=True):
    st.markdown(f"**{t('ahora.titulo.barras', p=etiqueta)}**", help=t("ahora.ayuda.barras"))
    colores = [NARANJA if a == anio_ref else ("#FDBA74" if a <= 2022 else "#FB923C") for a in tot.index]
    f1 = go.Figure(go.Bar(x=tot.index, y=tot.values, marker_color=colores,
                          hovertemplate="%{x}: %{y:,.0f}<extra></extra>"))
    if not np.isnan(normal):
        f1.add_hline(y=normal, line=dict(color="gray", dash="dash", width=1.5),
                     annotation_text=t("ahora.normal", v=num(normal)), annotation_position="top left",
                     annotation_font_size=11)
    f1.update_layout(dragmode=False, height=ALTO, margin=dict(l=0, r=0, t=5, b=0), separators=sep,
                     yaxis_title=t("cal.leyenda.focos"), bargap=0.15)
    st.plotly_chart(f1, width="stretch", theme="streamlit", config=CONFIG_GRAFICO)

with der.container(border=True):
    st.markdown(f"**{t('ahora.titulo.acum')}**", help=t("ahora.ayuda.acum"))
    n = len(ven[anio_ref])
    acum = np.array([ven[a].cumsum().to_numpy()[:n] for a in ref.index]) if len(ref) else np.empty((0, n))
    x = list(range(1, n + 1))
    f2 = go.Figure()
    if len(acum):
        q10, q50, q90 = np.percentile(acum, [10, 50, 90], axis=0)
        f2.add_trace(go.Scatter(x=x, y=q90, mode="lines", line=dict(width=0), showlegend=False, hoverinfo="skip"))
        f2.add_trace(go.Scatter(x=x, y=q10, mode="lines", fill="tonexty", line=dict(width=0),
                                fillcolor="rgba(128,128,128,0.25)", name=t("temp.banda"), hoverinfo="skip"))
        f2.add_trace(go.Scatter(x=x, y=q50, mode="lines", line=dict(color="gray", dash="dash"), name=t("temp.mediana")))
    fechas = pd.date_range(ini, fin, freq="D")
    f2.add_trace(go.Scatter(x=x, y=ven[anio_ref].cumsum().to_numpy(), mode="lines", line=dict(color=NARANJA, width=3),
                            name=str(anio_ref), customdata=[f"{f:%d/%m}" for f in fechas],
                            hovertemplate="%{customdata}: %{y:,.0f}<extra></extra>"))
    f2.update_layout(dragmode=False, height=ALTO, margin=dict(l=0, r=0, t=5, b=0), separators=sep,
                     legend=dict(orientation="h", y=1.02, yanchor="bottom", font=dict(size=10)),
                     xaxis_title=t("ahora.eje.dia"), yaxis_title=t("ahora.eje.acum"))
    st.plotly_chart(f2, width="stretch", theme="streamlit", config=CONFIG_GRAFICO)

barra_lateral_final(d, nombre)
