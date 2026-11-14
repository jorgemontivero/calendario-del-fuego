"""Calendario del Fuego - entry point.  Run: streamlit run app/app.py   (English: add ?lang=en to the URL)"""

import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parent))
from comun import meta, t  # noqa: E402

st.set_page_config(page_title="Calendario del Fuego", page_icon="🔥", layout="wide")
AQUI = Path(__file__).resolve().parent / "paginas"
paginas = [
    st.Page(AQUI / "serie.py", title=t("tab.serie", desde=2003, hasta=meta()["ultimo_mes_completo"][0]), default=True,
            url_path="serie"),
    st.Page(AQUI / "anio.py", title=t("tab.un_anio"), url_path="anio"),
    st.Page(AQUI / "metodologia.py", title=t("nav.metodologia"), url_path="metodologia"),
    st.Page(AQUI / "equipo.py", title=t("nav.equipo"), url_path="equipo"),
    st.Page(AQUI / "contacto.py", title=t("nav.contacto"), url_path="contacto"),
]
st.logo(str(Path(__file__).resolve().parent / "logo.svg"), size="large")
st.navigation(paginas, position="top").run()
