"""Contact."""

import streamlit as st

from comun import cabecera, pie, t, tr

cabecera()
st.title(tr("Contacto", "Contact"))
st.error(tr("**Esto no es para emergencias.** Si hay fuego, llamá al **100** (bomberos).",
            "**This is not for emergencies.** If there is a fire, call **100** (fire department, Argentina)."))
st.markdown(tr(
    "- **Errores o mejoras:** abrí un *issue* en el repositorio: "
    "https://github.com/jorgemontivero/calendario-del-fuego/issues\n"
    "- **Correo del proyecto:** [pendiente]",
    "- **Bugs or ideas:** open an issue in the repository: "
    "https://github.com/jorgemontivero/calendario-del-fuego/issues\n"
    "- **Project e-mail:** [pending]"))
st.caption(tr("No usamos formularios ni guardamos datos de quien visita la página.",
              "We use no forms and store no data about visitors."))
pie()
