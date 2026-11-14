"""Conversion models VIIRS -> Aqua-equivalent cell-days (shared by step 4 and step 5).

Notation (modelo.md): A = Aqua cell-days, V = VIIRS (Suomi NPP) cell-days, for one province x year x month x
day/night. A stratum k = (province, season, day/night). Factors are expressed as log(A / V) ("Aqua per VIIRS",
below 1); the "times more" figure people quote is 1 / exp(factor).

M0  one national factor.
M1  one factor per stratum.
M2  M1 shrunk toward the region, and the region toward the country (empirical Bayes, method of moments).
M3  negative binomial mixed model in R (glmmTMB): A ~ log(V + 0.5) + season * daynight + (1 | region/province).
"""

import subprocess
from pathlib import Path

import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parents[1]
RSCRIPT = Path(r"C:\Program Files\R\R-4.5.2\bin\Rscript.exe")

ESTACION = {12: "DEF", 1: "DEF", 2: "DEF", 3: "MAM", 4: "MAM", 5: "MAM",
            6: "JJA", 7: "JJA", 8: "JJA", 9: "SON", 10: "SON", 11: "SON"}
REGION = {  # INDEC regions, keyed by IGN province code (modelo.md, section 7)
    "02": "Pampeana", "06": "Pampeana", "14": "Pampeana", "30": "Pampeana", "42": "Pampeana", "82": "Pampeana",
    "10": "NOA", "38": "NOA", "46": "NOA", "66": "NOA", "86": "NOA", "90": "NOA",
    "18": "NEA", "22": "NEA", "34": "NEA", "54": "NEA",
    "50": "Cuyo", "70": "Cuyo", "74": "Cuyo",
    "26": "Patagonia", "58": "Patagonia", "62": "Patagonia", "78": "Patagonia", "94": "Patagonia",
}
ESTRATO = ["prov_cod", "estacion", "momento"]


def tabla_ajuste(conteo: pd.DataFrame, anios, viirs="SNPP") -> pd.DataFrame:
    """Province x year x month x day/night with A (Aqua) and V (`viirs`), complete months only."""
    c = conteo[conteo.anio.between(*anios) & conteo.mes_completo & conteo.plataforma.isin(["Aqua", viirs])]
    aj = c.pivot_table(index=["prov_cod", "provincia", "anio", "mes", "momento"], columns="plataforma",
                       values="celdas_dia").dropna().reset_index()
    aj = aj.rename(columns={"Aqua": "A", viirs: "V"})
    aj["estacion"] = aj.mes.map(ESTACION)
    aj["region"] = aj.prov_cod.map(REGION)
    assert aj.region.notna().all()
    return aj


# --------------------------------------------------------------------------------------------- M0, M1, M2
def _log_cociente(A, V):
    return np.log((A + 0.5) / (V + 0.5)), 1 / (A + 0.5) + 1 / (V + 0.5)


def inflacion_c(aj: pd.DataFrame) -> float:
    """c in modelo.md 3.3, estimated at the scale where it is used (province strata): the variance of the pooled
    log ratio, measured from its year-to-year spread (var of the yearly log ratios / number of years), divided by
    its Poisson variance. Median over strata with enough fire (A >= 50 in total). At least 1.

    (The first version used the NATIONAL ratio's year-to-year spread: with national counts the Poisson variance is
    tiny, so c came out ~23, every province got weight 0 and M2 collapsed to the regional value.)"""
    a = aj.groupby(ESTRATO + ["anio"])[["A", "V"]].sum().reset_index()
    a["l"], _ = _log_cociente(a.A, a.V)
    g = a.groupby(ESTRATO).agg(var_anios=("l", "var"), n_anios=("anio", "nunique"), A=("A", "sum"), V=("V", "sum"))
    g = g[g.A >= 50]
    _, v_pois = _log_cociente(g.A, g.V)
    return float(max(1.0, ((g.var_anios / g.n_anios) / v_pois).median()))


def _contraer(l, v, l_meta, ee_meta, grupo):
    """Shrink l (sampling variance v) toward l_meta (with its own error ee_meta). tau^2 (true variance between units
    around their target) by the DerSimonian-Laird estimator, one per `grupo` (day/night).

    (modelo.md proposed the plain method of moments, var(dev) - mean(v). It gave tau^2 = 0: mean(v) is dominated by
    a few almost empty strata - CABA, Tierra del Fuego at night - whose huge variances hide the real differences
    between provinces. DerSimonian-Laird weights each stratum by its precision.)"""
    d = pd.DataFrame({"dev": l - l_meta, "v": v, "g": grupo})

    def dl(x):
        w = 1 / x.v
        media = np.sum(w * x.dev) / np.sum(w)
        Q = np.sum(w * (x.dev - media) ** 2)
        return max(0.0, (Q - (len(x) - 1)) / (np.sum(w) - np.sum(w ** 2) / np.sum(w)))

    tau2 = d.groupby("g").apply(dl, include_groups=False)
    t = grupo.map(tau2)
    w = t / (t + v)
    lt = w * l + (1 - w) * l_meta
    ee = np.sqrt(w * v + (1 - w) ** 2 * ee_meta ** 2)
    return lt, ee, w, tau2


def ajustar_m012(aj: pd.DataFrame) -> dict:
    """Factors for M0, M1 and M2, one row per stratum (province x season x day/night)."""
    c = inflacion_c(aj)
    # national level, per season x day/night
    nac = aj.groupby(["estacion", "momento"])[["A", "V"]].sum().reset_index()
    nac["l_nac"], v = _log_cociente(nac.A, nac.V)
    nac["ee_nac"] = np.sqrt(c * v)
    # region level, shrunk toward the national value
    reg = aj.groupby(["region", "estacion", "momento"])[["A", "V"]].sum().reset_index()
    reg = reg.merge(nac[["estacion", "momento", "l_nac", "ee_nac"]], on=["estacion", "momento"])
    reg["l_reg_crudo"], v = _log_cociente(reg.A, reg.V)
    reg["v_reg"] = c * v
    reg["l_reg"], reg["ee_reg"], reg["w_reg"], _ = _contraer(reg.l_reg_crudo, reg.v_reg, reg.l_nac, reg.ee_nac, reg.momento)
    # province level (stratum), shrunk toward its region
    k = aj.groupby(["prov_cod", "provincia", "region", "estacion", "momento"])[["A", "V"]].sum().reset_index()
    k = k.merge(reg[["region", "estacion", "momento", "l_reg", "ee_reg", "l_reg_crudo"]],
                on=["region", "estacion", "momento"])
    k = k.merge(nac[["estacion", "momento", "l_nac"]], on=["estacion", "momento"])
    k["l1"], v = _log_cociente(k.A, k.V)
    k["v1"] = c * v
    k["l2"], k["ee2"], k["w"], tau2 = _contraer(k.l1, k.v1, k.l_reg, k.ee_reg, k.momento)
    l0, v0 = _log_cociente(aj.A.sum(), aj.V.sum())
    k["l0"], k["ee0"], k["ee1"] = l0, np.sqrt(c * v0), np.sqrt(k.v1)
    return {"estratos": k, "c": c, "tau2": tau2.to_dict(), "l0": l0}


def phi_momentos(A, mu) -> float:
    """Negative binomial dispersion (Var = mu + mu^2 / phi) by method of moments."""
    A, mu = np.asarray(A, float), np.asarray(mu, float)
    inv = np.sum((A - mu) ** 2 - mu) / np.sum(mu ** 2)
    return float(1 / inv) if inv > 1e-6 else 1e6


def ajustar_phi_curva(A, mu, momento) -> dict:
    """Dispersion that grows with the size of the month: phi = a * mu^b, per day/night.

    One phi for everything does not fit: on 2012-2022 the method-of-moments phi is ~3-4 for months with
    mu = 1-20 and ~60 for mu > 100 (daytime). A single pooled phi (54) made the 90 % intervals of mid-sized months
    far too narrow (coverage 71-76 %). The curve is fitted by least squares on log(phi) of mu bins (quantiles)."""
    d = pd.DataFrame({"A": np.asarray(A, float), "mu": np.asarray(mu, float), "m": np.asarray(momento)})
    d = d[d.mu > 0.5]
    curva = {}
    for m, g in d.groupby("m"):
        g = g.assign(b=pd.qcut(g.mu, 12, duplicates="drop"))
        pts = g.groupby("b", observed=True).apply(
            lambda x: pd.Series({"mu": x.mu.mean(), "phi": phi_momentos(x.A, x.mu)}), include_groups=False)
        pts = pts[(pts.phi > 0) & (pts.phi < 1e5)]
        b, loga = np.polyfit(np.log(pts.mu), np.log(pts.phi), 1)
        curva[m] = (float(np.exp(loga)), float(b))
    return curva


def phi_de(curva: dict, mu, momento):
    a = np.array([curva[m][0] for m in momento])
    b = np.array([curva[m][1] for m in momento])
    return a * np.maximum(np.asarray(mu, float), 0.5) ** b


def predecir_m012(fact: dict, filas: pd.DataFrame, modelo: str) -> pd.DataFrame:
    """Linear predictor log(mu) and its standard error for rows with V. `modelo` in M0, M1, M2."""
    col_l, col_ee = {"M0": ("l0", "ee0"), "M1": ("l1", "ee1"), "M2": ("l2", "ee2")}[modelo]
    k = fact["estratos"][ESTRATO + [col_l, col_ee]].rename(columns={col_l: "l", col_ee: "ee"})
    f = filas.merge(k, on=ESTRATO, how="left")
    assert f.l.notna().all(), "stratum without a factor"
    f["eta"] = f.l + np.log(np.maximum(f.V, 1e-9))
    f.loc[f.V == 0, "eta"] = -np.inf  # no VIIRS fire -> no Aqua fire expected (ratio model)
    f["ee_eta"] = f.ee
    return f


# --------------------------------------------------------------------------------------------- M3 (R)
R_M3 = r"""
suppressMessages(library(glmmTMB))
args <- commandArgs(trailingOnly = TRUE)
aj <- read.csv(args[1], colClasses = c(prov_cod = "character"))
nd <- read.csv(args[2], colClasses = c(prov_cod = "character"))
for (v in c("estacion", "momento", "region", "prov_cod")) {
  aj[[v]] <- factor(aj[[v]]); nd[[v]] <- factor(nd[[v]], levels = levels(aj[[v]]))
}
m <- glmmTMB(A ~ log(V + 0.5) + estacion * momento + (1 | region/prov_cod), family = nbinom2, data = aj)
p <- predict(m, newdata = nd, type = "link", se.fit = TRUE, allow.new.levels = TRUE)
nd$eta <- p$fit; nd$ee_eta <- p$se.fit
write.csv(nd, args[3], row.names = FALSE)
s <- summary(m)
info <- data.frame(
  converge = m$fit$convergence == 0 && isTRUE(m$sdr$pdHess),
  phi = sigma(m),
  beta_logV = fixef(m)$cond[["log(V + 0.5)"]],
  beta_logV_ee = s$coefficients$cond["log(V + 0.5)", "Std. Error"],
  sd_region = sqrt(VarCorr(m)$cond[["region"]][1]),
  sd_provincia = sqrt(VarCorr(m)$cond[["prov_cod:region"]][1]),
  aic = AIC(m))
write.csv(info, args[4], row.names = FALSE)
"""


def ajustar_predecir_m3(aj: pd.DataFrame, filas: pd.DataFrame, tmp: Path) -> tuple[pd.DataFrame, dict]:
    """Fit M3 in R on `aj` and predict the linear predictor (with se) for `filas` (needs V and the strata)."""
    tmp.mkdir(parents=True, exist_ok=True)
    rutas = {n: tmp / f"m3_{n}" for n in ("script.R", "aj.csv", "nd.csv", "pred.csv", "info.csv")}
    rutas["script.R"].write_text(R_M3, encoding="utf-8")
    cols = ["prov_cod", "region", "estacion", "momento", "V"]
    aj[cols + ["A"]].to_csv(rutas["aj.csv"], index=False)
    filas = filas.reset_index(drop=True).assign(fila=lambda d: d.index)
    filas[cols + ["fila"]].to_csv(rutas["nd.csv"], index=False)
    r = subprocess.run([str(RSCRIPT), str(rutas["script.R"]), str(rutas["aj.csv"]), str(rutas["nd.csv"]),
                        str(rutas["pred.csv"]), str(rutas["info.csv"])], capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"M3 failed in R:\n{r.stderr[-2000:]}")
    pred = pd.read_csv(rutas["pred.csv"])[["fila", "eta", "ee_eta"]]
    info = pd.read_csv(rutas["info.csv"]).iloc[0].to_dict()
    return filas.merge(pred, on="fila").drop(columns="fila"), info


# --------------------------------------------------------------------------------------------- simulation
def simular(eta, ee_eta, phi, grupo_factor, K=1000, semilla=2026):
    """K draws of Aqua-equivalent cell-days per row: the factor uncertainty (one draw per stratum and simulation,
    shared by all rows of that stratum) plus negative binomial sampling noise. Returns an array rows x K."""
    rng = np.random.default_rng(semilla)
    eta, ee_eta = np.asarray(eta, float), np.asarray(ee_eta, float)
    codigos, idx = np.unique(np.asarray(grupo_factor), return_inverse=True)
    z = rng.standard_normal((len(codigos), K))[idx]
    mu = np.exp(eta[:, None] + ee_eta[:, None] * z)
    mu[~np.isfinite(eta)] = 0.0
    phi = np.broadcast_to(np.asarray(phi, float).reshape(-1, 1) if np.ndim(phi) else phi, mu.shape)
    lam = rng.gamma(shape=phi, scale=np.where(mu > 0, mu / phi, 0.0))
    return rng.poisson(lam)
