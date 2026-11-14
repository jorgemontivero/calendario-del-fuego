"""Calendario del Fuego - entry point.  Run: streamlit run app/app.py   (English: add ?lang=en to the URL)"""

import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parent))
from comun import t  # noqa: E402

st.set_page_config(page_title="Calendario del Fuego", page_icon="🔥", layout="wide")
AQUI = Path(__file__).resolve().parent / "paginas"
# The analysis views go in the top bar. The reading pages (methodology, help, team, contact) are hidden from it and
# linked from the bottom of the sidebar (comun.cabecera): with them in the bar it overflowed into a "N more" item that
# Streamlit labels in English only.
paginas = [
    st.Page(AQUI / "serie.py", title=t("tab.serie"), default=True, url_path="serie"),
    st.Page(AQUI / "anio.py", title=t("tab.un_anio"), url_path="anio"),
    st.Page(AQUI / "ahora.py", title=t("nav.ahora"), url_path="ahora"),
    st.Page(AQUI / "geografico.py", title=t("nav.geo"), url_path="geografico"),
    st.Page(AQUI / "reportados.py", title=t("nav.rep"), url_path="reportados"),
    st.Page(AQUI / "clima.py", title=t("nav.clima"), url_path="clima"),
    st.Page(AQUI / "metodologia.py", title=t("nav.metodologia"), url_path="metodologia", visibility="hidden"),
    st.Page(AQUI / "ayuda.py", title=t("nav.ayuda"), url_path="ayuda", visibility="hidden"),
    st.Page(AQUI / "equipo.py", title=t("nav.equipo"), url_path="equipo", visibility="hidden"),
    st.Page(AQUI / "contacto.py", title=t("nav.contacto"), url_path="contacto", visibility="hidden"),
]
st.logo(str(Path(__file__).resolve().parent / "logo.svg"), size="large")
st.navigation(paginas, position="top").run()
