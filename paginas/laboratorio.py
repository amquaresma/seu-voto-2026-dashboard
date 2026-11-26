"""Laboratório: escolha a pergunta e as medidas; veja fórmula e conta com os dados reais."""
import streamlit as st

import config as cfg
import estatisticas as est
import estilo
import graficos as graf
import textos as tx
from comum import aviso_amostra_pequena, recorte, rotulo

NOME_TIPO = {
    est.QUANT: "Quantitativa: escala numérica de 0 a 10",
    est.ORD: "Qualitativa ordinal: categorias com ordem",
    est.NOM: "Qualitativa nominal: categorias sem ordem",
}
PUBLICO = {"votantes": "Só quem votou", "nao_votantes": "Só quem não votou", "todos": "Todas as pessoas"}
PADRAO = {est.QUANT: {"media", "mediana", "moda", "desvio_padrao"},
          est.ORD: {"mediana", "moda"}, est.NOM: {"moda"}}
COMPARAR = ["grupo_idade", "faixa_etaria", "escolaridade", "fonte_info", "eh_votante"]


def render():
    st.title("Laboratório estatístico")
    estilo.prosa("Escolha uma pergunta e as medidas que quer calcular. Só aparecem liberadas as medidas "
                 "que fazem sentido para o tipo de variável, e cada uma mostra a fórmula e a conta feita "
                 "com os dados reais.")

    df, _ = recorte("lab")
    if aviso_amostra_pequena(len(df)):
        return

    analisaveis = [p["chave"] for p in cfg.TODAS if p["tipo"] in (est.QUANT, est.ORD, est.NOM)]
    chave = st.selectbox("Pergunta", analisaveis, index=analisaveis.index("autoav_pre"),
                         format_func=lambda k: f"{rotulo(k)}  ({cfg.POR_CHAVE[k]['secao']})")
    p = cfg.POR_CHAVE[chave]
    tipo = p["tipo"]
    serie = est.serie_valida(df, chave)
    estilo.nota(f"“{tx.PERGUNTAS_COMPLETAS.get(chave, rotulo(chave))}”")

    c1, c2, c3 = st.columns(3)
    c1.metric("Tipo de variável", NOME_TIPO[tipo].split(":")[0])
    c2.metric("Quem respondeu", PUBLICO[p["publico"]])
    c3.metric("Respostas válidas", len(serie))
    estilo.nota(NOME_TIPO[tipo] + ".")
    if aviso_amostra_pequena(len(serie)):
        return

    st.subheader("Medidas")
    colunas = st.columns(len(est.GRUPOS))
    escolhidas = []
    for col, grupo in zip(colunas, est.GRUPOS):
        col.markdown(f"**{grupo}**")
        for m, info in est.MEDIDAS.items():
            if info["grupo"] != grupo:
                continue
            valida = est.medida_valida(m, tipo)
            if col.checkbox(info["nome"], value=valida and m in PADRAO[tipo], disabled=not valida,
                            key=f"m_{tipo}_{m}",
                            help=None if valida else est.motivo_bloqueio(m, tipo)) and valida:
                escolhidas.append(m)
    if tipo != est.QUANT:
        estilo.nota("As medidas em cinza não valem para este tipo de variável. Passe o mouse no ícone "
                    "de ajuda ao lado de cada uma para ver o motivo.")

    st.subheader("Resultado")
    g1, g2 = st.columns([3, 2], gap="large")
    with g1:
        st.plotly_chart(graf.distribuicao(serie, tipo, escolhidas, rotulo(chave)),
                        width="stretch", config=graf.CONFIG)
        if tipo == est.QUANT:
            st.plotly_chart(graf.boxplot(serie), width="stretch", config=graf.CONFIG)
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
        estilo.nota("fi: frequência absoluta. fr: relativa. Fi: acumulada. Fr: relativa acumulada.")

    if escolhidas:
        st.subheader("Como cada número foi calculado")
        for m in escolhidas:
            info = est.MEDIDAS[m]
            r = est.calcular(serie, m, tipo)
            with st.expander(f"{info['nome']}: {r['texto']}"):
                st.latex(info["formula"])
                st.markdown(r["passos"])

    st.subheader("Comparar entre grupos")
    grupo = st.selectbox("Comparar por", ["nenhum"] + [g for g in COMPARAR if g != chave],
                         format_func=lambda k: "Sem comparação" if k == "nenhum" else rotulo(k))
    if grupo != "nenhum":
        fig, ocultos = graf.comparacao(df, chave, grupo, f"{rotulo(chave)}, por {rotulo(grupo).lower()}")
        st.plotly_chart(fig, width="stretch", config=graf.CONFIG)
        st.dataframe(est.por_grupo(df, chave, grupo, escolhidas), hide_index=True, width="stretch")
        if ocultos:
            estilo.nota(f"Grupos com menos de {cfg.N_MINIMO} respostas ficam ocultos: {', '.join(ocultos)}.")


render()
