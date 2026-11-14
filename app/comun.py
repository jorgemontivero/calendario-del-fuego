"""Shared pieces: language, texts, number format, data loading, header and footer."""

import json
from pathlib import Path

import pandas as pd
import streamlit as st

from textos import MESES, MESES_LARGOS, T

DATOS = Path(__file__).resolve().parent / "datos"
NARANJA, AZUL = "#C2410C", "#1D4ED8"


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
    .block-container h2:first-of-type {padding-top: 0.2rem;}
    @media (max-width: 640px) {.st-key-barra_sup {right: 3.2rem;} .st-key-barra_sup p {font-size: 0.8rem;}}
    </style>""", unsafe_allow_html=True)
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
