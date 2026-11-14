"""Team (who we are)."""

import streamlit as st

from comun import cabecera, pie, tr

cabecera()
st.title(tr("Equipo", "Team"))
st.markdown(tr(
    "**Calendario del Fuego** · NASA Space Apps Challenge 2026 · Sede Catamarca, Argentina  \n"
    "Desafío: *Harmonization of MODIS and VIIRS Hot Spots*",
    "**Calendario del Fuego** · NASA Space Apps Challenge 2026 · Catamarca, Argentina  \n"
    "Challenge: *Harmonization of MODIS and VIIRS Hot Spots*"))
with st.container(border=True):
    st.markdown("**Jorge Luis Montivero**")
    st.write(tr("Licenciado en Estadística. Datos, modelo, validación, página y comunicación.",
                "Statistician. Data, model, validation, website and communication."))
st.header(tr("Uso de herramientas de inteligencia artificial", "Use of artificial intelligence tools"))
st.markdown(tr(
    "Usamos un asistente de IA (Claude, de Anthropic) para escribir y revisar código y textos. Las decisiones de "
    "método, la revisión de cada resultado y las conclusiones son nuestras. No usamos imágenes ni voces generadas "
    "con IA.",
    "We used an AI assistant (Claude, by Anthropic) to write and review code and text. Method decisions, the review "
    "of every result and the conclusions are ours. No AI-generated images or voices are used."))
st.header(tr("Licencia y agradecimientos", "License and acknowledgements"))
st.markdown(tr(
    "Código abierto bajo licencia MIT. Gracias a la NASA por FIRMS y a la organización local de Space Apps Catamarca.",
    "Open code under the MIT license. Thanks to NASA for FIRMS and to the Space Apps Catamarca local organizers."))
pie()
