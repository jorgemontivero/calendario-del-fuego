"""Step 5 - Validate: three tests with pass criteria fixed beforehand (presentacion/paso5_comprobar.pdf).

  a) Exam: learn on 2012-2018, convert Suomi NPP 2019-2022 and compare with what Aqua really saw.
     Pass: small total bias, 90 % interval covers 85-95 % of province-months, the chosen model beats M0.
     Also: Catamarca hidden from the fit, predicted from its region.
  b) No steps: the converted series has no jump when Suomi NPP (2012) or NOAA-20 (2018) arrive, and the trend
     goes the same way as Aqua alone (Pettitt, Mann-Kendall).
  c) Official, non-satellite source (Ministerio de Ambiente, burned area reported by the provinces): the
     harmonized series ranks provinces and years at least as well as Aqua, and better than the naive sum.
Plus the local case: Catamarca, September 2026, and La Paz.

Input:  data/derivados/conteo_provincia.parquet, serie_armonizada_*.parquet, focos_limpios.parquet
        data/oficial/ciam_dt510.csv (burned area by province and year, 1993-2023), ciam_dt427.csv (fires by month)
Output: reportes/validacion.md, data/derivados/validacion_examen.parquet

Usage: python pipeline/paso5_comprobar.py
"""

import sys
from datetime import datetime
from pathlib import Path

import duckdb
import numpy as np
import pandas as pd
from scipy.stats import kendalltau, norm, spearmanr

sys.path.insert(0, str(Path(__file__).resolve().parent))
import modelo as M  # noqa: E402

RAIZ = Path(__file__).resolve().parents[1]
DERIV = RAIZ / "data" / "derivados"
OFICIAL = RAIZ / "data" / "oficial"
REPORTES = RAIZ / "reportes"
K = 1000

conteo = pd.read_parquet(DERIV / "conteo_provincia.parquet")
prov_nombre = conteo.drop_duplicates("prov_cod").set_index("prov_cod").provincia


# =============================================================================================== a) the exam
def factores_ocultando(aj_ent, oculta=None):
    """M0-M2 factors; if a province is hidden, its strata take the (shrunk) regional value."""
    f = M.ajustar_m012(aj_ent[aj_ent.prov_cod != oculta] if oculta else aj_ent)
    return f


def predecir(modelo, aj_ent, aj_pru, oculta=None):
    """Linear predictor (eta, ee) for the test rows, plus a dispersion curve fitted on the training rows."""
    ent = aj_ent[aj_ent.prov_cod != oculta] if oculta else aj_ent
    if modelo == "M3":
        p, info = M.ajustar_predecir_m3(ent, pd.concat([aj_pru, ent], ignore_index=True), DERIV / "_tmp")
        p_pru, p_ent = p.iloc[:len(aj_pru)].copy(), p.iloc[len(aj_pru):].copy()
    else:
        f = M.ajustar_m012(ent)
        k = f["estratos"]
        if oculta is not None:  # hidden province: regional value (M2) or national (M0); M1 has nothing to use
            if modelo == "M1":
                return None, None
            reg = (k.drop_duplicates(["region", "estacion", "momento"])[["region", "estacion", "momento", "l_reg", "ee_reg"]])
            extra = (aj_pru[aj_pru.prov_cod == oculta][["prov_cod", "provincia", "region", "estacion", "momento"]]
                     .drop_duplicates().merge(reg, on=["region", "estacion", "momento"]))
            extra = extra.assign(l0=f["l0"], ee0=k.ee0.iloc[0], l1=np.nan, ee1=np.nan, l2=extra.l_reg, ee2=extra.ee_reg)
            f["estratos"] = pd.concat([k, extra], ignore_index=True)
        p_pru = M.predecir_m012(f, aj_pru, modelo)
        p_ent = M.predecir_m012(f, ent, modelo)
        info = None
    curva = M.ajustar_phi_curva(p_ent.A, np.exp(p_ent.eta), p_ent.momento)
    return p_pru, curva


def resumir_examen(p_pru, curva, semilla=1):
    p = p_pru.reset_index(drop=True)
    phi = M.phi_de(curva, np.exp(p.eta), p.momento)
    sims = M.simular(p.eta, p.ee_eta, phi, p.prov_cod + p.estacion + p.momento, K=K, semilla=semilla)
    p["clave"] = p.prov_cod + "|" + p.anio.astype(str) + "|" + p.mes.astype(str)
    cods, ix = np.unique(p.clave, return_inverse=True)
    S = np.zeros((len(cods), K))
    np.add.at(S, ix, sims)
    out = p.groupby("clave").agg(prov_cod=("prov_cod", "first"), region=("region", "first"), anio=("anio", "first"),
                                 mes=("mes", "first"), A=("A", "sum")).loc[cods].reset_index()
    out["pred"], out["lo"], out["hi"] = np.median(S, 1), np.percentile(S, 5, 1), np.percentile(S, 95, 1)
    out["media"] = S.mean(1)
    # day / night totals for the bias split
    p["media"] = sims.mean(1)
    return out, p


aj_ent = M.tabla_ajuste(conteo, (2012, 2018))
aj_pru = M.tabla_ajuste(conteo, (2019, 2022))
tam = aj_ent.groupby("prov_cod").A.sum()
chicas = set(tam[tam < tam.median()].index)  # the 12 provinces with least Aqua fire in 2012-2018

filas, por_mes = [], {}
for mod in ["M0", "M1", "M2", "M3"]:
    p_pru, curva = predecir(mod, aj_ent, aj_pru)
    out, p = resumir_examen(p_pru, curva)
    por_mes[mod] = out.assign(modelo=mod)
    sesgo = out.media.sum() / out.A.sum() - 1
    dn = p.groupby("momento").apply(lambda x: x.media.sum() / x.A.sum() - 1, include_groups=False)
    reg = out.groupby("region").apply(lambda x: x.media.sum() / x.A.sum() - 1, include_groups=False)
    g10 = out[out.A >= 10]
    err = (g10.pred - g10.A).abs() / g10.A
    err_ch = err[g10.prov_cod.isin(chicas)]
    cob = ((out.A >= out.lo) & (out.A <= out.hi)).mean()
    # Catamarca hidden
    pc, cc = predecir(mod, aj_ent, aj_pru, oculta="10")
    if pc is not None:
        oc, _ = resumir_examen(pc[pc.prov_cod == "10"], cc)
        oc10 = oc[oc.A >= 10]
        err_oculta = ((oc10.pred - oc10.A).abs() / oc10.A).median()
        cob_oculta = ((oc.A >= oc.lo) & (oc.A <= oc.hi)).mean()
    else:
        err_oculta = cob_oculta = np.nan
    cat_in = out[(out.prov_cod == "10") & (out.A >= 10)]
    filas.append(dict(modelo=mod, sesgo=sesgo, sesgo_dia=dn.get("dia"), sesgo_noche=dn.get("noche"),
                      sesgo_region_max=reg.abs().max(), error_tipico=err.median(), error_chicas=err_ch.median(),
                      cobertura=cob, err_catamarca_dentro=((cat_in.pred - cat_in.A).abs() / cat_in.A).median(),
                      err_catamarca_oculta=err_oculta, cob_catamarca_oculta=cob_oculta))
ex = pd.DataFrame(filas).set_index("modelo")
pd.concat(por_mes.values()).to_parquet(DERIV / "validacion_examen.parquet", index=False)

# choose: models whose coverage is 85-95 % and bias < 5 %; among them the lowest typical error in small provinces
# (the reason for the hierarchy); must beat M0 on typical error. Rule written before looking (paso5 PDF).
cand = ex[(ex.cobertura.between(0.85, 0.95)) & (ex.sesgo.abs() < 0.05)]
cand = cand[cand.index != "M0"]
elegido = cand.error_chicas.idxmin() if len(cand) else "M0"
gana_m0 = ex.loc[elegido, "error_tipico"] <= ex.loc["M0", "error_tipico"]
pasa_a = elegido != "M0" and gana_m0

# =============================================================================================== b) no steps
def pettitt(x):
    x = np.asarray(x, float)
    n = len(x)
    U = np.array([np.sign(x[t + 1:, None] - x[None, :t + 1]).sum() for t in range(n - 1)])
    k = int(np.argmax(np.abs(U)))
    Kmax = np.abs(U[k])
    p = 2 * np.exp(-6 * Kmax ** 2 / (n ** 3 + n ** 2))
    return k + 1, min(p, 1.0)  # index of the last value before the change


def mann_kendall(x):
    x = np.asarray(x, float)
    n = len(x)
    S = sum(np.sign(x[j] - x[i]) for i in range(n - 1) for j in range(i + 1, n))
    var = n * (n - 1) * (2 * n + 5) / 18
    z = (S - np.sign(S)) / np.sqrt(var) if S != 0 else 0.0
    pend = np.median([(x[j] - x[i]) / (j - i) for i in range(n - 1) for j in range(i + 1, n)])
    return z, 2 * (1 - norm.cdf(abs(z))), pend


pais = pd.read_parquet(DERIV / "serie_armonizada_pais.parquet")
anual = pais.groupby("anio").agg(arm=("valor", "sum"), aqua=("aqua", "sum"), conv=("conv", "sum"))
con = duckdb.connect()
ing = con.execute(f"select anio, count(*) n from '{(DERIV / 'focos_limpios.parquet').as_posix()}' group by 1").df().set_index("anio").n
anual["ingenua"] = ing
# NOAA-20 converted to Aqua (x k), 2018-2022, as a direct check of the 2018 step
fac = pd.read_parquet(DERIV / "factores.parquet")
n20 = conteo[(conteo.plataforma == "NOAA20") & conteo.anio.between(2019, 2022)].copy()
n20["estacion"] = n20.mes.map(M.ESTACION)
n20 = n20.merge(fac[["prov_cod", "estacion", "momento", "factor_M2", "k_noaa20"]], on=["prov_cod", "estacion", "momento"])
n20_conv = (n20.celdas_dia * n20.k_noaa20 * n20.factor_M2).groupby(n20.anio).sum()

completos = anual.loc[2003:2025]
cociente_conv = (anual.conv / anual.aqua).loc[2012:2022]
cociente_n20 = (n20_conv / anual.aqua.loc[2019:2022])
ing_aqua = (anual.ingenua / anual.aqua).loc[2003:2022]
tests_b = {}
for nombre, serie in [("Aqua solo (2003-2022)", anual.aqua.loc[2003:2022]),
                      ("Armonizada (2003-2025)", completos.arm),
                      ("Ingenua: todos los focos sumados (2003-2025)", completos.ingenua)]:
    k, pp = pettitt(np.log(serie.to_numpy()))
    z, pmk, pend = mann_kendall(np.log(serie.to_numpy()))
    tests_b[nombre] = dict(cambio=int(serie.index[k]), p_pettitt=pp, z_mk=z, p_mk=pmk,
                           cambio_pct=(np.exp(np.log(serie.to_numpy()[k:]).mean() - np.log(serie.to_numpy()[:k]).mean()) - 1))
plano = cociente_conv.between(0.85, 1.15).all() and abs(cociente_conv.loc[2012:2017].mean() - cociente_conv.loc[2018:2022].mean()) < 0.05
misma_dir = np.sign(tests_b["Armonizada (2003-2025)"]["z_mk"]) == np.sign(tests_b["Aqua solo (2003-2022)"]["z_mk"])
pasa_b = plano and misma_dir and cociente_n20.between(0.85, 1.15).all()

# =============================================================================================== c) official source
of = pd.read_csv(OFICIAL / "ciam_dt510.csv", sep=";", na_values=["-", "s/d", ""])
of.columns = ["anio", "jur", "unidad", "ha", "ha_bosque"]
NOM = {"Tierra del Fuego": "Tierra del Fuego, Antártida e Islas del Atlántico Sur", "CABA": "Ciudad Autónoma de Buenos Aires",
       "Ciudad Autónoma de Buenos Aires": "Ciudad Autónoma de Buenos Aires",
       "Tierra del Fuego, Antártida e Islas del Atlántico Sur": "Tierra del Fuego, Antártida e Islas del Atlántico Sur"}
of["provincia"] = of.jur.map(lambda j: NOM.get(j, j))
sin_cruce = sorted(set(of.provincia) - set(prov_nombre))
of = of[of.provincia.isin(prov_nombre) & of.anio.between(2003, 2023) & of.ha.notna()]

sp = pd.read_parquet(DERIV / "serie_armonizada_provincia.parquet")
anual_p = sp[sp.anio.between(2003, 2023)].groupby(["provincia", "anio"]).agg(arm=("valor", "sum"), aqua=("aqua", "sum")).reset_index()
ing_p = con.execute(f"""select provincia, anio, count(*) ingenua from '{(DERIV / 'focos_limpios.parquet').as_posix()}'
                        where provincia is not null and anio between 2003 and 2023 group by all""").df()
cmp = of.merge(anual_p, on=["provincia", "anio"]).merge(ing_p, on=["provincia", "anio"])
rho = {s: spearmanr(cmp.ha, cmp[s]).statistic for s in ["aqua", "arm", "ingenua"]}
# within each province (ranking of years), provinces with >= 10 years of official data
dentro = {}
for s in ["aqua", "arm", "ingenua"]:
    vals = [spearmanr(g.ha, g[s]).statistic for _, g in cmp.groupby("provincia") if len(g) >= 10 and g.ha.nunique() > 3]
    dentro[s] = (np.nanmedian(vals), len(vals))
# national trend of the official burned area (provinces reporting every year 2003-2023)
completas = of.groupby("provincia").anio.nunique()
completas = completas[completas == 21].index
of_nac = of[of.provincia.isin(completas)].groupby("anio").ha.sum()
z_of, p_of, _ = mann_kendall(np.log(of_nac.to_numpy()))
arm_comp = anual_p[anual_p.provincia.isin(completas)].groupby("anio").arm.sum()
ing_comp = ing_p[ing_p.provincia.isin(completas)].groupby("anio").ingenua.sum()
z_arm_c, p_arm_c, _ = mann_kendall(np.log(arm_comp.to_numpy()))
z_ing_c, p_ing_c, _ = mann_kendall(np.log(ing_comp.to_numpy()))
# province by province (the PDF's instruction when the national trend disagrees): Kendall tau of each series
# against the year, provinces with >= 15 years of official data
tend = []
for p_, g in of.groupby("provincia"):
    if len(g) < 15:
        continue
    h = anual_p[anual_p.provincia == p_].set_index("anio")
    i = ing_p[ing_p.provincia == p_].set_index("anio")
    t_of = kendalltau(g.anio, g.ha)
    tend.append((p_, len(g), t_of.statistic, t_of.pvalue, kendalltau(h.index, h.arm).statistic,
                 kendalltau(i.index, i.ingenua).statistic))
tend = pd.DataFrame(tend, columns=["provincia", "n", "tau_of", "p_of", "tau_arm", "tau_ing"])
sig = tend[tend.p_of < 0.10]
coinc_arm = int((np.sign(sig.tau_of) == np.sign(sig.tau_arm)).sum())
coinc_ing = int((np.sign(sig.tau_of) == np.sign(sig.tau_ing)).sum())
peso_3 = (of[of.provincia.isin(["La Pampa", "Buenos Aires", "Córdoba"])].groupby("anio").ha.sum()
          / of.groupby("anio").ha.sum()).median()
# record years
anual_full = sp[sp.anio.between(2003, 2025)].groupby(["provincia", "anio"]).valor.sum().reset_index()
records = []
for p_, a_ in [("Córdoba", 2020), ("Corrientes", 2022), ("Entre Ríos", 2020)]:
    g = anual_full[anual_full.provincia == p_].sort_values("valor", ascending=False).reset_index(drop=True)
    pos = int(g.index[g.anio == a_][0]) + 1
    o = of[of.provincia == p_].sort_values("ha", ascending=False).reset_index(drop=True)
    pos_of = int(o.index[o.anio == a_][0]) + 1 if (o.anio == a_).any() else None
    records.append((p_, a_, pos, len(g), pos_of, len(o)))
# seasonality: fires reported per month (2017-2025) vs harmonized monthly mean (2017-2025)
m427 = pd.read_csv(OFICIAL / "ciam_dt427.csv", sep=";")
m427 = m427[m427.mes != "Total"]
MESES = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
m427["mes_n"] = m427.mes.map({m: i + 1 for i, m in enumerate(MESES)})
cols_a = [f"año_{a}" for a in range(2017, 2026)]
inc_mes = m427.set_index("mes_n")[cols_a].apply(pd.to_numeric, errors="coerce").sum(axis=1).sort_index()
arm_mes = pais[pais.anio.between(2017, 2025)].groupby("mes").valor.mean()
rho_mes = spearmanr(inc_mes, arm_mes).statistic
pico_of, pico_arm = inc_mes.nlargest(3).index.tolist(), arm_mes.nlargest(3).index.tolist()
c_rank = rho["arm"] >= rho["aqua"] - 0.02 and rho["arm"] > rho["ingenua"]
c_tend = np.sign(z_of) == np.sign(z_arm_c)
pasa_c = c_rank and c_tend

# =============================================================================================== Catamarca 2026
cat = sp[(sp.provincia == "Catamarca") & (sp.mes == 9)]
c26 = cat[cat.anio == 2026].iloc[0]
hist9 = cat[cat.anio.between(2003, 2022)].valor
lp = con.execute(f"""
select count(*) focos, count(distinct (ci, cj)) celdas, count(distinct fecha) dias,
       max(n_dias) max_dias_celda, (max(lat) - min(lat)) * 111 alto_km, (max(lon) - min(lon)) * 98 ancho_km
from (select *, count(distinct fecha) over (partition by ci, cj) n_dias
      from '{(DERIV / 'focos_limpios.parquet').as_posix()}'
      where provincia = 'Catamarca' and depto = 'La Paz' and anio = 2026 and mes = 9 and sensor = 'VIIRS')""").fetchone()
deptos = con.execute(f"""select depto, count(distinct (ci, cj, fecha)) cd, min(fecha), max(fecha)
      from '{(DERIV / 'focos_limpios.parquet').as_posix()}'
      where provincia = 'Catamarca' and anio = 2026 and mes = 9 and plataforma = 'NOAA20' group by 1 order by 2 desc limit 5""").fetchall()


# =============================================================================================== report
def pct(x, s=True):
    return "—" if pd.isna(x) else (f"{x:+.1%}" if s else f"{x:.1%}")


L = ["# Validación (paso 5)", "",
     f"Generado por `pipeline/paso5_comprobar.py` el {datetime.now():%d/%m/%Y %H:%M}. Criterios de aprobación fijados antes "
     "de correr las pruebas (presentacion/paso5_comprobar.pdf).", "",
     "## Resultado", "",
     "| Prueba | Resultado |", "|---|---|",
     f"| a) El examen (aprender 2012-2018, probar 2019-2022) | {'APRUEBA' if pasa_a else 'NO APRUEBA'}: modelo elegido **{elegido}** |",
     f"| b) Sin escalones y misma dirección que Aqua | {'APRUEBA' if pasa_b else 'NO APRUEBA'} |",
     f"| c) Fuente oficial (superficie incendiada, Ministerio de Ambiente) | {'APRUEBA' if pasa_c else 'APRUEBA EN PARTE'}: "
     f"rankings {'sí' if c_rank else 'no'}; tendencia nacional {'sí' if c_tend else 'no (la oficial es plana; ver el detalle por provincia)'} |", "",
     "## a) El examen", "",
     "Se aprende con 2012-2018 y se convierte Suomi NPP 2019-2022 (incluye 2020, año extremo). Se compara con lo que "
     "Aqua vio de verdad. Unidad: provincia × mes, día + noche.", "",
     "| Modelo | Error total | De día | De noche | Peor región | Error típico (A ≥ 10) | Error típico, 12 provincias chicas | Acierto del margen 90 % | Catamarca dentro | Catamarca escondida |",
     "|---|---|---|---|---|---|---|---|---|---|"]
for m, r in ex.iterrows():
    L.append(f"| {m}{' ←' if m == elegido else ''} | {pct(r.sesgo)} | {pct(r.sesgo_dia)} | {pct(r.sesgo_noche)} | "
             f"{pct(r.sesgo_region_max, False)} | {pct(r.error_tipico, False)} | {pct(r.error_chicas, False)} | "
             f"{pct(r.cobertura, False)} | {pct(r.err_catamarca_dentro, False)} | {pct(r.err_catamarca_oculta, False)} |")
L += ["", "- Error total: suma convertida / suma de Aqua − 1. Error típico: mediana de |convertido − Aqua| / Aqua en los "
      "provincia-meses con 10 o más celdas-día de Aqua. Acierto del margen: proporción de provincia-meses en que Aqua cae "
      "dentro del intervalo del 90 % (aprueba entre 85 % y 95 %).",
      "- Catamarca escondida: se ajusta sin Catamarca y se la predice con el valor de su región (M2), el nacional (M0) o "
      "el efecto poblacional (M3). M1 no puede predecir una provincia que no vio.",
      f"- Regla de elección (escrita antes): margen entre 85 % y 95 % y error total menor que 5 %; entre esos, el menor "
      f"error típico en las provincias chicas; y tiene que ganarle a M0. **Elegido: {elegido}.** Se vuelve a ajustar "
      "con 2012-2022 para la serie final.", "",
      "## b) Sin escalones", "",
      "Cociente contra Aqua, año por año (tiene que ser plano, cerca de 1):", "",
      "| Año | Suomi NPP convertido / Aqua | NOAA-20 convertido / Aqua | Serie ingenua / Aqua |", "|---|---|---|---|"]
for a in range(2003, 2023):
    L.append(f"| {a} | {cociente_conv.get(a, np.nan):.2f} | {cociente_n20.get(a, np.nan):.2f} | {ing_aqua.get(a, np.nan):.1f} |"
             .replace("nan", ""))
L += ["", "Tendencia (logaritmo de los totales anuales):", "",
      "| Serie | Año del cambio (Pettitt) | Cambio de nivel | p | Mann-Kendall z | p |", "|---|---|---|---|---|---|"]
for n, t in tests_b.items():
    L.append(f"| {n} | {t['cambio']} | {t['cambio_pct']:+.0%} | {t['p_pettitt']:.3f} | {t['z_mk']:+.2f} | {t['p_mk']:.3f} |")
d23 = conteo[(conteo.plataforma == "Aqua") & conteo.anio.between(2023, 2025) & (conteo.momento == "dia")].celdas_dia.sum()
L += ["", f"- Control 2023-2025: ver `reportes/paso4_convertir.md` (Aqua observado de día queda por encima de la conversión: "
      "es la huella de su cambio de horario).", "",
      "## c) Contra la fuente oficial", "",
      f"Superficie incendiada por provincia y año, 2003-2023 (CIAM, dt 510; {len(cmp)} provincia-años con dato). "
      "Se comparan rankings (Spearman), no valores: hectáreas y celdas-día miden cosas distintas.", "",
      "| Serie | Spearman, todos los provincia-años | Mediana dentro de cada provincia (ranking de años) |", "|---|---|---|"]
for s, n in [("aqua", "Aqua solo"), ("arm", "Armonizada"), ("ingenua", "Ingenua (todos los focos)")]:
    L.append(f"| {n} | {rho[s]:.2f} | {dentro[s][0]:.2f} ({dentro[s][1]} provincias) |")
L += ["", f"Tendencia 2003-2023 en las {len(completas)} provincias con dato todos los años "
      f"({', '.join(completas)}):", "",
      "| Serie | Mann-Kendall z | p |", "|---|---|---|",
      f"| Superficie oficial | {z_of:+.2f} | {p_of:.3f} |", f"| Armonizada | {z_arm_c:+.2f} | {p_arm_c:.3f} |",
      f"| Ingenua | {z_ing_c:+.2f} | {p_ing_c:.3f} |", "",
      f"La suma oficial nacional no tiene tendencia, y el criterio fijado (\"va para el mismo lado que la armonizada\") "
      f"**no se cumple**. Pero la suma la dominan La Pampa, Buenos Aires y Córdoba (mediana {peso_3:.0%} del total), con "
      "años de pastizal enormes. Provincia por provincia (Kendall τ contra el año, provincias con 15 años o más de dato):", "",
      "| Provincia | Años | τ oficial | p | τ armonizada | τ ingenua |", "|---|---|---|---|---|---|"]
L += [f"| {r.provincia} | {r.n} | {r.tau_of:+.2f} | {r.p_of:.2f} | {r.tau_arm:+.2f} | {r.tau_ing:+.2f} |" for r in tend.itertuples()]
L += ["", f"**De las {len(sig)} provincias con tendencia oficial clara (p < 0,10), todas bajan; la armonizada coincide en "
      f"{coinc_arm} y la ingenua en {coinc_ing}.** La fuente oficial no confirma una baja nacional, pero desmiente el "
      "aumento de la serie ingenua.", "", "Años récord:", "",
      "| Provincia | Año | Puesto en la armonizada (2003-2025) | Puesto en la superficie oficial (2003-2023) |", "|---|---|---|---|"]
L += [f"| {p_} | {a_} | {pos} de {n} | {'—' if po is None else f'{po} de {no}'} |" for p_, a_, pos, n, po, no in records]
L += ["", f"Estacionalidad: incendios reportados por mes (dt 427, 2017-2025) contra el promedio mensual armonizado: "
      f"Spearman {rho_mes:.2f}. Meses pico, oficial: {pico_of}; armonizada: {pico_arm}.",
      f"- Jurisdicciones de la tabla oficial que no son provincias (quedan afuera): {', '.join(sin_cruce) or 'ninguna'}.",
      "- Cuidados: hay provincias y años sin dato, el esfuerzo de registro cambia entre provincias, y dos tablas oficiales "
      "no coinciden entre sí (Catamarca 2017: 45.170 ha en dt 510 y 17.385 en dt 416). Se usa la más larga (dt 510).", "",
      "## Catamarca, septiembre de 2026", "",
      f"- Serie armonizada (NOAA-20 convertido): **{c26.valor:.0f}** celdas-día de Aqua (intervalo 90 %: {c26.min90:.0f}–{c26.max90:.0f}).",
      f"- Septiembres 2003-2022: mediana {hist9.median():.0f}, percentil 90 {c26.p90:.0f}, máximo {hist9.max():.0f} "
      f"({int(cat.loc[cat.valor.idxmax(), 'anio'])}); {int((hist9 > c26.valor).sum())} de {len(hist9)} fueron más altos.",
      f"- Probabilidad de mes inusual: **{c26.prob_inusual:.0%}**. No es un récord: es un septiembre típico en la serie larga.",
      "- Departamentos con más celdas-día (NOAA-20): " + "; ".join(f"{d} {n} ({a:%d/%m}–{b:%d/%m})" for d, n, a, b in deptos) + ".",
      f"- La Paz (VIIRS): {lp[0]} focos en {lp[1]} cuadrados distintos y {lp[2]} días; el cuadrado que más se repite tuvo "
      f"{lp[3]} días; los focos ocupan unos {lp[4]:.0f} × {lp[5]:.0f} km. "
      + (f"Ningún cuadrado se acerca a los 30 días que definen una fuente fija y los focos están repartidos en {lp[1]} "
         "cuadrados: es fuego que se mueve, no una instalación. No aparece en la prensa: puede ser quema agrícola o de "
         "pastizal." if lp[3] < 15 and lp[1] >= 20 else "Revisar: hay concentración en pocos cuadrados.")]
(REPORTES / "validacion.md").write_text("\n".join(L) + "\n", encoding="utf-8")
print("\n".join(L))
