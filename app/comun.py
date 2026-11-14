"""Shared pieces: language, texts, number format, data loading, header and footer."""

import json
from pathlib import Path

import pandas as pd
import streamlit as st

from textos import MESES, MESES_LARGOS, T

DATOS = Path(__file__).resolve().parent / "datos"
NARANJA, AZUL = "#C2410C", "#1D4ED8"


# Plotly's toolbar: only "download as image" (the charts are meant to end up in reports). Zoom, pan, select and
# reset only got in the way on a dashboard. Maps have no toolbar and zoom with the mouse wheel (mapas.CONFIG).
CONFIG_GRAFICO = {"displaylogo": False, "modeBarButtons": [["toImage"]],
                  "toImageButtonOptions": {"format": "png", "scale": 2, "filename": "calendario_del_fuego"}}


def idioma() -> str:
    """The URL (?lang=en) wins; the session remembers it, because the top menu drops query parameters."""
    if "lang" in st.query_params:
        st.session_state["lang"] = "en" if st.query_params["lang"] == "en" else "es"
    lang = st.session_state.get("lang", "es")
    if st.query_params.get("lang") != lang:
        st.query_params["lang"] = lang
    return lang


def t(clave: str, **kw) -> str:
    texto = T[clave][1 if idioma() == "en" else 0]
    return texto.format(**kw) if kw else texto


def tr(es: str, en: str) -> str:
    """Long texts that live in their own page (Methods, Team, Contact): both languages side by side."""
    return en if idioma() == "en" else es


def num(x, dec=0) -> str:
    """Number in the language's format: 2,6 / 1.234 in Spanish; 2.6 / 1,234 in English."""
    if x is None or pd.isna(x):
        return "—"
    s = f"{x:,.{dec}f}"
    return s.replace(",", "§").replace(".", ",").replace("§", ".") if idioma() == "es" else s


def pct(x) -> str:
    return "—" if x is None or pd.isna(x) else f"{num(100 * x)} %"


def mes(m: int, largo=False) -> str:
    return (MESES_LARGOS if largo else MESES)[idioma()][m - 1]


@st.cache_data
def serie() -> pd.DataFrame:
    return pd.read_parquet(DATOS / "serie.parquet")


@st.cache_data
def clima() -> pd.DataFrame:
    """NASA POWER by province (and "00" for the country): rain, humidity, max temperature per month."""
    return pd.read_parquet(DATOS / "clima.parquet")


@st.cache_data
def anual_pais() -> pd.DataFrame:
    return pd.read_parquet(DATOS / "anual_pais.parquet")


@st.cache_data
def meta() -> dict:
    return json.loads((DATOS / "meta.json").read_text(encoding="utf-8"))


def fecha_datos() -> str:
    a, m, d = meta()["fecha_datos"].split("-")
    return f"{d}/{m}/{a}" if idioma() == "es" else f"{a}-{m}-{d}"


def cabecera():
    """Language switch and the emergency button, on every page. Streamlit has no slot for custom widgets in its top
    navigation bar, so this container is pinned there with CSS (class st-key-barra_sup), to the left of the
    toolbar; the page content then starts right under the bar."""
    st.markdown("""<style>
    .st-key-barra_sup {position: fixed; top: 0.55rem; right: 8.5rem; z-index: 999991; width: auto !important;}
    .st-key-barra_sup button {min-height: 2rem; padding-top: 0.15rem; padding-bottom: 0.15rem;}
    .block-container {padding-top: 2.4rem !important; padding-bottom: 0.5rem !important;}
    /* the menu must stop before the pinned language/emergency buttons (on narrow screens the rest folds away) */
    [data-testid="stTopNav"] {max-width: calc(100% - 430px) !important;}
    [data-testid="stTopNavLink"] {padding-left: 0.45rem !important; padding-right: 0.45rem !important;}
    .block-container h2:first-of-type {padding-top: 0.2rem;}
    @media (max-width: 640px) {.st-key-barra_sup {right: 3.2rem;} .st-key-barra_sup p {font-size: 0.8rem;}}
    /* "About the project" links: drawn first, shown last, at the foot of the sidebar */
    [data-testid="stSidebarUserContent"] > div > [data-testid="stVerticalBlock"] {min-height: calc(100vh - 7rem);}
    [data-testid="stLayoutWrapper"]:has(> .st-key-acerca) {order: 99; margin-top: auto;}
    .st-key-acerca {padding-top: 0.6rem; border-top: 1px solid rgba(128,128,128,0.25);}
    .st-key-acerca a {padding: 0.05rem 0.25rem !important; min-height: 0 !important;}
    .st-key-acerca a p {font-size: 0.9rem;}
    </style>""", unsafe_allow_html=True)
    with st.sidebar.container(key="acerca", gap="small"):
        st.caption(t("nav.acerca"))
        for archivo, clave, icono in [("metodologia", "nav.metodologia", ":material/science:"),
                                      ("ayuda", "nav.ayuda", ":material/help:"),
                                      ("equipo", "nav.equipo", ":material/group:"),
                                      ("contacto", "nav.contacto", ":material/mail:")]:
            st.page_link(f"paginas/{archivo}.py", label=t(clave), icon=icono)
    with st.container(key="barra_sup", horizontal=True, gap="small"):
        elegido = st.segmented_control(t("idioma"), ["ES", "EN"], default=idioma().upper(), label_visibility="collapsed",
                                       key="selector_idioma")
        if elegido and elegido.lower() != idioma():
            st.session_state["lang"] = elegido.lower()
            st.query_params["lang"] = elegido.lower()
            st.rerun()
        with st.popover("🔥 " + t("emerg.boton")):
            st.markdown(f"**{t('emerg.titulo')}**")
            st.write(t("emerg.texto"))
            st.markdown(t("emerg.lista"))
            st.caption(t("emerg.datos"))


def pie():
    st.divider()
    st.caption(t("datos.actualizado", fecha=fecha_datos()) + " " + t("pie"))
