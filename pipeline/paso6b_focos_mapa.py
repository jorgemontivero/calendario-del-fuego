"""Step 6b - Hot spot positions for the map of the Spatial analysis view.

Every cleaned hot spot (step 2) since 2003, one row each: province, department, local date, satellite, day/night,
position and fire radiative power. These are raw FIRMS detections, NOT harmonized: the app shows one satellite at a
time and says so. The position is the centre of the pixel where heat was detected (375 m VIIRS, 1 km MODIS), rounded
to 0.001 degrees (~100 m, well inside the pixel).

Sorted by province and date, in row groups of 100,000, so the app reads only the groups of the province and period
it asks for (DuckDB skips the rest) and never loads the whole file into memory.

Input:  data/derivados/focos_limpios.parquet
Output: app/datos/focos.parquet  (~35 MB)

Usage: python pipeline/paso6b_focos_mapa.py
"""

from pathlib import Path

import duckdb

RAIZ = Path(__file__).resolve().parents[1]
ENT = (RAIZ / "data" / "derivados" / "focos_limpios.parquet").as_posix()
SAL = RAIZ / "app" / "datos" / "focos.parquet"

con = duckdb.connect()
con.execute(f"""
copy (
    select prov_cod, depto_cod, cast(fecha as date) as fecha, plataforma, dia,
           round(lat, 3)::float as lat, round(lon, 3)::float as lon, round(frp, 1)::float as frp
    from '{ENT}'
    where anio >= 2003 and prov_cod is not null
    order by prov_cod, fecha
) to '{SAL.as_posix()}' (format parquet, compression zstd, row_group_size 100000)""")

n, desde, hasta = con.execute(f"select count(*), min(fecha), max(fecha) from '{SAL.as_posix()}'").fetchone()
total = con.execute(f"select count(*) from '{ENT}' where anio >= 2003 and prov_cod is not null").fetchone()[0]
assert n == total, (n, total)
print(f"{SAL.name}: {n:,} hot spots, {desde} to {hasta}, {SAL.stat().st_size / 1e6:.1f} MB")
