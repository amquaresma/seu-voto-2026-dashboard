"""
Site do projeto "Seu voto em 2026: o quanto você lembra?".

Modos (barra lateral):
    Dossiê              -> narrativa com as conclusões (etapa 3)
    Laboratório         -> escolha a pergunta e as medidas estatísticas
    Qualidade dos dados -> tratamento, alertas e download da base

Rodar:  streamlit run app.py
"""
import pandas as pd
import streamlit as st

import config as cfg
import estatisticas as est
import graficos as graf
import preparar_dados as prep

st.set_page_config(page_title="Seu voto em 2026", page_icon="🗳️", layout="wide")

NOME_TIPO = {
    est.QUANT: "Quantitativa (escala numérica)",
    est.ORD: "Qualitativa ordinal (categorias com ordem)",
    est.NOM: "Qualitativa nominal (categorias sem ordem)",
}
PUBLICO = {
    "votantes": "Respondida só por quem votou.",
    "nao_votantes": "Respondida só por quem não votou.",
    "todos": "Respondida por todos.",
}
PADRAO = {  # medidas que já vêm marcadas
    est.QUANT: {"media", "mediana", "moda", "desvio_padrao"},
    est.ORD: {"mediana", "moda"},
    est.NOM: {"moda"},
}
GRUPOS_COMPARACAO = ["grupo_idade", "faixa_etaria", "escolaridade", "fonte_info", "eh_votante"]
FILTROS = ["faixa_etaria", "escolaridade", "fonte_info", "eh_votante"]


@st.cache_data
def carregar() -> pd.DataFrame:
    return prep.carregar_limpo()


def rotulo(chave: str) -> str:
    return cfg.POR_CHAVE[chave]["curto"]


# ---------------------------------------------------------------------------
# Barra lateral: modo e filtros globais
# ---------------------------------------------------------------------------
base = carregar()

with st.sidebar:
    st.title("🗳️ Seu voto em 2026")
    modo = st.radio("Modo", ["📖 Dossiê", "🔬 Laboratório", "🧹 Qualidade dos dados"])

    st.divider()
    st.subheader("Filtros")
    st.caption("Valem para todas as telas.")
    st.caption("Vazio = todos.")
    df = base
    for chave in FILTROS:
        opcoes = [c for c in base[chave].cat.categories if (base[chave] == c).any()]
        escolha = st.multiselect(rotulo(chave), opcoes, placeholder="Todos", key=f"f_{chave}")
        if escolha:
            df = df[df[chave].isin(escolha)]

    st.metric("Respostas no filtro", f"{len(df)} de {len(base)}")
    if len(df) < cfg.N_MINIMO:
        st.error(f"Menos de {cfg.N_MINIMO} respostas: amplie os filtros.")

if len(df) < cfg.N_MINIMO:
    st.warning(f"O filtro deixou menos de {cfg.N_MINIMO} respostas. Para proteger o anonimato e "
               "evitar conclusões falsas, os resultados ficam ocultos.")
    st.stop()


# ---------------------------------------------------------------------------
# Modo Laboratório
# ---------------------------------------------------------------------------
def laboratorio(df: pd.DataFrame):
    st.title("🔬 Laboratório estatístico")
    st.caption("Escolha uma pergunta e as medidas. O site mostra só o que faz sentido "
               "para o tipo de variável e explica como cada número foi calculado.")

    analisaveis = [p for p in cfg.TODAS if p["tipo"] in (est.QUANT, est.ORD, est.NOM)]
    chaves = [p["chave"] for p in analisaveis]
    chave = st.selectbox(
        "Pergunta", chaves, index=chaves.index("autoav_pre"),
        format_func=lambda k: f"{cfg.POR_CHAVE[k]['secao']} · {rotulo(k)}",
    )
    p = cfg.POR_CHAVE[chave]
    tipo = p["tipo"]
    serie = est.serie_valida(df, chave)

    c1, c2, c3 = st.columns(3)
    c1.markdown(f"**Tipo de variável**  \n{NOME_TIPO[tipo]}")
    c2.markdown(f"**Quem respondeu**  \n{PUBLICO[p['publico']]}")
    c3.markdown(f"**Respostas válidas**  \n{len(serie)}")

    if len(serie) < cfg.N_MINIMO:
        st.warning(f"Só {len(serie)} resposta(s) para esta pergunta com os filtros atuais "
                   f"(mínimo {cfg.N_MINIMO}).")
        return

    # Escolha das medidas, por grupo; as inválidas aparecem bloqueadas
    st.subheader("Medidas")
    colunas = st.columns(len(est.GRUPOS))
    escolhidas = []
    for col, grupo in zip(colunas, est.GRUPOS):
        col.markdown(f"**{grupo}**")
        for m, info in est.MEDIDAS.items():
            if info["grupo"] != grupo:
                continue
            valida = est.medida_valida(m, tipo)
            marcada = col.checkbox(
                info["nome"] if valida else f"🔒 {info['nome']}",
                value=valida and m in PADRAO[tipo],
                disabled=not valida,
                key=f"m_{tipo}_{m}",
                help=None if valida else est.motivo_bloqueio(m, tipo),
            )
            if marcada and valida:
                escolhidas.append(m)

    if tipo != est.QUANT:
        with st.expander("🔒 Por que algumas medidas estão bloqueadas?"):
            st.markdown(est.MOTIVO_BLOQUEIO[tipo].format(medida="média, variância ou desvio padrão"))

    # Resultados
    st.subheader("Resultado")
    g1, g2 = st.columns([3, 2])
    with g1:
        st.plotly_chart(graf.distribuicao(serie, tipo, escolhidas, rotulo(chave)),
                        width="stretch", config={"displaylogo": False})
        if tipo == est.QUANT:
            caixa = graf.boxplot(serie)
            caixa.update_xaxes(title=None)   # a legenda da caixa já ocupa a base
            st.plotly_chart(caixa, width="stretch", config={"displaylogo": False})
    with g2:
        st.dataframe(est.resumo(serie, tipo, escolhidas), hide_index=True, width="stretch")

        freq = est.tabela_frequencias(serie, tipo).rename(columns={
            "Frequência (fi)": "fi", "Relativa (fr)": "fr",
            "Acumulada (Fi)": "Fi", "Relativa acumulada (Fr)": "Fr"})
        for c in ("fr", "Fr"):
            if c in freq:
                freq[c] = (freq[c] * 100).map(lambda v: est.fmt(v, 1) + "%")
        st.markdown("**Distribuição de frequências**")
        st.dataframe(freq, hide_index=True, width="stretch")
        st.caption("fi = frequência absoluta · fr = relativa · "
                   "Fi = acumulada · Fr = relativa acumulada")

    # Como foi calculado
    if escolhidas:
        st.subheader("🧮 Como foi calculado")
        for m in escolhidas:
            info = est.MEDIDAS[m]
            r = est.calcular(serie, m, tipo)
            with st.expander(f"{info['nome']}: {r['texto']}"):
                st.latex(info["formula"])
                st.markdown(r["passos"])

    # Comparação por grupo
    st.subheader("👥 Comparar por grupo")
    opcoes_grupo = [g for g in GRUPOS_COMPARACAO if g != chave]
    grupo = st.selectbox("Comparar por", ["(nenhum)"] + opcoes_grupo,
                         format_func=lambda k: k if k == "(nenhum)" else rotulo(k))
    if grupo != "(nenhum)":
        fig, ocultos = graf.comparacao(df, chave, grupo, f"{rotulo(chave)} por {rotulo(grupo).lower()}")
        st.plotly_chart(fig, width="stretch", config={"displaylogo": False})
        st.dataframe(est.por_grupo(df, chave, grupo, escolhidas), hide_index=True, width="stretch")
        if ocultos:
            st.caption(f"Ocultos por terem menos de {cfg.N_MINIMO} respostas: {', '.join(ocultos)}.")


# ---------------------------------------------------------------------------
# Modo Qualidade dos dados
# ---------------------------------------------------------------------------
def qualidade(df: pd.DataFrame):
    rel = prep.relatorio_qualidade(base)
    st.title("🧹 Qualidade dos dados")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Respostas", rel["total"])
    c2.metric("Votaram", rel["votantes"])
    c3.metric("Não votaram", rel["nao_votantes"])
    c4.metric("Período", f"{rel['periodo'][0]:%d/%m} a {rel['periodo'][1]:%d/%m}")

    st.markdown(
        f"""
- **Nenhuma resposta foi excluída.** Todas as {rel['total']} pessoas estão na análise.
- **Comentários removidos da parte pública:** {rel['comentarios_removidos']} (discurso violento). A pessoa continua na amostra.
- **Respostas de "Outro" agrupadas:** {sum(rel['recodificados'].values())}
  (o que pesou no voto: {rel['recodificados']['o_que_pesou']}, motivo de não votar:
  {rel['recodificados']['motivo_nao_votou']}, debate "Não se aplica": {rel['recodificados']['debate']}).
- **Alerta:** votou só no 2º turno, mas diz lembrar do deputado: {rel['alerta_2turno_lembra_deputado']}
  (deputados são escolhidos no 1º turno).
- **Alerta:** votou branco/nulo para deputado federal, mas diz ter pesquisado o candidato:
  {rel['alerta_branco_pesquisou']}.
"""
    )
    if rel["fora_das_opcoes"]:
        st.warning(f"Valores fora das opções previstas: {rel['fora_das_opcoes']}")

    st.subheader("Base de dados")
    so_alertas = st.toggle("Mostrar só respostas com alerta")
    tabela = df[df["tem_alerta"]] if so_alertas else df
    st.dataframe(tabela.rename(columns={p["chave"]: p["curto"] for p in cfg.TODAS}),
                 width="stretch", hide_index=True)
    st.download_button("⬇️ Baixar dados filtrados (CSV)", df.to_csv(index=False).encode("utf-8"),
                       file_name="seu_voto_2026_filtrado.csv", mime="text/csv")


# ---------------------------------------------------------------------------
# Modo Dossiê (etapa 3)
# ---------------------------------------------------------------------------
def dossie(df: pd.DataFrame):
    st.title("📖 Seu voto em 2026: o quanto você lembra?")
    st.info("O dossiê com as conclusões entra na etapa 3. Por enquanto, explore o "
            "**🔬 Laboratório** na barra lateral.")


{"📖 Dossiê": dossie, "🔬 Laboratório": laboratorio, "🧹 Qualidade dos dados": qualidade}[modo](df)
