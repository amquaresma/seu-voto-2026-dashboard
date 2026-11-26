"""Análises avançadas: antes x depois, correlação, cruzamento de perguntas e coleta."""
import pandas as pd
import streamlit as st

import avancado as av
import config as cfg
import estatisticas as est
import estilo
import graficos as graf
from comum import aviso_amostra_pequena, carregar, recorte, rotulo


def render():
    st.title("Análises avançadas")
    estilo.prosa(
        "Esta página vai além da estatística descritiva. Os testes usados aqui foram feitos para "
        "amostras aleatórias. Como esta amostra é por conveniência, leia os resultados como "
        "indícios sobre quem respondeu, nunca como prova sobre o eleitorado.")

    df, _ = recorte("av")
    if aviso_amostra_pequena(len(df)):
        return

    # Antes x depois
    st.header("A nota do voto mudou depois da reflexão?")
    r = av.antes_depois(df)
    if r["n"] >= cfg.N_MINIMO:
        st.plotly_chart(graf.mapa_calor(r["transicoes"], "Nota no início (linhas) e nota no fim (colunas)",
                                        formato="num", rotulo_cor="Pessoas"),
                        width="stretch", config=graf.CONFIG)
        estilo.nota("Cada célula conta quantas pessoas deram aquela combinação de notas. "
                    "Quem está na diagonal manteve a nota.")
        texto = [f"Entre {r['n']} eleitores, a média foi de {est.fmt(r['media_pre'])} para "
                 f"{est.fmt(r['media_pos'])} e a mediana, de {est.fmt(r['mediana_pre'])} para "
                 f"{est.fmt(r['mediana_pos'])}. {r['baixou']} baixaram a nota, {r['manteve']} mantiveram "
                 f"e {r['subiu']} subiram."]
        if "p" in r:
            texto.append(f"O teste de Wilcoxon para amostras pareadas compara as duas notas de cada pessoa. "
                         f"Aqui, a diferença {av.leitura_p(r['p'])}.")
        estilo.prosa(*texto)

    # Correlação
    st.header("O que anda junto com o quê")
    rho, n = av.correlacao(df)
    st.plotly_chart(graf.mapa_calor(rho, "Correlação de Spearman entre as perguntas com ordem",
                                    formato="num", divergente=True, rotulo_cor="rho"),
                    width="stretch", config=graf.CONFIG)
    estilo.prosa(
        "A correlação de Spearman vai de -1 a 1. Perto de 0, as respostas não têm relação; perto de 1, "
        "sobem juntas; perto de -1, uma sobe quando a outra desce. Ela mede associação, não causa.")
    fortes = av.correlacoes_fortes(rho)
    if fortes:
        st.markdown("**Pares com correlação de pelo menos 0,3, em valor absoluto**")
        st.dataframe(pd.DataFrame([dict(Par=f"{a} e {b}", rho=est.fmt(v),
                                        Leitura="sobem juntas" if v > 0 else "uma sobe quando a outra desce")
                                   for a, b, v in fortes]), hide_index=True, width="stretch")
    else:
        estilo.nota("Nenhum par passou de 0,3 neste recorte.")
    if "Nota do voto (fim)" in rho and "Pesquisa sobre o candidato" in rho:
        ini = rho.loc["Nota do voto (início)", "Pesquisa sobre o candidato"]
        fim = rho.loc["Nota do voto (fim)", "Pesquisa sobre o candidato"]
        estilo.prosa(f"Um detalhe: a nota dada no início tem correlação de {est.fmt(ini)} com o tempo de "
                     f"pesquisa sobre o candidato. A nota dada no fim, depois das perguntas, tem "
                     f"{est.fmt(fim)}. Quanto maior esse segundo número em relação ao primeiro, mais a "
                     f"reflexão aproximou a autoavaliação do que a pessoa de fato fez.")

    # Cruzamento
    st.header("Cruzar duas perguntas")
    categoricas = [p["chave"] for p in cfg.TODAS if p["tipo"] in (est.NOM, est.ORD)]
    c1, c2 = st.columns(2)
    linha = c1.selectbox("Linhas", categoricas, index=categoricas.index("grupo_idade"), format_func=rotulo)
    outras = [c for c in categoricas if c != linha]
    padrao = "celular_x_candidato" if "celular_x_candidato" in outras else outras[0]
    coluna = c2.selectbox("Colunas", outras, index=outras.index(padrao), format_func=rotulo)
    a = av.associacao(df, linha, coluna)
    if a["n"] < cfg.N_MINIMO:
        aviso_amostra_pequena(a["n"])
    else:
        st.plotly_chart(graf.mapa_calor(a["percentual"], f"{rotulo(coluna)}, por {rotulo(linha).lower()}",
                                        rotulo_cor="% da linha"),
                        width="stretch", config=graf.CONFIG)
        estilo.nota("Cada linha soma 100%. Compare as linhas entre si.")
        if "v" in a:
            texto = [f"Teste qui-quadrado com {a['n']} respostas: a associação entre as duas perguntas é "
                     f"{a['forca']} (V de Cramér = {est.fmt(a['v'])}) e {av.leitura_p(a['p'])}."]
            if a["esperado_baixo"] > 0.2:
                texto.append(f"Atenção: {round(a['esperado_baixo'] * 100)}% das células têm menos de 5 "
                             f"respostas esperadas. Com tão poucos casos, o teste perde confiabilidade.")
            estilo.prosa(*texto)
        with st.expander("Ver a tabela com as contagens"):
            st.dataframe(a["contagem"], width="stretch")

    # Coleta
    st.header("Como as respostas chegaram")
    base = carregar()
    st.plotly_chart(graf.coleta(base["carimbo"], "Respostas por dia"), width="stretch", config=graf.CONFIG)
    pico = base["carimbo"].dt.date.value_counts()
    estilo.prosa(f"A coleta durou de {base['carimbo'].min():%d/%m} a {base['carimbo'].max():%d/%m}. O dia com "
                 f"mais respostas foi {pico.idxmax():%d/%m}, com {pico.max()} de {len(base)}, o que mostra "
                 f"que boa parte da amostra veio de um mesmo compartilhamento.")


render()
