"""Explorador de achados: escolha pergunta, respostas e recorte; o site escreve a frase."""
import streamlit as st

import achados as ach
import config as cfg
import estatisticas as est
import estilo
import graficos as graf
import textos as tx
from comum import aviso_amostra_pequena, carregar, recorte, rotulo

NEUTRAS = ["Não se aplica", "Votei branco ou nulo", "Votei só no número do partido",
           "Não compartilhei nada", "Não uso redes sociais"]
COMPARAR = ["grupo_idade", "faixa_etaria", "escolaridade", "fonte_info", "eh_votante"]


def render():
    st.title("Explorar achados")
    estilo.prosa("Escolha uma pergunta e as respostas que interessam. O site escreve a frase com a "
                 "porcentagem, quantas pessoas ela representa e a margem de erro. Use o filtro para "
                 "olhar só um grupo, como as pessoas de 16 a 24 anos.")

    df, filtros = recorte("exp")
    desc = ach.descrever_recorte(filtros)
    st.caption(f"{len(df)} de {len(carregar())} respostas no recorte atual.")
    if aviso_amostra_pequena(len(df)):
        return

    # Monte a frase
    st.header("Monte uma frase")
    perguntas = [p["chave"] for p in cfg.TODAS
                 if p["tipo"] in (est.NOM, est.ORD, est.QUANT) and p["chave"] not in ("clarao", "indice_memoria")]
    c1, c2 = st.columns([2, 3])
    chave = c1.selectbox("Pergunta", perguntas, index=perguntas.index("celular_x_candidato"),
                         format_func=lambda k: rotulo(k))
    p = cfg.POR_CHAVE[chave]
    opcoes = [o for o in (p["opcoes"] or []) if (df[chave] == o).any()]
    curados = [a for a in ach.CURADOS if a["chave"] == chave]
    padrao = [o for o in (curados[0]["respostas"] if curados else opcoes[:1]) if o in opcoes]
    respostas = c2.multiselect("Respostas que contam", opcoes, default=padrao, key=f"resp_{chave}")
    estilo.nota(f"Pergunta no formulário: “{tx.PERGUNTAS_COMPLETAS.get(chave, rotulo(chave))}”")

    if not respostas:
        st.info("Escolha pelo menos uma resposta para montar a frase.")
    else:
        curado = ach.curado_para(chave, respostas)
        if curado:
            excluir = curado.get("excluir")
        else:
            tirar = st.checkbox("Desconsiderar respostas como “Não se aplica” e voto branco ou nulo",
                                value=True)
            excluir = [o for o in opcoes if o in NEUTRAS and o not in respostas] if tirar else None
        r = ach.proporcao(df, chave, respostas, excluir)
        if r["n"] < cfg.N_MINIMO:
            aviso_amostra_pequena(r["n"])
        else:
            texto = (ach.frase(curado, r, desc) if curado else
                     ach.frase_livre(chave, respostas, r, desc, tx.PERGUNTAS_COMPLETAS.get(chave, rotulo(chave))))
            estilo.html(f'<p class="frase-gerada">{texto}</p>')
            estilo.nota(ach.meta(r))

            grupo = st.selectbox("Comparar entre grupos", [g for g in COMPARAR if g != chave],
                                 format_func=rotulo)
            tab = ach.por_grupo(df, chave, respostas, excluir, grupo)
            visiveis = tab[~tab["oculto"]].rename(columns={"grupo": "rotulo"})
            if len(visiveis) >= 2:
                st.plotly_chart(graf.proporcoes(visiveis, f"A mesma frase em cada grupo: {rotulo(grupo).lower()}"),
                                width="stretch", config=graf.CONFIG)
            ocultos = tab.loc[tab["oculto"], "grupo"].tolist()
            if ocultos:
                estilo.nota(f"Grupos com menos de {cfg.N_MINIMO} respostas ficam de fora: {', '.join(ocultos)}.")
            if len(visiveis) >= 2:
                estilo.nota("Se as linhas de margem de erro de dois grupos se cruzam, a diferença entre "
                            "eles pode ser só acaso.")

    # Ranking
    st.header("Os achados mais fortes neste recorte")
    estilo.prosa("Frases preparadas a partir do questionário, calculadas para o recorte escolhido e "
                 "ordenadas da maior para a menor porcentagem.")
    blocos = []
    for a in ach.ranking(df):
        blocos.append(
            f'<div class="achado"><div class="achado-frase">{ach.frase(a, a, desc)}</div>'
            f'<div class="achado-meta">{ach.meta(a)}</div>{estilo.barra_html(a["p"])}</div>')
    estilo.html("".join(blocos) or '<p class="nota">Nenhum achado tem respostas suficientes neste recorte.</p>')


render()
