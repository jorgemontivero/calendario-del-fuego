"""Step 4 - Convert: one series in "Aqua cell-days" for every province and month since 2003, with its margin.

Input:  data/derivados/conteo_provincia.parquet, conteo_departamento.parquet (step 3)
Output: data/derivados/serie_armonizada_provincia.parquet  province x month, 2003-today
        data/derivados/serie_armonizada_pais.parquet       Argentina x month (sum of the provincial simulations)
        data/derivados/serie_armonizada_departamento.parquet  department x month, point values (for the app)
        data/derivados/factores.parquet                    conversion factor per province x season x day/night
        reportes/paso4_convertir.md

Which number goes in each year (modelo.md 4.2):
  2003-2022  Aqua observed (the reference). 2012-2022 also gets Suomi NPP converted, as a check.
  2023-2025  Suomi NPP converted (Aqua's overpass drifted later from 2023 and stopped being a fixed reference).
  2026       NOAA-20 converted, scaled to Suomi NPP with k = SNPP / NOAA-20 (2019-2022, per day/night).
The conversion is fitted on 2012-2022 (Aqua and Suomi NPP flying together at the same hour).

The model is chosen in step 5 (validation); MODELO below holds that choice.

Usage: python pipeline/paso4_convertir.py
"""

import sys
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import modelo as M  # noqa: E402

MODELO = "M2"  # provisional until step 5 decides
K = 1000
RAIZ = Path(__file__).resolve().parents[1]
DERIV = RAIZ / "data" / "derivados"
REPORTES = RAIZ / "reportes"

conteo = pd.read_parquet(DERIV / "conteo_provincia.parquet")
dep = pd.read_parquet(DERIV / "conteo_departamento.parquet")

# --- 1. fit on 2012-2022 --------------------------------------------------------------------------------------
aj = M.tabla_ajuste(conteo, (2012, 2022))
fact = M.ajustar_m012(aj)
est = fact["estratos"]

# NOAA-20 -> Suomi NPP scale (national, per day/night, complete months 2019-2022)
kk = (conteo[conteo.anio.between(2019, 2022) & conteo.mes_completo & conteo.plataforma.isin(["SNPP", "NOAA20"])]
      .groupby(["momento", "plataforma"]).celdas_dia.sum().unstack())
k_n20 = (kk.SNPP / kk.NOAA20).to_dict()

# --- 2. rows to convert: Suomi NPP 2012-2025, NOAA-20 (x k) 2026 ---------------------------------------------
claves = ["prov_cod", "provincia", "anio", "mes", "momento"]
v_snpp = conteo[(conteo.plataforma == "SNPP") & conteo.anio.between(2012, 2025)][claves + ["celdas_dia", "mes_completo"]]
v_n20 = conteo[(conteo.plataforma == "NOAA20") & (conteo.anio == 2026)][claves + ["celdas_dia", "mes_completo"]].copy()
v_n20["celdas_dia"] = v_n20.celdas_dia * v_n20.momento.map(k_n20)
filas = pd.concat([v_snpp.assign(fuente_viirs="SNPP"), v_n20.assign(fuente_viirs="NOAA20")], ignore_index=True)
filas = filas.rename(columns={"celdas_dia": "V"})
filas["estacion"] = filas.mes.map(M.ESTACION)
filas["region"] = filas.prov_cod.map(M.REGION)

if MODELO == "M3":
    pred, info_m3 = M.ajustar_predecir_m3(aj, filas, DERIV / "_tmp")
    phi = info_m3["phi"]
else:
    pred = M.predecir_m012(fact, filas, MODELO)
    entren = M.predecir_m012(fact, aj, MODELO)
    info_m3 = None
# dispersion grows with the size of the month: phi = a * mu^b per day/night (see modelo.ajustar_phi_curva)
if MODELO == "M3":
    entren, _ = M.ajustar_predecir_m3(aj, aj, DERIV / "_tmp")
curva_phi = M.ajustar_phi_curva(entren.A, np.exp(entren.eta), entren.momento)
phi = curva_phi

# --- 3. simulate: factor uncertainty + counting noise; day + night summed ------------------------------------
pred = pred.reset_index(drop=True)
grupo = pred.prov_cod + "|" + pred.estacion + "|" + pred.momento
sims = M.simular(pred.eta, pred.ee_eta, M.phi_de(curva_phi, np.exp(pred.eta), pred.momento), grupo, K=K)
pred["clave"] = pred.prov_cod + "|" + pred.anio.astype(str) + "|" + pred.mes.astype(str)
codigos, idx = np.unique(pred.clave, return_inverse=True)
S = np.zeros((len(codigos), K))
np.add.at(S, idx, sims)  # province-month x K (day + night)
meta = pred.groupby("clave").agg(prov_cod=("prov_cod", "first"), provincia=("provincia", "first"), anio=("anio", "first"),
                                 mes=("mes", "first"), fuente_viirs=("fuente_viirs", "first"),
                                 mes_completo_viirs=("mes_completo", "all")).loc[codigos].reset_index()

# country: the same simulation index summed over provinces (keeps the shared factor draws together)
meta["clave_pais"] = meta.anio.astype(str) + "|" + meta.mes.astype(str)
cp, ip = np.unique(meta.clave_pais, return_inverse=True)
SP = np.zeros((len(cp), K))
np.add.at(SP, ip, S)

# --- 4. Aqua observed and the "unusual" threshold (90th percentile of Aqua 2003-2022, per month of the year) --
aqua = (conteo[(conteo.plataforma == "Aqua") & conteo.anio.between(2003, 2026)]
        .groupby(["prov_cod", "provincia", "anio", "mes"]).agg(aqua=("celdas_dia", "sum"), aqua_completo=("mes_completo", "all"))
        .reset_index())
aqua_pais = aqua.groupby(["anio", "mes"]).agg(aqua=("aqua", "sum"), aqua_completo=("aqua_completo", "all")).reset_index()
hist = aqua[aqua.anio.between(2003, 2022)]
p90 = hist.groupby(["prov_cod", "mes"]).aqua.quantile(0.9).rename("p90").reset_index()
p90_pais = aqua_pais[aqua_pais.anio.between(2003, 2022)].groupby("mes").aqua.quantile(0.9).rename("p90").reset_index()


def resumir(sim, umbral):
    return pd.DataFrame({"conv": np.median(sim, axis=1), "conv_min90": np.percentile(sim, 5, axis=1),
                         "conv_max90": np.percentile(sim, 95, axis=1),
                         "conv_prob_inusual": (sim > umbral[:, None]).mean(axis=1)})


meta = meta.merge(p90, on=["prov_cod", "mes"], how="left")
meta = pd.concat([meta, resumir(S, meta.p90.to_numpy())], axis=1)
pais = pd.DataFrame({"clave_pais": cp})
pais[["anio", "mes"]] = pais.clave_pais.str.split("|", expand=True).astype(int)
pais = pais.merge(p90_pais, on="mes", how="left")
pais = pd.concat([pais, resumir(SP, pais.p90.to_numpy())], axis=1)
pais["fuente_viirs"] = np.where(pais.anio == 2026, "NOAA20", "SNPP")


def armar(obs, conv, claves_):
    s = obs.merge(conv, on=claves_, how="outer")
    usa_aqua = s.anio <= 2022
    s["origen"] = np.where(usa_aqua, "Aqua observado",
                           np.where(s.fuente_viirs == "NOAA20", "NOAA-20 convertido", "Suomi NPP convertido"))
    s["valor"] = np.where(usa_aqua, s.aqua, s.conv)
    s["min90"] = np.where(usa_aqua, s.aqua, s.conv_min90)
    s["max90"] = np.where(usa_aqua, s.aqua, s.conv_max90)
    s["prob_inusual"] = np.where(usa_aqua, (s.aqua > s.p90).astype(float), s.conv_prob_inusual)
    s["mes_completo"] = np.where(usa_aqua, s.aqua_completo, s.mes_completo_viirs if "mes_completo_viirs" in s else True)
    s.loc[~s.mes_completo.astype(bool), "prob_inusual"] = np.nan  # a partial month is not comparable
    s = s[s.anio >= 2003]
    return s


prov = armar(aqua, meta.drop(columns=["clave", "clave_pais"]), ["prov_cod", "provincia", "anio", "mes"])
prov = prov.drop(columns=["p90_x"], errors="ignore").rename(columns={"p90_y": "p90"})
prov["region"] = prov.prov_cod.map(M.REGION)
prov = prov.sort_values(["prov_cod", "anio", "mes"])
cols = ["prov_cod", "provincia", "region", "anio", "mes", "valor", "min90", "max90", "prob_inusual", "origen",
        "mes_completo", "p90", "aqua", "conv", "conv_min90", "conv_max90"]
prov = prov.rename(columns={"aqua": "aqua"})[cols]

pais_s = armar(aqua_pais, pais.drop(columns=["clave_pais"]).assign(mes_completo_viirs=True), ["anio", "mes"])
pais_s = pais_s.drop(columns=["p90_x"], errors="ignore").rename(columns={"p90_y": "p90"})
pais_s.loc[(pais_s.anio == 2026) & (pais_s.mes == 11), ["mes_completo", "prob_inusual"]] = [False, np.nan]
pais_s = pais_s.assign(prov_cod="00", provincia="Argentina", region="País").sort_values(["anio", "mes"])[cols]

# departments: point conversion with the province factor (the app's area view)
fac = est[["prov_cod", "estacion", "momento"]].copy()
fac["factor"] = np.exp(est[{"M0": "l0", "M1": "l1", "M2": "l2"}.get(MODELO, "l2")])
d = dep.copy()
d["estacion"] = d.mes.map(M.ESTACION)
d = d.merge(fac, on=["prov_cod", "estacion", "momento"], how="left")
d["k"] = np.where(d.plataforma == "NOAA20", d.momento.map(k_n20), 1.0)
d["conv"] = d.celdas_dia * d.k * d.factor
obs_d = d[(d.plataforma == "Aqua") & d.anio.between(2003, 2022)].groupby(["prov_cod", "depto_cod", "depto", "anio", "mes"]).celdas_dia.sum()
cv_snpp = d[(d.plataforma == "SNPP") & d.anio.between(2023, 2025)].groupby(["prov_cod", "depto_cod", "depto", "anio", "mes"]).conv.sum()
cv_n20 = d[(d.plataforma == "NOAA20") & (d.anio == 2026)].groupby(["prov_cod", "depto_cod", "depto", "anio", "mes"]).conv.sum()
serie_dep = pd.concat([obs_d.rename("valor").reset_index().assign(origen="Aqua observado"),
                       cv_snpp.rename("valor").reset_index().assign(origen="Suomi NPP convertido"),
                       cv_n20.rename("valor").reset_index().assign(origen="NOAA-20 convertido")], ignore_index=True)

factores = est[["prov_cod", "provincia", "region", "estacion", "momento", "A", "V", "l1", "l2", "ee2", "w", "l_reg"]].copy()
factores["factor_M2"] = np.exp(factores.l2)
factores["veces_M2"] = 1 / factores.factor_M2
factores["veces_propio"] = np.exp(-factores.l1)
factores["veces_region"] = np.exp(-factores.l_reg)
factores["k_noaa20"] = factores.momento.map(k_n20)
factores["phi_a"] = factores.momento.map(lambda m: curva_phi[m][0])
factores["phi_b"] = factores.momento.map(lambda m: curva_phi[m][1])
factores["modelo"] = MODELO

prov.to_parquet(DERIV / "serie_armonizada_provincia.parquet", index=False)
pais_s.to_parquet(DERIV / "serie_armonizada_pais.parquet", index=False)
serie_dep.to_parquet(DERIV / "serie_armonizada_departamento.parquet", index=False)
factores.to_parquet(DERIV / "factores.parquet", index=False)

# --- 5. quick checks (the real test is step 5) -----------------------------------------------------------------
chk = []


def control(n, ok, det):
    chk.append((n, bool(ok), det))


control("Un factor para cada estrato, sin vacíos ni infinitos", np.isfinite(est[["l0", "l1", "l2", "ee2"]]).all().all()
        and len(est) == 24 * 4 * 2, f"{len(est)} estratos")
vd = factores[factores.momento == "dia"].veces_M2
vn = factores[factores.momento == "noche"].veces_M2
control("Factores razonables: de día entre 2 y 5; de noche más altos", vd.between(2, 5).all() and (vn.median() > vd.median() * 2),
        f"día {vd.min():.2f}-{vd.max():.2f} (mediana {vd.median():.2f}); noche {vn.min():.2f}-{vn.max():.2f} (mediana {vn.median():.2f})")
cat = factores[factores.provincia == "Catamarca"]
entre = ((cat.veces_M2 - cat.veces_propio) * (cat.veces_M2 - cat.veces_region) <= 1e-9).all()
control("Catamarca queda entre su propio número y el del NOA", entre,
        "; ".join(f"{r.estacion} {r.momento}: {r.veces_propio:.1f} → {r.veces_M2:.1f} (NOA {r.veces_region:.1f}, peso {r.w:.2f})" for r in cat.itertuples()))
chq = pais_s[pais_s.anio.between(2012, 2022)].groupby("anio")[["aqua", "conv"]].sum()
sesgo = chq.conv.sum() / chq.aqua.sum() - 1
control("2012-2022: Suomi NPP convertido se parece a Aqua en el total del país", abs(sesgo) < 0.10,
        f"sesgo total {sesgo:+.1%}; por año {(chq.conv / chq.aqua - 1).min():+.1%} a {(chq.conv / chq.aqua - 1).max():+.1%}")
# drift: daytime only, 2023-2025
dd = pred[(pred.anio.between(2023, 2025)) & (pred.momento == "dia")]
conv_dia = np.median(sims[dd.index.to_numpy()].sum(axis=0))
aqua_dia = conteo[(conteo.plataforma == "Aqua") & conteo.anio.between(2023, 2025) & (conteo.momento == "dia")].celdas_dia.sum()
control("2023-2025, de día: Aqua observado por encima de la conversión (deriva de horario)", aqua_dia > conv_dia,
        f"Aqua {aqua_dia:,.0f} contra convertido {conv_dia:,.0f} ({aqua_dia / conv_dia - 1:+.1%})")
cob = prov[prov.anio.between(2012, 2022) & prov.aqua.notna() & prov.conv.notna()]
cobertura = ((cob.aqua >= cob.conv_min90) & (cob.aqua <= cob.conv_max90)).mean()
control("Vista previa: cobertura del intervalo del 90 % en 2012-2022 (dentro de muestra)", 0.80 <= cobertura <= 0.98,
        f"{cobertura:.1%} de {len(cob):,} provincia-meses")


# --- 6. report ------------------------------------------------------------------------------------------------
def miles(x):
    return f"{x:,.0f}".replace(",", ".")


anual = pais_s[pais_s.mes_completo.astype(bool) | (pais_s.anio < 2026)].groupby("anio").agg(
    valor=("valor", "sum"), min90=("min90", "sum"), max90=("max90", "sum"), origen=("origen", "first"))
ingenuo = conteo.groupby(["plataforma", "anio"]).celdas_dia.sum().unstack(0)
L = ["# Paso 4: convertir", "",
     f"Generado por `pipeline/paso4_convertir.py` el {datetime.now():%d/%m/%Y %H:%M}. Modelo: **{MODELO}** "
     "(provisorio hasta la validación del paso 5). Ajuste: Aqua contra Suomi NPP, 2012-2022, meses completos.", "",
     f"- Inflación de la varianza de muestreo `c` = {fact['c']:.2f}; varianza real entre provincias "
     f"τ² = {fact['tau2']['dia']:.3f} (día) y {fact['tau2']['noche']:.3f} (noche).",
     f"- Dispersión de la binomial negativa, creciente con el tamaño del mes: φ = {curva_phi['dia'][0]:.2f}·μ^{curva_phi['dia'][1]:.2f} (día), "
     f"{curva_phi['noche'][0]:.2f}·μ^{curva_phi['noche'][1]:.2f} (noche).",
     f"- NOAA-20 → Suomi NPP: k = {k_n20['dia']:.3f} (día), {k_n20['noche']:.3f} (noche).",
     f"- M0, un solo número para todo: Suomi NPP ve {np.exp(-fact['l0']):.2f} veces más que Aqua.", "",
     "## Cuántas veces más ve Suomi NPP que Aqua (M2)", "",
     "| Región | Estación | Día | Noche |", "|---|---|---|---|"]
reg = factores.groupby(["region", "estacion", "momento"]).veces_region.first().unstack()
L += [f"| {r} | {e} | {v.dia:.2f} | {v.noche:.2f} |" for (r, e), v in reg.iterrows()]
L += ["", "## Catamarca", "", "| Estación | Momento | Celdas-día Aqua | Celdas-día SNPP | Propio | NOA | M2 | Peso propio |",
      "|---|---|---|---|---|---|---|---|"]
L += [f"| {r.estacion} | {r.momento} | {miles(r.A)} | {miles(r.V)} | {r.veces_propio:.2f} | {r.veces_region:.2f} | {r.veces_M2:.2f} | {r.w:.2f} |"
      for r in cat.itertuples()]
L += ["", "## Serie armonizada del país (celdas-día de Aqua por año)", "",
      "| Año | Valor | Intervalo 90 % | Origen | Aqua observado | Suma ingenua de todos los satélites |", "|---|---|---|---|---|---|"]
aqua_anual = aqua_pais.groupby("anio").aqua.sum()
for a, r in anual.iterrows():
    ing = ingenuo.loc[a].sum() if a in ingenuo.index else np.nan
    L.append(f"| {a} | {miles(r.valor)} | {miles(r.min90)}–{miles(r.max90)} | {r.origen} | "
             f"{miles(aqua_anual.get(a, np.nan))} | {miles(ing)} |")
L += ["", "2026 llega hasta el 14/11: el año está incompleto.", "", "## Controles rápidos", ""]
L += [f"- {'OK' if ok else 'REVISAR'} — {n}: {d}" for n, ok, d in chk]
(REPORTES / "paso4_convertir.md").write_text("\n".join(L) + "\n", encoding="utf-8")
print("\n".join(L))
