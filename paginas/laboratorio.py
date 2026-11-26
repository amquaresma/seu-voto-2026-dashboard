"""Laboratório: escolha a pergunta e as medidas; veja fórmula e conta com os dados reais."""
from html import escape

import streamlit as st

import config as cfg
import estatisticas as est
import estilo
import graficos as graf
import textos as tx
from comum import aviso_amostra_pequena, recorte, rotulo

NOME_TIPO = {est.QUANT: "Quantitativa", est.ORD: "Qualitativa ordinal", est.NOM: "Qualitativa nominal"}
EXPLICA_TIPO = {
    est.QUANT: "números de uma escala, então todas as medidas valem",
    est.ORD: "categorias com ordem, então valem as medidas de posição",
    est.NOM: "categorias sem ordem, então vale a moda e a contagem de cada resposta",
}
POR_QUE = {
    est.ORD: ("Variável ordinal: as categorias têm ordem, mas a distância entre elas não é numérica. "
              "De “Nada” para “Menos de 30 minutos” não é o mesmo salto que de “30 minutos a 2 horas” "
              "para “Mais de 2 horas”. Por isso não existem média, variância nem desvio padrão aqui: "
              "valem as medidas de posição, como mediana e quartis."),
    est.NOM: ("Variável nominal: as categorias não têm ordem nem valor numérico. Não existe média entre "
              "Instagram e TV. Por isso valem só a moda e a contagem de cada resposta."),
}
PUBLICO = {"votantes": "Só quem votou", "nao_votantes": "Só quem não votou", "todos": "Todas as pessoas"}
PADRAO = {est.QUANT: ["media", "mediana", "moda", "desvio_padrao"],
          est.ORD: ["mediana", "moda", "quartis"], est.NOM: ["moda"]}
COMPARAR = ["grupo_idade", "faixa_etaria", "escolaridade", "fonte_info", "eh_votante"]


def _blocos(serie, tipo, escolhidas) -> str:
    itens = [("Respostas", str(len(serie)))]
    itens += [(est.MEDIDAS[m]["nome"], est.calcular(serie, m, tipo)["texto"]) for m in escolhidas]
    partes = []
    for nome, valor in itens:
        classe = "medida-valor texto" if len(valor) > 14 else "medida-valor"
        partes.append(f'<div class="medida"><div class="medida-nome">{escape(nome)}</div>'
                      f'<div class="{classe}">{escape(valor)}</div></div>')
    return f'<div class="medidas">{"".join(partes)}</div>'


def render():
    st.title("Laboratório estatístico")
    estilo.prosa("Escolha uma pergunta e as medidas. O laboratório só oferece as medidas que fazem sentido "
                 "para o tipo de variável e mostra a fórmula e a conta feita com os dados reais.")

    analisaveis = [p["chave"] for p in cfg.TODAS if p["tipo"] in (est.QUANT, est.ORD, est.NOM)]
    c1, c2 = st.columns([4, 1], vertical_alignment="bottom")
    chave = c1.selectbox("Pergunta", analisaveis, index=analisaveis.index("autoav_pre"),
                         format_func=lambda k: f"{rotulo(k)}  ({cfg.POR_CHAVE[k]['secao']})")
    with c2:
        df, _ = recorte("lab")

    p = cfg.POR_CHAVE[chave]
    tipo = p["tipo"]
    serie = est.serie_valida(df, chave)
    estilo.html(f'<div class="ficha"><div><span>Tipo</span>{NOME_TIPO[tipo]}</div>'
                f'<div><span>Quem respondeu</span>{PUBLICO[p["publico"]]}</div>'
                f'<div><span>Respostas válidas</span>{len(serie)}</div></div>')
    estilo.nota(f"Pergunta: “{tx.PERGUNTAS_COMPLETAS.get(chave, rotulo(chave))}” "
                f"É {NOME_TIPO[tipo].lower()}: {EXPLICA_TIPO[tipo]}.")
    if aviso_amostra_pequena(len(serie)):
        return

    # Escolha das medidas: só as válidas viram botões; as outras ficam explicadas abaixo
    validas = [m for g in est.GRUPOS for m, i in est.MEDIDAS.items() if i["grupo"] == g and est.medida_valida(m, tipo)]
    bloqueadas = [m for m in est.MEDIDAS if m not in validas]
    escolhidas = st.pills("Medidas", validas, selection_mode="multi",
                          default=[m for m in PADRAO[tipo] if m in validas],
                          format_func=lambda m: est.MEDIDAS[m]["nome"], key=f"pills_{tipo}") or []
    escolhidas = [m for m in validas if m in escolhidas]
    if bloqueadas:
        with st.expander(f"Por que {len(bloqueadas)} medidas não aparecem para esta pergunta?"):
            st.markdown(POR_QUE[tipo])
            st.caption("Fora desta pergunta: " + ", ".join(est.MEDIDAS[m]["nome"] for m in bloqueadas) + ".")

    estilo.html(_blocos(serie, tipo, escolhidas))

    aba_grafico, aba_tabela, aba_conta, aba_grupos = st.tabs(
        ["Gráfico", "Tabela de frequências", "Como foi calculado", "Comparar grupos"])

    with aba_grafico:
        st.plotly_chart(graf.distribuicao(serie, tipo, escolhidas, rotulo(chave)),
                        width="stretch", config=graf.CONFIG)
        if tipo == est.QUANT:
            st.plotly_chart(graf.boxplot(serie, "Resumo em cinco números (boxplot)"),
                            width="stretch", config=graf.CONFIG)

    with aba_tabela:
        freq = est.tabela_frequencias(serie, tipo).rename(columns={
            "Frequência (fi)": "fi", "Relativa (fr)": "fr",
            "Acumulada (Fi)": "Fi", "Relativa acumulada (Fr)": "Fr"})
        for c in ("fr", "Fr"):
            if c in freq:
                freq[c] = (freq[c] * 100).map(lambda v: est.fmt(v, 1) + "%")
        st.dataframe(freq, hide_index=True, width="stretch")
        estilo.nota("fi: frequência absoluta. fr: frequência relativa. Fi: frequência acumulada. "
                    "Fr: frequência relativa acumulada.")

    with aba_conta:
        if not escolhidas:
            st.info("Escolha pelo menos uma medida para ver a conta.")
        for m in escolhidas:
            info = est.MEDIDAS[m]
            r = est.calcular(serie, m, tipo)
            with st.expander(f"{info['nome']}: {r['texto']}", expanded=len(escolhidas) == 1):
                st.latex(info["formula"])
                st.markdown(r["passos"])

    with aba_grupos:
        grupo = st.selectbox("Comparar por", [g for g in COMPARAR if g != chave], format_func=rotulo)
        fig, ocultos = graf.comparacao(df, chave, grupo, f"{rotulo(chave)}, por {rotulo(grupo).lower()}")
        st.plotly_chart(fig, width="stretch", config=graf.CONFIG)
        if escolhidas:
            st.dataframe(est.por_grupo(df, chave, grupo, escolhidas), hide_index=True, width="stretch")
        if ocultos:
            estilo.nota(f"Grupos com menos de {cfg.N_MINIMO} respostas ficam ocultos: {', '.join(ocultos)}.")


render()
