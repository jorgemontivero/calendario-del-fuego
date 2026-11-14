"""Open data: every table behind the app as a download, with its dictionary. The files live in datos_abiertos/
(written by pipeline/paso7_datos_abiertos.py), so they can also be read straight from the repository."""

import json
from pathlib import Path

import streamlit as st

from comun import cabecera, fecha_datos, idioma, num, pie, t, tr

CARPETA = Path(__file__).resolve().parents[2] / "datos_abiertos"
REPO = "https://github.com/jorgemontivero/calendario-del-fuego/tree/main/datos_abiertos"

cabecera()
st.title(tr("Datos abiertos", "Open data"))
st.markdown(tr(
    "Todas las tablas que usa esta página, para abrir en una planilla o usar en otra aplicación. Son CSV con nombres "
    "de columna en inglés; los dos archivos grandes vienen dentro de un .zip. La unidad son **focos equivalentes "
    f"MODIS** (qué es: sección Ayuda). Datos al {fecha_datos()}.",
    "Every table behind this site, to open in a spreadsheet or use in another application. They are CSV files with "
    "English column names; the two large ones come inside a .zip. The unit is **MODIS-equivalent hot spots** (what "
    f"that is: Help section). Data as of {fecha_datos()}."))

indice = json.loads((CARPETA / "indice.json").read_text(encoding="utf-8"))["archivos"] if (CARPETA / "indice.json").exists() else []
if not indice:
    st.info(tr("Los archivos todavía no están generados.", "The files have not been generated yet."))
for a in indice:
    ruta = CARPETA / a["archivo"]
    with st.container(border=True):
        c1, c2 = st.columns([4, 1.2], vertical_alignment="center")
        with c1:
            st.markdown(f"**`{a['archivo']}`** · {num(a['filas'])} {tr('filas', 'rows')} · "
                        f"{num(a['kb'] / 1024, 1) + ' MB' if a['kb'] >= 1024 else num(a['kb']) + ' KB'}")
            st.write(a[idioma()])
            st.caption(tr("Columnas: ", "Columns: ") + ", ".join(a["columnas"]))
        with c2:
            if ruta.exists():
                st.download_button("⬇️ " + tr("Descargar", "Download"), ruta.read_bytes(), file_name=a["archivo"],
                                   mime="application/zip" if ruta.suffix == ".zip" else "text/csv",
                                   width="stretch", key="desc_" + a["archivo"])

st.markdown(tr(f"Los mismos archivos están en el repositorio: {REPO}",
               f"The same files are in the repository: {REPO}"))
diccionario = CARPETA / ("README.md" if idioma() == "es" else "README.en.md")
if diccionario.exists():
    with st.expander(tr("Diccionario de columnas, uso y cita", "Column dictionary, use and citation")):
        texto = diccionario.read_text(encoding="utf-8")
        st.markdown(texto.split("\n", 1)[1] if texto.startswith("# ") else texto)  # the page already has a title
st.subheader(tr("Cómo citar", "How to cite"))
st.code(t("cita"), language=None)
pie()
