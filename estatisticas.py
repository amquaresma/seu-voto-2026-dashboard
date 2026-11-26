"""
Etapa 2: estatística descritiva.

Calcula as medidas de cada pergunta respeitando o tipo de variável:
    quantitativa -> todas as medidas
    ordinal      -> medidas de posição (mediana, quartis, moda, amplitude)
    nominal      -> só moda e frequências

Cada medida traz: nome, grupo, fórmula (LaTeX), para que serve e o
"Como foi calculado" com os números reais da amostra.
"""
from collections import Counter

import numpy as np
import pandas as pd
from scipy import stats

import config as cfg

QUANT, ORD, NOM = "quantitativa", "ordinal", "nominal"


# ---------------------------------------------------------------------------
# Formatação no padrão brasileiro (vírgula decimal)
# ---------------------------------------------------------------------------
def fmt(x, casas: int = 2) -> str:
    if x is None or (isinstance(x, float) and np.isnan(x)):
        return "—"
    if isinstance(x, (int, np.integer)) or float(x).is_integer():
        return f"{int(round(float(x)))}"
    return f"{x:.{casas}f}".replace(".", ",")


def fmt_pct(p: float, casas: int = 1) -> str:
    return f"{p * 100:.{casas}f}%".replace(".", ",")


# ---------------------------------------------------------------------------
# Preparação da série
# ---------------------------------------------------------------------------
def tipo_de(chave: str) -> str:
    return cfg.POR_CHAVE[chave]["tipo"]


def serie_valida(df: pd.DataFrame, chave: str) -> pd.Series:
    """Respostas da pergunta, sem os vazios (quem não viu a pergunta)."""
    s = df[chave].dropna()
    if isinstance(s.dtype, pd.CategoricalDtype):
        s = s.cat.remove_unused_categories() if tipo_de(chave) == NOM else s
    return s


def _codigos(s: pd.Series) -> np.ndarray:
    """Posição de cada resposta ordinal na escala (0, 1, 2...)."""
    return s.cat.codes.to_numpy()


def _categoria(s: pd.Series, codigo: float) -> str:
    return str(s.cat.categories[int(codigo)])


# ---------------------------------------------------------------------------
# Medidas para variáveis quantitativas
# ---------------------------------------------------------------------------
def _q_media(x):
    soma, n = x.sum(), len(x)
    return dict(valor=x.mean(),
                passos=f"x̄ = Σx / n = {fmt(soma)} / {n} = **{fmt(x.mean())}**")


def _q_mediana(x):
    xs = np.sort(x)
    n = len(xs)
    med = np.median(xs)
    if n % 2:
        pos = (f"n = {n} é ímpar, então a mediana é o valor na posição (n + 1) / 2 = "
               f"{(n + 1) // 2}, que vale **{fmt(med)}**")
    else:
        a, b = xs[n // 2 - 1], xs[n // 2]
        pos = (f"n = {n} é par, então a mediana é a média das posições {n // 2} e {n // 2 + 1}: "
               f"({fmt(a)} + {fmt(b)}) / 2 = **{fmt(med)}**")
    return dict(valor=med, passos=f"Valores em ordem crescente. {pos}.")


def _moda_generica(valores, rotulo=fmt):
    cont = Counter(valores)
    maior = max(cont.values())
    modas = [v for v, c in cont.items() if c == maior]
    if len(modas) == len(cont) and len(cont) > 1:
        return dict(valor=None, texto="Amodal",
                    passos="Todas as respostas aparecem o mesmo número de vezes: não há moda.")
    texto = " e ".join(rotulo(m) for m in sorted(modas, key=str))
    tipo = "unimodal" if len(modas) == 1 else ("bimodal" if len(modas) == 2 else "multimodal")
    return dict(valor=modas[0] if len(modas) == 1 else None, texto=texto,
                passos=f"Resposta mais frequente: **{texto}**, com {maior} ocorrência(s) ({tipo}).")


def _q_moda(x):
    return _moda_generica(x.tolist())


def _q_media_aparada(x, prop=0.10):
    k = int(len(x) * prop)
    v = stats.trim_mean(x, prop)
    return dict(valor=v, passos=(
        f"Remove {int(prop * 100)}% dos valores de cada ponta ({k} menores e {k} maiores) "
        f"e calcula a média dos {len(x) - 2 * k} restantes = **{fmt(v)}**. "
        "Ela é menos afetada por valores extremos do que a média comum."))


def _q_amplitude(x):
    return dict(valor=x.max() - x.min(),
                passos=f"A = máx − mín = {fmt(x.max())} − {fmt(x.min())} = **{fmt(x.max() - x.min())}**")


def _q_variancia(x):
    m, n = x.mean(), len(x)
    sq = ((x - m) ** 2).sum()
    v = x.var(ddof=1)
    return dict(valor=v, passos=(
        f"Soma dos quadrados dos desvios: Σ(x − x̄)² = {fmt(sq)}. "
        f"Divide por n − 1 = {n - 1} (variância amostral): s² = {fmt(sq)} / {n - 1} = **{fmt(v)}**"))


def _q_desvio(x):
    v = x.var(ddof=1)
    s = x.std(ddof=1)
    return dict(valor=s, passos=(
        f"s = √s² = √{fmt(v)} = **{fmt(s)}**. Em média, as respostas ficam a cerca de "
        f"{fmt(s)} ponto(s) da média ({fmt(x.mean())})."))


def _q_cv(x):
    m, s = x.mean(), x.std(ddof=1)
    if m == 0:
        return dict(valor=np.nan, passos="A média é zero, então o CV não pode ser calculado.")
    cv = s / abs(m)
    nivel = "baixa" if cv < 0.15 else ("moderada" if cv < 0.30 else "alta")
    return dict(valor=cv, texto=fmt_pct(cv), passos=(
        f"CV = s / x̄ = {fmt(s)} / {fmt(m)} = **{fmt_pct(cv)}**: dispersão {nivel} "
        "(referência usual: até 15% baixa, 15% a 30% moderada, acima de 30% alta)."))


def _q_quartis(x):
    q1, q2, q3 = np.percentile(x, [25, 50, 75])
    return dict(valor=(q1, q2, q3), texto=f"Q1 = {fmt(q1)} · Q2 = {fmt(q2)} · Q3 = {fmt(q3)}",
                passos=(f"25% das respostas ficam até **{fmt(q1)}**, 50% até **{fmt(q2)}** "
                        f"e 75% até **{fmt(q3)}** (interpolação linear)."))


def _q_iqr(x):
    q1, q3 = np.percentile(x, [25, 75])
    return dict(valor=q3 - q1, passos=(
        f"IQR = Q3 − Q1 = {fmt(q3)} − {fmt(q1)} = **{fmt(q3 - q1)}**. "
        "É a largura da faixa onde estão os 50% de respostas do meio."))


def _q_dma(x):
    m = x.mean()
    d = np.abs(x - m).mean()
    return dict(valor=d, passos=(
        f"DMA = Σ|x − x̄| / n = {fmt(np.abs(x - m).sum())} / {len(x)} = **{fmt(d)}**"))


def _q_percentis(x):
    ps = [10, 25, 50, 75, 90]
    vals = np.percentile(x, ps)
    texto = " · ".join(f"P{p} = {fmt(v)}" for p, v in zip(ps, vals))
    return dict(valor=dict(zip(ps, vals)), texto=texto,
                passos=f"P10 = {fmt(vals[0])} significa que 10% das respostas ficam até esse valor. {texto}")


def _q_escore_z(x):
    m, s = x.mean(), x.std(ddof=1)
    if s == 0:
        return dict(valor=None, texto="—", passos="Desvio padrão zero: todos responderam igual.")
    zmin, zmax = (x.min() - m) / s, (x.max() - m) / s
    return dict(valor=(zmin, zmax), texto=f"mín: z = {fmt(zmin)} · máx: z = {fmt(zmax)}",
                passos=(f"z = (x − x̄) / s. Para o menor valor ({fmt(x.min())}): "
                        f"({fmt(x.min())} − {fmt(m)}) / {fmt(s)} = **{fmt(zmin)}**. "
                        f"Para o maior ({fmt(x.max())}): **{fmt(zmax)}**. "
                        "|z| acima de 2 indica um valor incomum."))


def _q_assimetria(x):
    if len(x) < 3 or x.std() == 0:
        return dict(valor=np.nan, passos="Precisa de pelo menos 3 respostas diferentes.")
    g = stats.skew(x, bias=False)
    if abs(g) < 0.5:
        leitura = "distribuição aproximadamente simétrica"
    elif g < 0:
        leitura = "assimetria negativa: as respostas se concentram nos valores altos, com cauda à esquerda"
    else:
        leitura = "assimetria positiva: as respostas se concentram nos valores baixos, com cauda à direita"
    return dict(valor=g, passos=f"Coeficiente de assimetria (Fisher) = **{fmt(g)}**: {leitura}.")


def _q_curtose(x):
    if len(x) < 4 or x.std() == 0:
        return dict(valor=np.nan, passos="Precisa de pelo menos 4 respostas diferentes.")
    k = stats.kurtosis(x, bias=False)
    leitura = ("leptocúrtica: mais concentrada no centro e com caudas pesadas" if k > 0.5 else
               "platicúrtica: mais achatada que a normal" if k < -0.5 else
               "mesocúrtica: parecida com a curva normal")
    return dict(valor=k, passos=f"Curtose em excesso = **{fmt(k)}** (normal = 0): {leitura}.")


def _q_outliers(x):
    q1, q3 = np.percentile(x, [25, 75])
    iqr = q3 - q1
    li, ls = q1 - 1.5 * iqr, q3 + 1.5 * iqr
    fora = np.sort(x[(x < li) | (x > ls)])
    texto = f"{len(fora)} valor(es)" if len(fora) else "Nenhum"
    lista = f" Valores: {', '.join(fmt(v) for v in fora)}." if len(fora) else ""
    return dict(valor=len(fora), texto=texto, passos=(
        f"Limites: Q1 − 1,5·IQR = {fmt(q1)} − 1,5·{fmt(iqr)} = {fmt(li)} e "
        f"Q3 + 1,5·IQR = {fmt(q3)} + 1,5·{fmt(iqr)} = {fmt(ls)}. "
        f"Fora desses limites: **{texto}**.{lista}"))


# ---------------------------------------------------------------------------
# Medidas para variáveis ordinais (usam a posição na escala)
# ---------------------------------------------------------------------------
def _o_mediana(s):
    c = np.sort(_codigos(s))
    n = len(c)
    if n % 2:
        cat = _categoria(s, c[n // 2])
        return dict(valor=cat, texto=cat, passos=(
            f"Respostas ordenadas na escala. n = {n} é ímpar: a mediana é a resposta "
            f"na posição {(n + 1) // 2}, que é **{cat}**."))
    a, b = _categoria(s, c[n // 2 - 1]), _categoria(s, c[n // 2])
    texto = a if a == b else f"entre {a} e {b}"
    return dict(valor=texto, texto=texto, passos=(
        f"Respostas ordenadas na escala. n = {n} é par: as posições do meio são "
        f"{n // 2} ({a}) e {n // 2 + 1} ({b}). Mediana: **{texto}**."))


def _o_moda(s):
    return _moda_generica(s.astype(str).tolist(), rotulo=str)


def _o_quartis(s):
    c = _codigos(s)
    q = [_categoria(s, np.quantile(c, p, method="inverted_cdf")) for p in (0.25, 0.5, 0.75)]
    texto = f"Q1: {q[0]} · Q2: {q[1]} · Q3: {q[2]}"
    return dict(valor=q, texto=texto, passos=(
        f"Posição na escala acumulada: 25% das respostas vão até **{q[0]}**, "
        f"50% até **{q[1]}** e 75% até **{q[2]}**."))


def _o_percentis(s):
    c = _codigos(s)
    ps = [10, 25, 50, 75, 90]
    vals = [_categoria(s, np.quantile(c, p / 100, method="inverted_cdf")) for p in ps]
    texto = " · ".join(f"P{p}: {v}" for p, v in zip(ps, vals))
    return dict(valor=dict(zip(ps, vals)), texto=texto,
                passos=f"Categoria em que a frequência acumulada atinge cada percentil. {texto}")


def _o_amplitude(s):
    c = _codigos(s)
    a, b = _categoria(s, c.min()), _categoria(s, c.max())
    return dict(valor=(a, b), texto=f"de {a} a {b}", passos=(
        f"Em variável ordinal, a amplitude é o intervalo entre a menor e a maior "
        f"categoria respondida: **de {a} a {b}**. Não dá para subtrair categorias."))


# ---------------------------------------------------------------------------
# Catálogo de medidas
# ---------------------------------------------------------------------------
MEDIDAS = {
    "media": dict(nome="Média", grupo="Tendência central",
                  formula=r"\bar{x} = \frac{\sum x_i}{n}", funcoes={QUANT: _q_media}),
    "mediana": dict(nome="Mediana", grupo="Tendência central",
                    formula=r"Md = x_{\left(\frac{n+1}{2}\right)}",
                    funcoes={QUANT: _q_mediana, ORD: _o_mediana}),
    "moda": dict(nome="Moda", grupo="Tendência central", formula=r"Mo = \text{valor mais frequente}",
                 funcoes={QUANT: _q_moda, ORD: _o_moda, NOM: _o_moda}),
    "media_aparada": dict(nome="Média aparada (10%)", grupo="Tendência central",
                          formula=r"\bar{x}_{10\%} = \text{média sem os 10\% extremos de cada lado}",
                          funcoes={QUANT: _q_media_aparada}),
    "amplitude": dict(nome="Amplitude", grupo="Dispersão", formula=r"A = x_{máx} - x_{mín}",
                      funcoes={QUANT: _q_amplitude, ORD: _o_amplitude}),
    "variancia": dict(nome="Variância", grupo="Dispersão",
                      formula=r"s^2 = \frac{\sum (x_i - \bar{x})^2}{n - 1}", funcoes={QUANT: _q_variancia}),
    "desvio_padrao": dict(nome="Desvio padrão", grupo="Dispersão", formula=r"s = \sqrt{s^2}",
                          funcoes={QUANT: _q_desvio}),
    "cv": dict(nome="Coeficiente de variação", grupo="Dispersão",
               formula=r"CV = \frac{s}{\bar{x}} \times 100\%", funcoes={QUANT: _q_cv}),
    "iqr": dict(nome="Amplitude interquartil (IQR)", grupo="Dispersão", formula=r"IQR = Q_3 - Q_1",
                funcoes={QUANT: _q_iqr}),
    "dma": dict(nome="Desvio médio absoluto", grupo="Dispersão",
                formula=r"DMA = \frac{\sum |x_i - \bar{x}|}{n}", funcoes={QUANT: _q_dma}),
    "quartis": dict(nome="Quartis", grupo="Posição", formula=r"Q_k = P_{25k}",
                    funcoes={QUANT: _q_quartis, ORD: _o_quartis}),
    "percentis": dict(nome="Percentis", grupo="Posição",
                      formula=r"P_k = \text{valor abaixo do qual estão } k\% \text{ dos dados}",
                      funcoes={QUANT: _q_percentis, ORD: _o_percentis}),
    "escore_z": dict(nome="Escore-z", grupo="Posição", formula=r"z = \frac{x - \bar{x}}{s}",
                     funcoes={QUANT: _q_escore_z}),
    "assimetria": dict(nome="Assimetria", grupo="Forma",
                       formula=r"g_1 = \frac{n}{(n-1)(n-2)} \sum \left(\frac{x_i - \bar{x}}{s}\right)^3",
                       funcoes={QUANT: _q_assimetria}),
    "curtose": dict(nome="Curtose", grupo="Forma",
                    formula=r"g_2 = \frac{n(n+1)}{(n-1)(n-2)(n-3)} \sum \left(\frac{x_i - \bar{x}}{s}\right)^4 - \frac{3(n-1)^2}{(n-2)(n-3)}",
                    funcoes={QUANT: _q_curtose}),
    "outliers": dict(nome="Outliers (regra do IQR)", grupo="Outliers",
                     formula=r"x < Q_1 - 1{,}5\,IQR \;\;\text{ou}\;\; x > Q_3 + 1{,}5\,IQR",
                     funcoes={QUANT: _q_outliers}),
}
GRUPOS = ["Tendência central", "Dispersão", "Posição", "Forma", "Outliers"]

MOTIVO_BLOQUEIO = {
    ORD: ("Variável **ordinal**: as categorias têm ordem, mas a distância entre elas não é "
          "numérica (de \"Nada\" para \"Menos de 30 min\" não é o mesmo salto que de "
          "\"30 min a 2 h\" para \"Mais de 2 h\"). Por isso não se calcula {medida}. "
          "Use mediana, quartis ou moda."),
    NOM: ("Variável **nominal**: as categorias não têm ordem nem valor numérico "
          "(não existe \"média\" entre Instagram e TV). Por isso não se calcula {medida}. "
          "Use a moda e a tabela de frequências."),
}


def medida_valida(medida: str, tipo: str) -> bool:
    return tipo in MEDIDAS[medida]["funcoes"]


def motivo_bloqueio(medida: str, tipo: str) -> str:
    return MOTIVO_BLOQUEIO[tipo].format(medida=MEDIDAS[medida]["nome"].lower())


def calcular(serie: pd.Series, medida: str, tipo: str) -> dict:
    """Devolve {valor, texto, passos}. Levanta ValueError se a medida não vale para o tipo."""
    if not medida_valida(medida, tipo):
        raise ValueError(motivo_bloqueio(medida, tipo))
    dados = serie.to_numpy(dtype=float) if tipo == QUANT else serie
    r = MEDIDAS[medida]["funcoes"][tipo](dados)
    if "texto" not in r:
        r["texto"] = r["valor"] if isinstance(r["valor"], str) else fmt(r["valor"])
    return r


# ---------------------------------------------------------------------------
# Tabelas
# ---------------------------------------------------------------------------
def tabela_frequencias(serie: pd.Series, tipo: str) -> pd.DataFrame:
    """Frequência absoluta, relativa e (se houver ordem) acumulada."""
    if tipo == QUANT:
        cont = serie.value_counts().sort_index()
        cont.index = [fmt(v) for v in cont.index]
    else:
        cont = serie.value_counts(sort=False)
        if tipo == NOM:
            cont = cont.sort_values(ascending=False)
    n = cont.sum()
    tab = pd.DataFrame({"Resposta": cont.index.astype(str), "Frequência (fi)": cont.values})
    tab["Relativa (fr)"] = tab["Frequência (fi)"] / n
    if tipo in (QUANT, ORD):
        tab["Acumulada (Fi)"] = tab["Frequência (fi)"].cumsum()
        tab["Relativa acumulada (Fr)"] = tab["Relativa (fr)"].cumsum()
    return tab


def resumo(serie: pd.Series, tipo: str, medidas: list[str]) -> pd.DataFrame:
    """Tabela Medida | Valor, só com as medidas válidas para o tipo."""
    linhas = [("n (respostas)", str(len(serie)))]
    for m in medidas:
        if medida_valida(m, tipo):
            linhas.append((MEDIDAS[m]["nome"], calcular(serie, m, tipo)["texto"]))
    return pd.DataFrame(linhas, columns=["Medida", "Valor"])


def por_grupo(df: pd.DataFrame, chave: str, grupo: str, medidas: list[str]) -> pd.DataFrame:
    """
    Uma linha por grupo (ex.: faixa etária), com n e as medidas escolhidas.
    Grupos com menos de cfg.N_MINIMO respostas ficam ocultos.
    """
    tipo = tipo_de(chave)
    validas = [m for m in medidas if medida_valida(m, tipo)]
    linhas = []
    for nome, sub in df.groupby(grupo, observed=True):
        s = serie_valida(sub, chave)
        linha = {"Grupo": str(nome), "n": len(s)}
        for m in validas:
            linha[MEDIDAS[m]["nome"]] = (calcular(s, m, tipo)["texto"]
                                         if len(s) >= cfg.N_MINIMO else f"oculto (n < {cfg.N_MINIMO})")
        linhas.append(linha)
    return pd.DataFrame(linhas)


def tabela_cruzada(df: pd.DataFrame, chave: str, grupo: str) -> pd.DataFrame:
    """Percentual de cada resposta dentro de cada grupo (cada linha soma 100%)."""
    sub = df[[chave, grupo]].dropna()
    return pd.crosstab(sub[grupo], sub[chave], normalize="index")
