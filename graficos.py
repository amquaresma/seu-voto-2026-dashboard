"""
Etapa 2: gráficos (Plotly).

    distribuicao(...)  -> barras de frequência, com as medidas desenhadas por cima
    boxplot(...)       -> caixa com quartis, mediana, média e outliers
    comparacao(...)    -> a mesma pergunta comparada entre grupos

Cores: paleta validada para daltonismo (ordem fixa, nunca reciclada).
"""
import numpy as np
import pandas as pd
import plotly.graph_objects as go

import config as cfg
import estatisticas as est

# Paleta categórica (ordem fixa) e rampas ordinais de um só tom (azul)
CATEGORICA = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100",
              "#e87ba4", "#008300", "#6250d6", "#e34948"]
RAMPA = {
    2: ["#86b6ef", "#1c5cab"],
    3: ["#86b6ef", "#2a78d6", "#104281"],
    4: ["#86b6ef", "#3987e5", "#1c5cab", "#0d366b"],
    5: ["#86b6ef", "#5598e7", "#2a78d6", "#1c5cab", "#0d366b"],
}
TINTA_ESCURA = "#0b0b0b"     # texto sobre cores claras
COR_BARRA = CATEGORICA[0]    # uma série = uma cor
COR_MEDIA = CATEGORICA[1]    # laranja
COR_MEDIANA = CATEGORICA[2]  # verde-água
COR_MODA = CATEGORICA[6]     # violeta
COR_FAIXA = "rgba(42,120,214,0.12)"
GRADE = "rgba(137,135,129,0.25)"
FONTE = 'system-ui, -apple-system, "Segoe UI", sans-serif'


def _layout(fig: go.Figure, titulo: str = "", altura: int = 400) -> go.Figure:
    fig.update_layout(
        title=dict(text=titulo, x=0, xanchor="left", font=dict(size=16)),
        height=altura,
        margin=dict(l=10, r=20, t=60 if titulo else 20, b=10),
        font=dict(family=FONTE, size=13),
        bargap=0.3,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0, title=None),
        hoverlabel=dict(font_family=FONTE),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    fig.update_xaxes(showgrid=False, linecolor=GRADE, zeroline=False)
    fig.update_yaxes(gridcolor=GRADE, zeroline=False)
    return fig


def _linha_vertical(fig, x, nome, cor, traco, y_rotulo):
    """Linha de referência com rótulo e entrada na legenda."""
    fig.add_vline(x=x, line=dict(color=cor, width=2, dash=traco))
    fig.add_annotation(x=x, y=y_rotulo, yref="paper", text=f"{nome}: {est.fmt(x)}",
                       showarrow=False, xanchor="left", xshift=4, font=dict(size=12),
                       bgcolor="rgba(127,127,127,0.12)")
    fig.add_trace(go.Scatter(x=[None], y=[None], mode="lines", name=nome,
                             line=dict(color=cor, width=2, dash=traco)))


# ---------------------------------------------------------------------------
# Distribuição de uma pergunta
# ---------------------------------------------------------------------------
def distribuicao(serie: pd.Series, tipo: str, medidas: list[str], titulo: str = "") -> go.Figure:
    tab = est.tabela_frequencias(serie, tipo)
    if tipo == est.QUANT:
        return _distribuicao_quantitativa(serie, tab, medidas, titulo)
    return _distribuicao_categorica(serie, tipo, tab, medidas, titulo)


def _distribuicao_quantitativa(serie, tab, medidas, titulo):
    x = serie.to_numpy(dtype=float)
    cont = pd.Series(x).value_counts().sort_index()
    n = len(x)
    fig = go.Figure(go.Bar(
        x=cont.index, y=cont.values, marker_color=COR_BARRA, name="Respostas",
        customdata=cont.values / n,
        hovertemplate="Valor %{x}<br>%{y} pessoa(s) · %{customdata:.1%}<extra></extra>",
        showlegend=False,
    ))

    m, s = x.mean(), x.std(ddof=1)
    if "desvio_padrao" in medidas:
        fig.add_vrect(x0=m - s, x1=m + s, fillcolor=COR_FAIXA, line_width=0, layer="below")
        fig.add_annotation(x=m - s, y=0.98, yref="paper", text="±1 desvio padrão",
                           showarrow=False, xanchor="left", xshift=4, font=dict(size=11))
    if "quartis" in medidas or "iqr" in medidas:
        q1, q3 = np.percentile(x, [25, 75])
        for q, nome in ((q1, "Q1"), (q3, "Q3")):
            fig.add_vline(x=q, line=dict(color="#898781", width=1, dash="dot"))
            fig.add_annotation(x=q, y=0.05, yref="paper", text=nome, showarrow=False,
                               xanchor="left", xshift=3, font=dict(size=11))
    if "media" in medidas:
        _linha_vertical(fig, m, "Média", COR_MEDIA, "solid", 0.90)
    if "mediana" in medidas:
        _linha_vertical(fig, float(np.median(x)), "Mediana", COR_MEDIANA, "dash", 0.80)
    if "moda" in medidas:
        r = est.calcular(serie, "moda", est.QUANT)
        if r["valor"] is not None:
            _linha_vertical(fig, float(r["valor"]), "Moda", COR_MODA, "dot", 0.70)

    fig.update_xaxes(title="Resposta", dtick=1)
    fig.update_yaxes(title="Pessoas")
    return _layout(fig, titulo)


def _distribuicao_categorica(serie, tipo, tab, medidas, titulo):
    horizontal = tipo == est.NOM
    rotulos = tab["Resposta"].tolist()
    textos = [f"{fi} · {est.fmt_pct(fr)}" for fi, fr in zip(tab["Frequência (fi)"], tab["Relativa (fr)"])]

    if horizontal and "moda" in medidas:
        moda = est.calcular(serie, "moda", tipo)["texto"]
        textos = [t + "  ← moda" if r == moda else t for r, t in zip(rotulos, textos)]

    if horizontal:   # nominal: barras deitadas, maior em cima
        barra = go.Bar(y=rotulos[::-1], x=tab["Frequência (fi)"][::-1], orientation="h",
                       text=textos[::-1], textposition="outside", cliponaxis=False,
                       marker_color=COR_BARRA, hovertemplate="%{y}<br>%{x} pessoa(s)<extra></extra>")
    else:            # ordinal: colunas na ordem da escala
        barra = go.Bar(x=rotulos, y=tab["Frequência (fi)"], text=textos, textposition="outside",
                       cliponaxis=False, marker_color=COR_BARRA,
                       hovertemplate="%{x}<br>%{y} pessoa(s)<extra></extra>")
    fig = go.Figure(barra)
    fig.update_traces(showlegend=False)

    # Marca a moda e, se for ordinal, a mediana
    marcas = []
    if "moda" in medidas and not horizontal:
        marcas.append(("Moda", est.calcular(serie, "moda", tipo)["texto"]))
    if tipo == est.ORD and "mediana" in medidas:
        marcas.append(("Mediana", est.calcular(serie, "mediana", tipo)["texto"]))
    for i, (nome, cat) in enumerate(marcas):
        if cat not in rotulos:      # ex.: mediana "entre A e B" ou moda múltipla
            continue
        fig.add_annotation(x=cat, y=1.0 + 0.07 * i, yref="paper", text=f"▼ {nome}",
                           showarrow=False, font=dict(size=12))

    if horizontal:
        maior = tab["Frequência (fi)"].max()
        fig.update_xaxes(title="Pessoas", showgrid=True, gridcolor=GRADE, range=[0, maior * 1.35])
        fig.update_yaxes(title=None, showgrid=False)
        altura = max(300, 60 + 42 * len(rotulos))
    else:
        maior = tab["Frequência (fi)"].max()
        fig.update_yaxes(title="Pessoas", range=[0, maior * 1.2])
        fig.update_xaxes(title=None)
        altura = 420
    return _layout(fig, titulo, altura)


# ---------------------------------------------------------------------------
# Boxplot (só quantitativas)
# ---------------------------------------------------------------------------
def boxplot(serie: pd.Series, titulo: str = "") -> go.Figure:
    x = serie.to_numpy(dtype=float)
    fig = go.Figure(go.Box(
        x=x, name="", boxpoints="outliers", boxmean=True, marker_color=COR_BARRA,
        line=dict(width=1.5), fillcolor="rgba(42,120,214,0.18)",
        hovertemplate="%{x}<extra></extra>",
    ))
    fig.update_xaxes(title="Resposta", dtick=1, showgrid=True, gridcolor=GRADE)
    fig.update_yaxes(showticklabels=False, showgrid=False)
    fig.add_annotation(text="Linha cheia = mediana · tracejada = média · pontos = outliers",
                       x=0, y=-0.35, xref="paper", yref="paper", showarrow=False,
                       xanchor="left", font=dict(size=11, color="#898781"))
    fig = _layout(fig, titulo, altura=220)
    fig.update_layout(margin=dict(b=50))
    return fig


# ---------------------------------------------------------------------------
# Comparação entre grupos
# ---------------------------------------------------------------------------
def _grupos_validos(df, chave, grupo):
    sub = df[[chave, grupo]].dropna()
    n = sub[grupo].value_counts()
    validos = [g for g in sub[grupo].cat.categories if n.get(g, 0) >= cfg.N_MINIMO] \
        if isinstance(sub[grupo].dtype, pd.CategoricalDtype) else \
        [g for g in sorted(n.index) if n[g] >= cfg.N_MINIMO]
    ocultos = [str(g) for g in n.index if n[g] < cfg.N_MINIMO and n[g] > 0]
    return sub[sub[grupo].isin(validos)], validos, ocultos, n


def comparacao(df: pd.DataFrame, chave: str, grupo: str, titulo: str = "") -> tuple[go.Figure, list]:
    """Devolve (figura, grupos ocultos por terem n < N_MINIMO)."""
    if chave == grupo:
        raise ValueError("A pergunta e o grupo de comparação precisam ser diferentes.")
    tipo = est.tipo_de(chave)
    sub, validos, ocultos, n = _grupos_validos(df, chave, grupo)
    nomes = [f"{g} (n={n[g]})" for g in validos]

    if tipo == est.QUANT:
        fig = go.Figure()
        for g, nome in zip(validos, nomes):
            fig.add_trace(go.Box(x=sub.loc[sub[grupo] == g, chave], name=nome, boxmean=True,
                                 marker_color=COR_BARRA, fillcolor="rgba(42,120,214,0.18)",
                                 line=dict(width=1.5), boxpoints="outliers", showlegend=False))
        fig.update_xaxes(title=cfg.POR_CHAVE[chave]["curto"], dtick=1, showgrid=True, gridcolor=GRADE)
        fig.update_yaxes(autorange="reversed", showgrid=False)
        return _layout(fig, titulo, altura=140 + 70 * len(validos)), ocultos

    # Categóricas: barras 100% empilhadas (cada grupo soma 100%)
    tab = pd.crosstab(sub[grupo], sub[chave], normalize="index")
    tab = tab.loc[[g for g in validos if g in tab.index]]
    opcoes = list(cfg.POR_CHAVE[chave]["opcoes"])
    if tipo == est.ORD and len(opcoes) in RAMPA:
        cores = RAMPA[len(opcoes)]
        claras = {0, 1} if len(opcoes) >= 4 else {0}
    else:
        cores = CATEGORICA
        claras = {3}                                  # amarelo pede texto escuro
    fig = go.Figure()
    for c in [c for c in opcoes if c in tab.columns and tab[c].sum() > 0]:
        i = opcoes.index(c)                           # cor fixa por categoria
        vals = tab[c].to_numpy()
        fig.add_trace(go.Bar(
            y=nomes, x=vals, name=str(c), orientation="h", marker_color=cores[i % len(cores)],
            marker_line=dict(width=1, color="rgba(255,255,255,0.9)"),
            text=[est.fmt_pct(v, 0) if v >= 0.08 else "" for v in vals],
            textposition="inside", insidetextanchor="middle",
            textfont=dict(color=TINTA_ESCURA if i in claras else "#ffffff", size=12),
            hovertemplate=f"<b>{c}</b><br>%{{y}}: %{{x:.1%}}<extra></extra>",
        ))
    fig.update_layout(barmode="stack")
    fig.update_xaxes(tickformat=".0%", range=[0, 1], showgrid=False)
    fig.update_yaxes(autorange="reversed")
    fig = _layout(fig, titulo, altura=180 + 55 * len(validos))
    fig.update_layout(legend=dict(traceorder="normal"), bargap=0.35)
    return fig, ocultos
