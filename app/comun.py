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
    """Language switch and the emergency button, on every page."""
    c1, c2, c3 = st.columns([6, 2, 2])
    with c1:
        st.caption(t("app.lema"))
    with c2:
        elegido = st.segmented_control(t("idioma"), ["ES", "EN"], default=idioma().upper(), label_visibility="collapsed",
                                       key="selector_idioma")
        if elegido and elegido.lower() != idioma():
            st.session_state["lang"] = elegido.lower()
            st.query_params["lang"] = elegido.lower()
            st.rerun()
    with c3:
        with st.popover("🔥 " + t("emerg.boton"), width="stretch"):
            st.markdown(f"**{t('emerg.titulo')}**")
            st.write(t("emerg.texto"))
            st.markdown(t("emerg.lista"))
            st.caption(t("emerg.datos"))


def pie():
    st.divider()
    st.caption(t("datos.actualizado", fecha=fecha_datos()) + " " + t("pie"))
