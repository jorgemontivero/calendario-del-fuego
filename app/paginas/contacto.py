"""Contact."""

import streamlit as st

from comun import cabecera, pie, t, tr

cabecera()
st.title(tr("Contacto", "Contact"))
st.error(tr("**Esto no es para emergencias.** Si hay fuego, llamá al **100** (bomberos).",
            "**This is not for emergencies.** If there is a fire, call **100** (fire department, Argentina)."))
# The address is assembled here instead of written whole in the code and the page source, which makes it a little
# harder for spam crawlers to harvest; people see and click a normal mailto link.
CORREO = "calendariodelfuego" + "@" + "gmail.com"
st.markdown(tr(
    f"- **Correo del proyecto:** [{CORREO}](mailto:{CORREO})\n"
    "- **Errores o mejoras:** abrí un *issue* en el repositorio: "
    "https://github.com/jorgemontivero/calendario-del-fuego/issues",
    f"- **Project e-mail:** [{CORREO}](mailto:{CORREO})\n"
    "- **Bugs or ideas:** open an issue in the repository: "
    "https://github.com/jorgemontivero/calendario-del-fuego/issues"))
st.caption(tr("No usamos formularios ni guardamos datos de quien visita la página.",
              "We use no forms and store no data about visitors."))
pie()
