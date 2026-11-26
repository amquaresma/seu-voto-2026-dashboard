"""
Gráficos (Plotly), com cores para o tema claro e para o escuro.

Paleta validada para daltonismo. Regras usadas em todo o site:
  - uma série = uma cor (azul);
  - categorias com ordem = um único tom, do mais fraco ao mais forte;
  - categorias sem ordem = cores fixas por categoria (nunca mudam com o filtro);
  - todo gráfico tem o número escrito ou disponível ao passar o mouse.
"""
import numpy as np
import pandas as pd
import plotly.graph_objects as go

import config as cfg
import estatisticas as est

PALETAS = {
    "light": dict(
        cat=["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#6250d6", "#e34948"],
        rampa={2: ["#86b6ef", "#1c5cab"], 3: ["#86b6ef", "#2a78d6", "#104281"],
               4: ["#86b6ef", "#3987e5", "#1c5cab", "#0d366b"],
               5: ["#86b6ef", "#5598e7", "#2a78d6", "#1c5cab", "#0d366b"]},
        claras_rampa=lambda n: {0, 1} if n >= 4 else {0},
        faixa="rgba(42,120,214,0.12)", preenchimento="rgba(42,120,214,0.18)",
        escala=[[0, "#f0efec"], [1, "#1c5cab"]],
        divergente=[[0, "#e34948"], [0.5, "#f0efec"], [1, "#2a78d6"]],
    ),
    "dark": dict(
        cat=["#3987e5", "#d95926", "#199e70", "#c98500", "#d55181", "#008300", "#9085e9", "#e66767"],
        rampa={2: ["#184f95", "#86b6ef"], 3: ["#184f95", "#3987e5", "#9ec5f4"],
               4: ["#184f95", "#3987e5", "#86b6ef", "#cde2fb"],
               5: ["#184f95", "#256abf", "#3987e5", "#6da7ec", "#9ec5f4"]},
        claras_rampa=lambda n: {n - 1, n - 2} if n >= 4 else {n - 1},
        faixa="rgba(57,135,229,0.16)", preenchimento="rgba(57,135,229,0.25)",
        escala=[[0, "#232529"], [1, "#6da7ec"]],
        divergente=[[0, "#e66767"], [0.5, "#383835"], [1, "#3987e5"]],
    ),
}
TINTA_ESCURA = "#1c1f22"
CINZA = "#898781"
GRADE = "rgba(137,135,129,0.25)"
FONTE = '"Public Sans", system-ui, sans-serif'
CONFIG = {"displaylogo": False, "modeBarButtonsToRemove": ["select2d", "lasso2d", "autoScale2d"]}


def tema() -> str:
    """'light' ou 'dark', conforme o tema ativo no navegador de quem acessa."""
    try:
        import streamlit as st
        return "dark" if st.context.theme.type == "dark" else "light"
    except Exception:
        return "light"


def _p():
    return PALETAS[tema()]


def _layout(fig: go.Figure, titulo: str = "", altura: int = 400, legenda_embaixo: bool = False) -> go.Figure:
    # Espaço no topo para o título e para a legenda (uma ou duas linhas), sem sobreposição
    itens = [tr for tr in fig.data if tr.name and tr.showlegend is not False]
    linhas_legenda = 0 if not itens or legenda_embaixo else (1 if len(itens) <= 3 else 2)
    topo = (40 if titulo else 12) + 26 * linhas_legenda
    fig.update_layout(
        title=dict(text=titulo, x=0, xanchor="left", y=1, yanchor="top", yref="container",
                   pad=dict(t=8), font=dict(size=15)),
        height=altura + 26 * linhas_legenda,
        margin=dict(l=10, r=20, t=topo + 8, b=10),
        font=dict(family=FONTE, size=13),
        bargap=0.3,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0, title=None),
        hoverlabel=dict(font_family=FONTE),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    if legenda_embaixo:
        fig.update_layout(legend=dict(orientation="h", yanchor="top", y=-0.2, x=0),
                          margin=dict(b=90), height=altura + 50)
    fig.update_xaxes(showgrid=False, linecolor=GRADE, zeroline=False)
    fig.update_yaxes(gridcolor=GRADE, zeroline=False)
    return fig


def _linha_vertical(fig, x, nome, cor, traco):
    """Linha de referência; o valor vai na legenda para não cobrir as barras."""
    fig.add_vline(x=x, line=dict(color=cor, width=2, dash=traco))
    fig.add_trace(go.Scatter(x=[None], y=[None], mode="lines", name=f"{nome}: {est.fmt(x)}",
                             line=dict(color=cor, width=2, dash=traco)))


def _cores_categorias(chave: str):
    """Cor fixa por categoria: rampa para ordinais, paleta categórica para nominais."""
    p = _p()
    opcoes = list(cfg.POR_CHAVE[chave]["opcoes"])
    if cfg.POR_CHAVE[chave]["tipo"] == est.ORD and len(opcoes) in p["rampa"]:
        return opcoes, p["rampa"][len(opcoes)], p["claras_rampa"](len(opcoes))
    claras = {3} if tema() == "light" else set()
    return opcoes, p["cat"], claras


# ---------------------------------------------------------------------------
# Distribuição de uma pergunta (Laboratório)
# ---------------------------------------------------------------------------
def distribuicao(serie: pd.Series, tipo: str, medidas: list[str], titulo: str = "") -> go.Figure:
    tab = est.tabela_frequencias(serie, tipo)
    if tipo == est.QUANT:
        return _distribuicao_quantitativa(serie, medidas, titulo)
    return _distribuicao_categorica(serie, tipo, tab, medidas, titulo)


def _distribuicao_quantitativa(serie, medidas, titulo):
    p = _p()
    x = serie.to_numpy(dtype=float)
    cont = pd.Series(x).value_counts().sort_index()
    fig = go.Figure(go.Bar(
        x=cont.index, y=cont.values, marker_color=p["cat"][0], showlegend=False,
        customdata=cont.values / len(x),
        hovertemplate="Valor %{x}<br>%{y} pessoa(s), %{customdata:.1%}<extra></extra>",
    ))
    m, s = x.mean(), x.std(ddof=1)
    lim = (x.min() - 0.6, x.max() + 0.6)
    if "desvio_padrao" in medidas:
        fig.add_vrect(x0=max(m - s, lim[0]), x1=min(m + s, lim[1]), fillcolor=p["faixa"],
                      line_width=0, layer="below")
        fig.add_trace(go.Scatter(x=[None], y=[None], mode="markers", name=f"Média ± 1 desvio padrão ({est.fmt(s)})",
                                 marker=dict(symbol="square", size=12, color=p["faixa"])))
    if "quartis" in medidas or "iqr" in medidas:
        q1, q3 = np.percentile(x, [25, 75])
        for q, nome in ((q1, "Q1"), (q3, "Q3")):
            fig.add_vline(x=q, line=dict(color=CINZA, width=1, dash="dot"))
            fig.add_annotation(x=q, y=0.04, yref="paper", text=nome, showarrow=False,
                               xanchor="left", xshift=3, font=dict(size=11))
    if "media" in medidas:
        _linha_vertical(fig, m, "Média", p["cat"][1], "solid")
    if "mediana" in medidas:
        _linha_vertical(fig, float(np.median(x)), "Mediana", p["cat"][2], "dash")
    if "moda" in medidas:
        r = est.calcular(serie, "moda", est.QUANT)
        if r["valor"] is not None:
            _linha_vertical(fig, float(r["valor"]), "Moda", p["cat"][6], "dot")
    fig.update_xaxes(title="Resposta", dtick=1, range=list(lim))
    fig.update_yaxes(title="Pessoas")
    return _layout(fig, titulo, legenda_embaixo=True)


def _distribuicao_categorica(serie, tipo, tab, medidas, titulo):
    p = _p()
    horizontal = tipo == est.NOM
    rotulos = tab["Resposta"].tolist()
    textos = [f"{fi} ({est.fmt_pct(fr)})" for fi, fr in zip(tab["Frequência (fi)"], tab["Relativa (fr)"])]
    if horizontal and "moda" in medidas:
        moda = est.calcular(serie, "moda", tipo)["texto"]
        textos = [t + "   moda" if r == moda else t for r, t in zip(rotulos, textos)]

    if horizontal:
        fig = go.Figure(go.Bar(
            y=rotulos[::-1], x=tab["Frequência (fi)"][::-1], orientation="h", text=textos[::-1],
            textposition="outside", cliponaxis=False, marker_color=p["cat"][0], showlegend=False,
            hovertemplate="%{y}<br>%{x} pessoa(s)<extra></extra>"))
        fig.update_xaxes(title="Pessoas", showgrid=True, gridcolor=GRADE,
                         range=[0, tab["Frequência (fi)"].max() * 1.4])
        fig.update_yaxes(title=None, showgrid=False)
        return _layout(fig, titulo, max(280, 70 + 40 * len(rotulos)))

    fig = go.Figure(go.Bar(
        x=rotulos, y=tab["Frequência (fi)"], text=textos, textposition="outside", cliponaxis=False,
        marker_color=p["cat"][0], showlegend=False, hovertemplate="%{x}<br>%{y} pessoa(s)<extra></extra>"))
    marcas = []
    if "moda" in medidas:
        marcas.append(("moda", est.calcular(serie, "moda", tipo)["texto"]))
    if "mediana" in medidas:
        marcas.append(("mediana", est.calcular(serie, "mediana", tipo)["texto"]))
    for i, (nome, cat) in enumerate(m for m in marcas if m[1] in rotulos):
        fig.add_annotation(x=cat, y=1.0 + 0.07 * i, yref="paper", text=nome, showarrow=False,
                           font=dict(size=12))
    fig.update_yaxes(title="Pessoas", range=[0, tab["Frequência (fi)"].max() * 1.22])
    fig.update_xaxes(title=None)
    return _layout(fig, titulo, 420)


def boxplot(serie: pd.Series, titulo: str = "") -> go.Figure:
    p = _p()
    fig = go.Figure(go.Box(
        x=serie.to_numpy(dtype=float), name="", boxpoints="outliers", boxmean=True,
        marker_color=p["cat"][0], line=dict(width=1.5), fillcolor=p["preenchimento"],
        hovertemplate="%{x}<extra></extra>"))
    fig.update_xaxes(dtick=1, showgrid=True, gridcolor=GRADE)
    fig.update_yaxes(showticklabels=False, showgrid=False)
    fig.add_annotation(text="Linha cheia: mediana. Tracejada: média. Pontos: valores atípicos.",
                       x=0, y=-0.5, xref="paper", yref="paper", showarrow=False,
                       xanchor="left", yanchor="top", font=dict(size=11, color=CINZA))
    fig = _layout(fig, titulo, altura=230)
    fig.update_layout(margin=dict(b=70))
    return fig


# ---------------------------------------------------------------------------
# Comparação entre grupos
# ---------------------------------------------------------------------------
def _grupos_validos(df, chave, grupo):
    sub = df[[chave, grupo]].dropna()
    n = sub[grupo].value_counts()
    ordem = list(sub[grupo].cat.categories) if isinstance(sub[grupo].dtype, pd.CategoricalDtype) \
        else sorted(n.index)
    validos = [g for g in ordem if n.get(g, 0) >= cfg.N_MINIMO]
    ocultos = [str(g) for g in ordem if 0 < n.get(g, 0) < cfg.N_MINIMO]
    return sub[sub[grupo].isin(validos)], validos, ocultos, n


def empilhadas(linhas: dict, chave_opcoes: str, titulo: str = "", rotulo_eixo: str = "") -> go.Figure:
    """
    Barras 100% empilhadas. `linhas` = {nome da linha: Series de respostas}.
    As cores seguem as opções de `chave_opcoes`.
    """
    opcoes, cores, claras = _cores_categorias(chave_opcoes)
    nomes = list(linhas.keys())
    props = {nome: s.value_counts(normalize=True) for nome, s in linhas.items()}
    fig = go.Figure()
    for i, c in enumerate(opcoes):
        vals = np.array([props[nm].get(c, 0.0) for nm in nomes])
        if vals.sum() == 0:
            continue
        fig.add_trace(go.Bar(
            y=nomes, x=vals, name=str(c), orientation="h", marker_color=cores[i % len(cores)],
            marker_line=dict(width=1.5, color="rgba(127,127,127,0.0)"),
            text=[est.fmt_pct(v, 0) if v >= 0.07 else "" for v in vals],
            textposition="inside", insidetextanchor="middle",
            textfont=dict(color=TINTA_ESCURA if i in claras else "#ffffff", size=12),
            hovertemplate=f"<b>{c}</b><br>%{{y}}: %{{x:.1%}}<extra></extra>"))
    fig.update_layout(barmode="stack", bargap=0.38, legend=dict(traceorder="normal"))
    fig.update_xaxes(tickformat=".0%", range=[0, 1], showgrid=False, title=rotulo_eixo or None)
    fig.update_yaxes(autorange="reversed", showgrid=False)
    return _layout(fig, titulo, altura=150 + 52 * len(nomes))


def comparacao(df: pd.DataFrame, chave: str, grupo: str, titulo: str = "") -> tuple[go.Figure, list]:
    """Mesma pergunta entre grupos. Devolve (figura, grupos ocultos por n < N_MINIMO)."""
    if chave == grupo:
        raise ValueError("A pergunta e o grupo de comparação precisam ser diferentes.")
    sub, validos, ocultos, n = _grupos_validos(df, chave, grupo)
    nomes = {g: f"{g} (n={n[g]})" for g in validos}

    if est.tipo_de(chave) == est.QUANT:
        p = _p()
        fig = go.Figure()
        for g in validos:
            fig.add_trace(go.Box(x=sub.loc[sub[grupo] == g, chave], name=nomes[g], boxmean=True,
                                 marker_color=p["cat"][0], fillcolor=p["preenchimento"],
                                 line=dict(width=1.5), boxpoints="outliers", showlegend=False))
        fig.update_xaxes(title=cfg.POR_CHAVE[chave]["curto"], dtick=1, showgrid=True, gridcolor=GRADE)
        fig.update_yaxes(autorange="reversed", showgrid=False)
        return _layout(fig, titulo, altura=130 + 70 * len(validos)), ocultos

    linhas = {nomes[g]: sub.loc[sub[grupo] == g, chave] for g in validos}
    return empilhadas(linhas, chave, titulo), ocultos


# ---------------------------------------------------------------------------
# Gráficos do dossiê e das análises
# ---------------------------------------------------------------------------
def duas_series(s1: pd.Series, s2: pd.Series, nome1: str, nome2: str, categorias: list,
                titulo: str = "", rotulo_y: str = "Pessoas") -> go.Figure:
    """Duas distribuições na mesma escala, lado a lado (ex.: candidato x celular)."""
    p = _p()
    fig = go.Figure()
    for s, nome, cor in ((s1, nome1, p["cat"][0]), (s2, nome2, p["cat"][1])):
        cont = s.value_counts().reindex(categorias, fill_value=0)
        fig.add_trace(go.Bar(
            x=[str(c) for c in categorias], y=cont.values, name=nome, marker_color=cor,
            text=[str(v) if v else "" for v in cont.values], textposition="outside", cliponaxis=False,
            hovertemplate=f"<b>{nome}</b><br>%{{x}}: %{{y}} pessoa(s)<extra></extra>"))
    fig.update_layout(barmode="group", bargap=0.28, bargroupgap=0.08)
    fig.update_xaxes(type="category")
    fig.update_yaxes(title=rotulo_y)
    return _layout(fig, titulo, 400)


def proporcoes(linhas: pd.DataFrame, titulo: str = "", rotulo: str = "rotulo") -> go.Figure:
    """
    Barras de porcentagem com a margem de erro desenhada.
    `linhas` precisa das colunas: rotulo, p, k, n, ic (tupla).
    """
    p = _p()
    linhas = linhas.iloc[::-1]
    lo = [r["p"] - r["ic"][0] for _, r in linhas.iterrows()]
    hi = [r["ic"][1] - r["p"] for _, r in linhas.iterrows()]
    fig = go.Figure(go.Bar(
        y=linhas[rotulo], x=linhas["p"], orientation="h", marker_color=p["cat"][0], showlegend=False,
        error_x=dict(type="data", symmetric=False, array=hi, arrayminus=lo,
                     color=CINZA, thickness=1.2, width=4),
        customdata=np.array([[r["ic"][0], r["ic"][1]] for _, r in linhas.iterrows()]),
        hovertemplate="%{y}<br>%{x:.0%} (margem: %{customdata[0]:.0%} a %{customdata[1]:.0%})<extra></extra>",
    ))
    # Rótulo depois do fim da margem de erro, para não cruzar com a linha
    fig.add_trace(go.Scatter(
        y=linhas[rotulo], x=[r["ic"][1] + 0.015 for _, r in linhas.iterrows()], mode="text",
        text=[f"<b>{round(v * 100)}%</b>  {k} de {n}" for v, k, n in zip(linhas["p"], linhas["k"], linhas["n"])],
        textposition="middle right", showlegend=False, hoverinfo="skip", cliponaxis=False))
    fig.update_xaxes(tickformat=".0%", range=[0, 1.25], tickvals=[0, 0.25, 0.5, 0.75, 1],
                     showgrid=True, gridcolor=GRADE)
    fig.update_yaxes(showgrid=False)
    return _layout(fig, titulo, altura=110 + 46 * len(linhas))


def mapa_calor(tab: pd.DataFrame, titulo: str = "", formato: str = "pct",
               divergente: bool = False, rotulo_cor: str = "") -> go.Figure:
    """Tabela cruzada (percentuais por linha) ou matriz de correlação."""
    p = _p()
    z = tab.to_numpy(dtype=float)
    if formato == "pct":
        texto = [[f"{round(v * 100)}%" for v in linha] for linha in z]
    else:
        texto = [[est.fmt(v) if not np.isnan(v) else "" for v in linha] for linha in z]
    if formato == "num":
        texto = [["" if (not np.isnan(v) and v == 0 and not divergente) else t for v, t in zip(lz, lt)]
                 for lz, lt in zip(z, texto)]
    fig = go.Figure(go.Heatmap(
        z=z, x=[str(c) for c in tab.columns], y=[str(i) for i in tab.index],
        colorscale=p["divergente"] if divergente else p["escala"],
        zmin=-1 if divergente else 0, zmax=1 if divergente or formato == "pct" else None,
        text=texto, texttemplate="%{text}", textfont=dict(size=12),
        xgap=2, ygap=2, colorbar=dict(title=rotulo_cor, thickness=10, tickformat=".0%" if formato == "pct" else None),
        hovertemplate="%{y}<br>%{x}: %{text}<extra></extra>"))
    muitas = len(tab.columns) > 6
    fig.update_yaxes(autorange="reversed", showgrid=False, type="category")
    fig.update_xaxes(showgrid=False, type="category", side="bottom" if muitas else "top",
                     tickangle=-35 if muitas else 0)
    fig = _layout(fig, titulo, altura=140 + 48 * len(tab.index) + (90 if muitas else 0))
    fig.update_layout(margin=dict(t=60 if muitas else 100, b=120 if muitas else 10))
    return fig


def antes_depois(pre: pd.Series, pos: pd.Series, titulo: str = "") -> go.Figure:
    return duas_series(pre.astype(int), pos.astype(int), "Nota no início", "Nota no fim",
                       list(range(0, 11)), titulo)


def coleta(carimbos: pd.Series, titulo: str = "") -> go.Figure:
    p = _p()
    dias = carimbos.dt.normalize().value_counts().sort_index()
    idx = pd.date_range(dias.index.min(), dias.index.max(), freq="D")
    dias = dias.reindex(idx, fill_value=0)
    fig = go.Figure(go.Bar(x=dias.index, y=dias.values, marker_color=p["cat"][0], showlegend=False,
                           customdata=dias.cumsum().values,
                           hovertemplate="%{x|%d/%m}: %{y} resposta(s), %{customdata} no total<extra></extra>"))
    fig.update_xaxes(tickformat="%d/%m", dtick=86400000 * 2)
    fig.update_yaxes(title="Respostas no dia")
    return _layout(fig, titulo, 340)
