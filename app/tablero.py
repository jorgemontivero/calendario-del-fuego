"""Pieces shared by the two dashboard views (Series and One year): the area filter in the sidebar, the compact
indicator cards, and the chart height that makes each view fit the browser window without scrolling."""

import html

import numpy as np
import pandas as pd
import streamlit as st
from streamlit_js_eval import streamlit_js_eval

from comun import clima, fecha_datos, meta, mes, num, pct, serie, t

ICONO = {"inusual": "🔴", "arriba": "🟠", "normal": "⚪", "abajo": "🔵", "en_curso": "⏳"}

CSS = """<style>
.tarjetas {display: flex; gap: 0.6rem; align-items: stretch; width: 100%;}
.tarjeta {flex: 1 1 0; min-width: 0; border: 1px solid rgba(128,128,128,0.28); border-radius: 0.5rem;
          padding: 0.35rem 0.7rem; line-height: 1.25;}
.tarjeta .et {font-size: 0.78rem; opacity: 0.75; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;}
.tarjeta .va {font-size: 1.35rem; font-weight: 600; white-space: nowrap;}
.tarjeta .de {font-size: 0.75rem; margin-left: 0.35rem; font-weight: 500;}
.tarjetas:has(> .tarjeta:nth-child(5)) {gap: 0.45rem;}
.tarjetas:has(> .tarjeta:nth-child(5)) .tarjeta {padding: 0.35rem 0.55rem;}
.tarjetas:has(> .tarjeta:nth-child(5)) .va {font-size: 1.12rem; overflow: hidden; text-overflow: ellipsis;}
.tarjeta .de.baja {color: #16a34a;} .tarjeta .de.sube {color: #dc2626;}  /* readable on light and dark */
/* phones: two cards per row instead of five squeezed into one */
@media (max-width: 640px) {
  .tarjetas {flex-wrap: wrap; gap: 0.4rem !important; margin-bottom: 0.9rem;}
  .tarjeta {flex: 1 1 calc(50% - 0.4rem);}
  .tarjeta .et {white-space: normal;}
  .tarjeta .va, .tarjetas:has(> .tarjeta:nth-child(5)) .va {font-size: 1.05rem; white-space: normal;}
}
.resumen {font-size: 0.92rem; margin: 0.1rem 0 0.15rem 0; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;}
@media (max-width: 900px) {.resumen {white-space: normal;}}
.area-titulo {font-size: 1.55rem; font-weight: 700; line-height: 1.15; margin: 0;}
.area-sub {font-size: 0.75rem; opacity: 0.7;}
/* the window-height probe is an invisible iframe: take it out of the layout (it keeps running) */
div[data-testid="stElementContainer"]:has(iframe[title*="streamlit_js_eval"]) {position: absolute; height: 0;
    width: 0; overflow: hidden; margin: 0; padding: 0;}
</style>"""


def alto_graficos(resto: int) -> int:
    """Height for every chart of the view: the browser window minus `resto` (everything that is not a chart:
    top bar, indicators, controls, panel titles; measured on screen). The window height is read once with a tiny JS
    component, which runs in an iframe (hence window.parent); the first run, before it answers, assumes 900 px."""
    # The probe is drawn only until it answers, once per session. Drawn on every page, its answer arrived after the
    # user had switched views and triggered a rerun of the previous page: the app jumped back to "Historical series".
    if "alto_px" not in st.session_state:
        with st.sidebar:
            alto_js = streamlit_js_eval(js_expressions="window.parent.innerHeight", key="alto_ventana")
        if alto_js:
            st.session_state["alto_px"] = int(alto_js)
            st.rerun()  # redraw at the right size right away
    return int(min(600, max(230, st.session_state.get("alto_px", 900) - resto)))


def filtros():
    """Province and department in the sidebar. The choice lives in session_state, so it survives switching views
    (widget values are dropped when the widget is not on the page, and the top menu drops the URL parameters)."""
    s = serie()
    st.markdown(CSS, unsafe_allow_html=True)
    if "prov_sel" not in st.session_state:
        st.session_state["prov_sel"] = st.query_params.get("prov", "00")  # all of Argentina by default (?prov=10: Catamarca)
    with st.sidebar:
        st.markdown(f"### {t('tab.filtros')}")
        provincias = s[s.nivel == "provincia"].drop_duplicates("area_cod").sort_values("area")
        opciones_p = [("00", t("area.todo_pais"))] + list(zip(provincias.area_cod, provincias.area))
        idx_p = next((i for i, (c, _) in enumerate(opciones_p) if c == st.session_state["prov_sel"]), 0)
        prov_cod, prov_nom = st.selectbox(t("area.provincia"), opciones_p, index=idx_p, format_func=lambda o: o[1])
        if prov_cod != st.session_state["prov_sel"]:
            st.session_state["prov_sel"], st.session_state["dep_sel"] = prov_cod, None
        dep_cod, dep_nom = None, None
        if prov_cod != "00":
            deps = s[(s.nivel == "departamento") & (s.prov_cod == prov_cod)].drop_duplicates("area_cod").sort_values("area")
            opciones_d = [(None, t("area.todos"))] + list(zip(deps.area_cod, deps.area))
            idx_d = next((i for i, (c, _) in enumerate(opciones_d) if c == st.session_state.get("dep_sel")), 0)
            dep_cod, dep_nom = st.selectbox(t("area.departamento"), opciones_d, index=idx_d, format_func=lambda o: o[1])
            st.session_state["dep_sel"] = dep_cod
    if dep_cod:
        d, nombre = s[(s.nivel == "departamento") & (s.area_cod == dep_cod)], f"{dep_nom} ({prov_nom})"
    elif prov_cod == "00":
        d, nombre = s[s.nivel == "pais"], t("area.todo_pais")
    else:
        d, nombre = s[(s.nivel == "provincia") & (s.area_cod == prov_cod)], prov_nom
    return d.copy(), nombre, prov_cod, prov_nom, dep_cod


def _tarjeta(etiqueta, valor, delta=None, sube=None, ayuda=None):
    tit = f' title="{html.escape(ayuda)}"' if ayuda else ""
    de = ""
    if delta:
        flecha = "▲" if sube else "▼"
        de = f'<span class="de {"sube" if sube else "baja"}">{flecha} {html.escape(delta)}</span>'
    return (f'<div class="tarjeta"{tit}><div class="et">{html.escape(etiqueta)}</div>'
            f'<div class="va">{html.escape(valor)}{de}</div></div>')


def _pct_txt(v, n):
    return (None, None) if not n else (f"{num(abs(100 * (v / n - 1)))} % {t('kpi.vs_normal')}", v > n)


def puesto_txt(k, n) -> str:
    """Rank in words: "the highest of 24", "the lowest of 24", "3rd highest of 24"."""
    k, n = int(k), int(n)
    if k == 1:
        return t("puesto.max", n=n)
    if k == n:
        return t("puesto.min", n=n)
    suf = "th" if 10 <= k % 100 <= 20 else {1: "st", 2: "nd", 3: "rd"}.get(k % 10, "th")
    return t("puesto.k", k=k, suf=suf, n=n)


def _normal_acumulado(d: pd.DataFrame, hasta_mes: int) -> float:
    """What is normal for January..hasta_mes: the median, over 2003-2022, of each year's January..hasta_mes total
    (not the sum of the monthly medians, which is lower)."""
    ref = d[d.anio.between(2003, 2022) & (d.mes <= hasta_mes)].groupby("anio").valor.sum()
    return float(ref.median())


def _tarjetas_recientes(d: pd.DataFrame):
    """Series view: the last full month and the year so far."""
    ua, um = meta()["ultimo_mes_completo"]
    u = d[(d.anio == ua) & (d.mes == um)].iloc[0]
    av = d[(d.anio == ua) & (d.mes <= um)].valor.sum()
    an = _normal_acumulado(d, um)
    ayuda1 = t("kpi.mes.ayuda") + (" " + t("ultimo.rango", li=num(u.min90), ls=num(u.max90)) if not np.isnan(u.min90) else "")
    d1, s1 = _pct_txt(u.valor, u.normal)
    d2, s2 = _pct_txt(av, an)
    ayuda4 = t("ultimo.prob", p=pct(u.prob_inusual)) if not np.isnan(u.prob_inusual) else None
    return [
        _tarjeta(t("kpi.mes", mes=mes(um, True).capitalize(), anio=ua), num(u.valor), d1, s1, ayuda1),
        _tarjeta(t("kpi.acum", anio=ua, mes=mes(um)), num(av), d2, s2, t("kpi.acum.ayuda", mes=mes(um, True))),
        _tarjeta(t("kpi.puesto", mes=mes(um)), puesto_txt(u.puesto, u.n_anios), ayuda=t("puesto.ayuda")),
        _tarjeta(t("kpi.estado"), f"{ICONO[u.estado]} {t('estado.corto.' + u.estado)}", ayuda=ayuda4),
    ]


def _lluvia(prov_cod: str, ua: int, um: int) -> dict | None:
    """Climate context: rain of the three months ending in the last full month, against the median of the same
    three months in 2003-2022 (NASA POWER, province of the area; the country for all of Argentina)."""
    c = clima()
    c = c[c.prov_cod == prov_cod].set_index(["anio", "mes"]).sort_index()
    if (ua, um) not in c.index or not c.loc[(ua, um), "completo"]:
        return None
    meses = [((ua * 12 + um - 1 - k) // 12, (ua * 12 + um - 1 - k) % 12 + 1) for k in (2, 1, 0)]
    v = float(c.lluvia_mm.reindex(meses).sum())
    # the same three months in each reference year (shifted whole years back, so Dec-Feb windows still work)
    ref = np.array([c.lluvia_mm.reindex([(y + a - ua, m) for y, m in meses]).sum(min_count=3)
                    for a in range(2003, 2023)])
    ref = ref[~np.isnan(ref)]
    if not len(ref):
        return None
    q1, q2 = np.quantile(ref, [1 / 3, 2 / 3])
    return dict(v=v, normal=float(np.median(ref)), m1=meses[0][1],
                ter="seco" if v <= q1 else ("lluvioso" if v >= q2 else "normal"),
                hum=float(c.loc[(ua, um), "humedad"]),
                hum_n=float(c.humedad.reindex([(a, um) for a in range(2003, 2023)]).median()))


def _tarjeta_lluvia(prov_cod: str, ua: int, um: int) -> str:
    ll = _lluvia(prov_cod, ua, um)
    if ll is None:
        return ""
    etiqueta = t("kpi.lluvia", m1=mes(ll["m1"]), m2=mes(um))
    ayuda = t("kpi.lluvia.ayuda", n=num(ll["normal"]), h=num(ll["hum"]), hn=num(ll["hum_n"]))
    color = {"seco": "#EA580C", "lluvioso": "#3B82F6"}.get(ll["ter"], "inherit")
    return (f'<div class="tarjeta" title="{html.escape(ayuda)}"><div class="et">{html.escape(etiqueta)}</div>'
            f'<div class="va">{num(ll["v"])} mm<span class="de" style="color:{color}">'
            f'{html.escape(t("kpi.lluvia." + ll["ter"]))}</span></div></div>')


def frase_resumen(d: pd.DataFrame) -> str:
    """One sentence saying what the cards show, for someone who looks for thirty seconds: the last full month and
    the year so far. Fire only: the rain context lives in the Climate and fire view, next to its correlation."""
    ua, um = meta()["ultimo_mes_completo"]
    u = d[(d.anio == ua) & (d.mes == um)].iloc[0]
    m_largo, n = mes(um, True), int(u.n_anios) if not np.isnan(u.n_anios) else 0
    if u.normal <= 0 and u.valor <= 0:
        p_mes = t("res.mes.sin", mes=m_largo.capitalize(), anio=ua)
    elif not np.isnan(u.puesto) and int(u.puesto) == 1 and n > 1:
        p_mes = t("res.mes.max", mes=m_largo.capitalize(), anio=ua, m=m_largo, n=n, v=num(u.valor))
    elif not np.isnan(u.puesto) and int(u.puesto) == n and n > 1:
        p_mes = t("res.mes.min", mes=m_largo.capitalize(), anio=ua, m=m_largo, n=n, v=num(u.valor))
    elif u.estado == "normal" or u.normal <= 0:
        p_mes = t("res.mes.normal", mes=m_largo.capitalize(), anio=ua, v=num(u.valor), n=num(u.normal))
    else:
        p_mes = t("res.mes.arriba" if u.valor > u.normal else "res.mes.abajo", mes=m_largo.capitalize(), anio=ua,
                  v=num(u.valor), p=num(abs(100 * (u.valor / u.normal - 1))))
    av, an = d[(d.anio == ua) & (d.mes <= um)].valor.sum(), _normal_acumulado(d, um)
    if not an:
        p_anio = ""
    elif abs(av / an - 1) < 0.1:
        p_anio = t("res.anio.cerca")
    else:
        p_anio = t("res.anio.arriba" if av > an else "res.anio.abajo", p=num(abs(100 * (av / an - 1))))
    return " ".join(x for x in (p_mes, p_anio) if x)


def _tarjetas_anio(d: pd.DataFrame, anio: int):
    """One-year view: the chosen year. The current year is incomplete, so it is compared January..last full month
    against the same months of every other year."""
    ua, um = meta()["ultimo_mes_completo"]
    hasta = um if anio == ua else 12
    tot = d[(d.mes <= hasta) & (d.anio <= ua) & ~((d.anio == ua) & (d.mes > um))].groupby("anio").valor.sum()
    tot = tot[tot.index >= 2003]
    if anio != ua:
        tot = tot[tot.index < ua]  # complete years only
    v = float(tot.loc[anio])
    normal = _normal_acumulado(d, hasta)
    puesto = int(tot.rank(ascending=False, method="min").loc[anio])
    da, sa = _pct_txt(v, normal)
    etiqueta = t("kpi.anio.parcial", anio=anio, mes=mes(um)) if anio == ua else t("kpi.anio", anio=anio)
    meses = d[(d.anio == anio) & d.mes_completo]
    pico = meses.loc[meses.valor.idxmax()] if len(meses) else None
    # months outside the usual range = the grey band of the season chart (10th-90th percentile of 2003-2022 for
    # that month), on both sides, so the card and the chart say the same thing
    banda = d[d.anio.between(2003, 2022)].groupby("mes").valor.quantile([0.1, 0.9]).unstack()
    m_b = meses.join(banda, on="mes")
    bajos = int((m_b.valor < m_b[0.1]).sum())
    altos = int((m_b.valor > m_b[0.9]).sum())
    return [
        _tarjeta(etiqueta, num(v), da, sa, t("kpi.anio.ayuda")),
        _tarjeta(t("kpi.puesto.anios"), puesto_txt(puesto, len(tot)), ayuda=t("kpi.puesto.anios.ayuda")),
        _tarjeta(t("kpi.pico", anio=anio), f"{mes(int(pico.mes), True).capitalize()} · {num(pico.valor)}" if pico is not None else "—",
                 ayuda=t("kpi.pico.ayuda")),
        _tarjeta(t("kpi.inusuales"), t("kpi.inusuales.valor", bajos=bajos, altos=altos),
                 ayuda=t("kpi.inusuales.ayuda", n=len(meses))),
    ]


def encabezado(d: pd.DataFrame, nombre: str, anio: int | None = None):
    """Area name and four compact cards of the same size, in one row: about the latest months (Series view) or
    about the chosen year (One-year view)."""
    tarjetas = "".join(_tarjetas_recientes(d) if anio is None else _tarjetas_anio(d, anio))
    c0, c1 = st.columns([1, 4.2] if anio is None else [1, 3.2], vertical_alignment="center")
    with c0:
        aviso = f'<div class="area-sub">⚠️ {html.escape(t("area.aviso.corto"))}</div>' if d.mediana_anual.iloc[0] < 50 else ""
        st.markdown(f'<div class="area-titulo">{html.escape(nombre)}</div>{aviso}', unsafe_allow_html=True,
                    help=t("area.aviso.chica") if aviso else None)
    with c1:
        st.markdown(f'<div class="tarjetas">{tarjetas}</div>', unsafe_allow_html=True)


def barra_lateral_final(d: pd.DataFrame, nombre: str):
    """The download of the chosen area and the data date, at the bottom of the sidebar. Explanations (how to read,
    what a hot spot is, how to cite, sources) live in the Help page."""
    csv = pd.DataFrame({
        "area": nombre, "year": d.anio, "month": d.mes, "hotspots": d.valor, "lo90": d.min90, "hi90": d.max90,
        "median_month": d.normal, "p90_month": d.p90, "rank": d.puesto, "n_years": d.n_anios,
        "unusual": (d.estado == "inusual").astype(int), "status": d.estado, "complete_month": d.mes_completo.astype(int),
        "source": d.origen})
    with st.sidebar:
        st.divider()
        st.download_button("⬇️ " + t("desc.boton", area=t("area.pais_frase") if nombre == t("area.todo_pais") else nombre), csv.to_csv(index=False).encode("utf-8"),
                           file_name=f"calendario_del_fuego_{nombre.replace(' ', '_')}.csv", mime="text/csv",
                           width="stretch", help=t("desc.texto"))
        st.caption(t("datos.actualizado", fecha=fecha_datos()))
