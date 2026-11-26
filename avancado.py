"""
Análises além da estatística descritiva (bônus).

Os testes abaixo supõem amostra aleatória. Como esta amostra é por conveniência,
os resultados servem como indício, nunca como prova sobre o eleitorado.
"""
import numpy as np
import pandas as pd
from scipy import stats

import config as cfg
import estatisticas as est

# Variáveis com ordem que entram na correlação (categorias viram posições 0, 1, 2...)
CORRELACAO = {
    "autoav_pre": "Nota do voto (início)",
    "autoav_pos": "Nota do voto (fim)",
    "indice_memoria": "Memória do voto",
    "tempo_candidato": "Pesquisa sobre o candidato",
    "tempo_celular": "Pesquisa antes de um celular",
    "quando_decidiu": "Quão tarde decidiu",
    "impacto_vida": "Política afeta a vida",
    "escolaridade": "Escolaridade",
    "faixa_etaria": "Faixa etária",
}


def _numerica(df: pd.DataFrame, chave: str) -> pd.Series:
    s = df[chave]
    if isinstance(s.dtype, pd.CategoricalDtype):
        return s.cat.codes.replace(-1, np.nan).astype(float)
    return pd.to_numeric(s, errors="coerce")


def leitura_p(p: float) -> str:
    if p < 0.01:
        return "muito pouco provável de ser acaso (p < 0,01)"
    if p < 0.05:
        return f"pouco provável de ser acaso (p = {est.fmt(p, 3)})"
    return f"pode ser fruto do acaso (p = {est.fmt(p, 2)})"


# ---------------------------------------------------------------------------
# Antes x depois
# ---------------------------------------------------------------------------
def antes_depois(df: pd.DataFrame) -> dict:
    sub = df[["autoav_pre", "autoav_pos"]].dropna()
    pre, pos = sub["autoav_pre"], sub["autoav_pos"]
    dif = pos - pre
    r = dict(n=len(sub), media_pre=pre.mean(), media_pos=pos.mean(),
             mediana_pre=pre.median(), mediana_pos=pos.median(),
             baixou=int((dif < 0).sum()), manteve=int((dif == 0).sum()), subiu=int((dif > 0).sum()),
             transicoes=pd.crosstab(pre.astype(int), pos.astype(int)))
    if (dif != 0).sum() >= 6:
        w = stats.wilcoxon(pos, pre, zero_method="wilcox")
        r.update(estatistica=float(w.statistic), p=float(w.pvalue))
    return r


# ---------------------------------------------------------------------------
# Associação entre duas perguntas de categoria
# ---------------------------------------------------------------------------
def associacao(df: pd.DataFrame, linha: str, coluna: str) -> dict:
    sub = df[[linha, coluna]].dropna()
    cont = pd.crosstab(sub[linha], sub[coluna])
    cont = cont.loc[cont.sum(axis=1) > 0, cont.sum(axis=0) > 0]
    r = dict(n=int(cont.to_numpy().sum()), contagem=cont,
             percentual=cont.div(cont.sum(axis=1), axis=0))
    if min(cont.shape) < 2:
        return r
    chi2, p, gl, esperado = stats.chi2_contingency(cont)
    v = np.sqrt(chi2 / (r["n"] * (min(cont.shape) - 1)))
    forca = "desprezível" if v < 0.1 else "fraca" if v < 0.3 else "moderada" if v < 0.5 else "forte"
    r.update(chi2=chi2, p=p, gl=gl, v=v, forca=forca,
             esperado_baixo=float((esperado < 5).mean()))
    return r


# ---------------------------------------------------------------------------
# Correlação de Spearman
# ---------------------------------------------------------------------------
def correlacao(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Devolve (matriz de rho, matriz de n por par)."""
    num = pd.DataFrame({rot: _numerica(df, k) for k, rot in CORRELACAO.items()})
    rho = num.corr(method="spearman", min_periods=cfg.N_MINIMO * 2)
    n = num.notna().astype(int).T @ num.notna().astype(int)
    return rho, n


def correlacoes_fortes(rho: pd.DataFrame, limite: float = 0.3) -> list[tuple[str, str, float]]:
    pares = []
    cols = list(rho.columns)
    for i, a in enumerate(cols):
        for b in cols[i + 1:]:
            v = rho.loc[a, b]
            if pd.notna(v) and abs(v) >= limite:
                pares.append((a, b, float(v)))
    return sorted(pares, key=lambda x: abs(x[2]), reverse=True)
