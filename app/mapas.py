"""Choropleth of fire per 1,000 km2 (harmonized series), shared by the One-year view and the Geographic analysis.

All of Argentina is drawn by province; a province, by department. The density uses the area in an equal-area
projection (km2, computed in step 6), so large departments don't look like the most burned just because of their
size. For a comparison, both maps get the same color range (`zrango`)."""

import json
import math

import geopandas as gpd
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from comun import DATOS, meta, num, serie, t


@st.cache_data
def limites():
    return gpd.read_parquet(DATOS / "limites.parquet")


def datos_mapa(prov_cod: str, anio: int) -> gpd.GeoDataFrame:
    """Areas to draw (provinces for "00", else the departments of the province) with the year's harmonized total
    and its density. The current, incomplete year counts up to the last full month."""
    s, lim = serie(), limites()
    ua, um = meta()["ultimo_mes_completo"]
    hasta = um if anio == ua else 12
    if prov_cod == "00":
        geo = lim[lim.nivel == "provincia"]
        sel = s[(s.nivel == "provincia") & (s.anio == anio) & (s.mes <= hasta)]
    else:
        geo = lim[(lim.nivel == "departamento") & (lim.prov_cod == prov_cod)]
        sel = s[(s.nivel == "departamento") & (s.prov_cod == prov_cod) & (s.anio == anio) & (s.mes <= hasta)]
    geo = geo[geo.km2 > 0].copy()
    geo["valor"] = geo.area_cod.map(sel.groupby("area_cod").valor.sum()).fillna(0)
    geo["dens"] = 1000 * geo.valor / geo.km2
    geo["zl"] = np.log10(geo.dens + 0.1)
    return geo


def figura_mapa(geo: gpd.GeoDataFrame, alto: int, ancho_px: int = 560, resaltar: str | None = None,
                zrango: tuple[float, float] | None = None, barra: bool = True) -> go.Figure:
    """A MapLibre map (light Carto basemap) framed on the areas' bounding box. The geo subplot keeps a fixed aspect
    ratio and left the country small in the panel; this fills it, and the user can zoom and pan."""
    zmin, zmax = zrango if zrango else (float(geo.zl.min()), float(geo.zl.max()))
    ticks = [v for v in [0.1, 0.3, 1, 3, 10, 30, 100, 300] if zmin - 0.3 <= math.log10(v + 0.1) <= zmax + 0.3]
    x0, y0, x1, y1 = geo.total_bounds
    merc = lambda lat: math.log(math.tan(math.pi / 4 + math.radians(lat) / 2))  # noqa: E731
    frac_y = max((merc(y1) - merc(y0)) / (2 * math.pi), 1e-6)
    frac_x = max((x1 - x0) / 360, 1e-6)
    zoom = min(math.log2(alto / 512 / frac_y), math.log2(ancho_px / 512 / frac_x)) - 0.3  # a little margin
    centro_lat = math.degrees(math.atan(math.sinh((merc(y0) + merc(y1)) / 2)))
    fig = go.Figure(go.Choroplethmap(
        geojson=json.loads(geo[["area_cod", "geometry"]].to_json()), featureidkey="properties.area_cod",
        locations=geo.area_cod, z=geo.zl, zmin=zmin, zmax=zmax, colorscale="YlOrRd",
        marker_line_width=0.5, marker_line_color="white", showscale=barra,
        customdata=np.stack([geo["area"], geo.valor.round(0), geo.dens.round(1)], axis=1),
        hovertemplate="<b>%{customdata[0]}</b><br>%{customdata[1]} " + t("cal.hover.valor") +
                      "<br>%{customdata[2]} " + t("mapa.leyenda") + "<extra></extra>",
        colorbar=dict(title=t("mapa.leyenda"), tickvals=[math.log10(v + 0.1) for v in ticks],
                      ticktext=[num(v, 1 if v < 1 else 0) for v in ticks], thickness=10)))
    if resaltar is not None and (geo.area_cod == resaltar).any():
        sel = geo[geo.area_cod == resaltar]
        fig.add_trace(go.Choroplethmap(geojson=json.loads(sel[["area_cod", "geometry"]].to_json()),
                                       featureidkey="properties.area_cod", locations=sel.area_cod, z=[0],
                                       colorscale=[[0, "rgba(0,0,0,0)"], [1, "rgba(0,0,0,0)"]], showscale=False,
                                       marker_line_width=3, marker_line_color="#111827", hoverinfo="skip"))
    fig.update_layout(height=alto, margin=dict(l=0, r=0, t=0, b=0),
                      map=dict(style="carto-positron", center=dict(lat=centro_lat, lon=(x0 + x1) / 2), zoom=zoom))
    return fig


CONFIG = {"displayModeBar": False, "scrollZoom": True}


def ranking(prov_cod: str, anio: int, n: int = 10) -> pd.DataFrame:
    """Areas with the most fire in the year (provinces, or departments of a province), with their own normal: the
    median of their 2003-2022 totals for the same months."""
    s = serie()
    ua, um = meta()["ultimo_mes_completo"]
    hasta = um if anio == ua else 12
    nivel = "provincia" if prov_cod == "00" else "departamento"
    x = s[(s.nivel == nivel) & (s.mes <= hasta)]
    if nivel == "departamento":
        x = x[x.prov_cod == prov_cod]
    tot = x.groupby(["area_cod", "area", "anio"]).valor.sum().reset_index()
    normal = tot[tot.anio.between(2003, 2022)].groupby("area_cod").valor.median().rename("normal")
    r = tot[tot.anio == anio].merge(normal, on="area_cod")
    r["razon"] = (r.valor + 1) / (r.normal + 1)
    return r.sort_values("valor", ascending=False).head(n)
