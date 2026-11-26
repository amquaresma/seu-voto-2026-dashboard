"""Página principal: a pesquisa contada como reportagem, com todos os números visíveis."""
from html import escape

import pandas as pd
import streamlit as st

import achados as ach
import config as cfg
import estatisticas as est
import estilo
import graficos as graf
import textos as tx
from comum import carregar


def _secao(chave: str):
    s = tx.SECOES[chave]
    st.header(s["titulo"], anchor=chave)
    estilo.prosa(s["intro"])


def _n(r: dict) -> str:
    return f"{ach.pct(r['p'])} ({r['k']} de {r['n']})"


def render():
    df = carregar()
    vot = df[df["eh_votante"] == "Votou"]
    nao = df[df["eh_votante"] == "Não votou"]
    inicio, fim = df["carimbo"].min(), df["carimbo"].max()

    # Abertura: manchete à esquerda, urna ilustrativa ao lado
    texto, ilustracao = st.columns([3, 2], gap="large", vertical_alignment="center")
    with texto:
        estilo.html(f'<h1 class="manchete">{tx.MANCHETE}</h1>')
        estilo.html(f'<p class="linha-fina">{tx.LINHA_FINA.format(n=len(df))}</p>')
    with ilustracao:
        estilo.urna("Deputado federal")

    celular = ach.proporcao(df, "celular_x_candidato", ["Pesquisou mais o celular"])
    estilo.html(f'<p class="achado-principal">{ach.frase(ach.POR_ID["celular"], celular)}</p>')
    estilo.nota(ach.meta(celular))

    # Como foi feito
    st.header("Como a pesquisa foi feita", anchor="metodo")
    blocos = "".join(f'<div class="principio"><h4>{t}</h4><p>{d}</p></div>' for t, d in tx.PRINCIPIOS)
    estilo.html(f'<div class="principios">{blocos}</div>')
    estilo.prosa(*[p.format(inicio=f"{inicio:%d/%m}", fim=f"{fim:%d/%m/%Y}") for p in tx.COMO_FOI_FEITO])
    estilo.prosa(f"Foram **{len(df)} respostas**: {len(vot)} de pessoas que votaram e {len(nao)} de "
                 f"pessoas que não votaram. Todo percentual abaixo informa de quantas respostas saiu.")

    # Memória
    _secao("memoria")
    lembra = {
        "Deputado federal": vot["lembra_dep_federal"].dropna(),
        "Deputado estadual": vot["lembra_dep_estadual"].dropna(),
        "Senadores": vot["lembra_senadores"].dropna(),
    }
    st.plotly_chart(graf.empilhadas(lembra, "lembra_dep_federal", "Você lembra o nome de quem recebeu seu voto?"),
                    width="stretch", config=graf.CONFIG)
    fed = ach.proporcao(vot, "lembra_dep_federal", ["Sim, lembro o nome"])
    nulo = ach.proporcao(vot, "lembra_dep_federal", ["Votei branco ou nulo", "Votei só no número do partido"])
    nao_sabe = ach.proporcao(vot, "sabe_eleito_federal", ["Não sei"], ["Não se aplica"])
    estilo.prosa(
        f"Entre os eleitores, **{_n(fed)}** dizem lembrar o nome do deputado federal em quem votaram. "
        f"Outros {_n(nulo)} votaram em branco, nulo ou só no número do partido.",
        f"Lembrar o nome não significa acompanhar o resultado: {_n(nao_sabe)} dos que escolheram um candidato "
        f"não sabem se ele foi eleito.",
    )
    estilo.nota("Respostas autodeclaradas: o formulário não pediu o nome do candidato, então não há como "
                "conferir se a lembrança está certa.")

    # Decisão
    _secao("decisao")
    st.plotly_chart(graf.duas_series(vot["tempo_candidato"].dropna(), vot["tempo_celular"].dropna(),
                                     "Pesquisando o candidato a deputado federal", "Pesquisando antes de comprar um celular",
                                     cfg.TEMPO_PESQUISA, "Quanto tempo de pesquisa cada escolha recebeu"),
                    width="stretch", config=graf.CONFIG)
    mais_cand = ach.proporcao(df, "celular_x_candidato", ["Pesquisou mais o candidato"])
    tarde = ach.proporcao(vot, "quando_decidiu", ach.POR_ID["decidiu_tarde"]["respostas"])
    proposta = ach.proporcao(vot, "conhece_proposta", ach.POR_ID["proposta"]["respostas"], ["Não se aplica"])
    estilo.prosa(
        f"**{_n(celular)}** dos eleitores dedicaram mais tempo à pesquisa de um celular do que à do deputado "
        f"federal. Só {_n(mais_cand)} fizeram o contrário.",
        f"A decisão também costuma ser tardia: {_n(tarde)} só escolheram o deputado federal na última semana, "
        f"no dia da eleição ou diante da urna. E {_n(proposta)} não sabem explicar com segurança nenhuma "
        f"proposta de quem escolheram.",
    )
    st.plotly_chart(graf.distribuicao(est.serie_valida(vot, "o_que_pesou"), est.NOM, ["moda"],
                                      "O que mais pesou na escolha do deputado federal"),
                    width="stretch", config=graf.CONFIG)

    # Clima
    _secao("clima")
    itens = [("fake", "Receberam notícia falsa ou duvidosa"), ("ia", "Viram conteúdo de candidatos feito com IA"),
             ("briga", "Brigaram ou se afastaram de alguém próximo"), ("bolha", "Viam no feed só opiniões parecidas"),
             ("debate", "Não viram nenhum debate completo"), ("sem_checar", "Compartilharam sem checar ou não lembram")]
    linhas = []
    for id_, rot in itens:
        a = ach.POR_ID[id_]
        linhas.append(dict(rotulo=rot, **ach.proporcao(vot, a["chave"], a["respostas"], a.get("excluir"))))
    st.plotly_chart(graf.proporcoes(pd.DataFrame(linhas), "Entre os eleitores, quantos disseram que..."),
                    width="stretch", config=graf.CONFIG)
    estilo.nota("A linha fina em cada barra é a margem de erro: com poucas respostas, o valor real "
                "pode estar em qualquer ponto dela.")

    # Antes e depois
    _secao("antes_depois")
    st.plotly_chart(graf.antes_depois(vot["autoav_pre"].dropna(), vot["autoav_pos"].dropna(),
                                      "Nota que cada eleitor deu ao próprio voto"),
                    width="stretch", config=graf.CONFIG)
    pre, pos = vot["autoav_pre"].dropna(), vot["autoav_pos"].dropna()
    dez = ach.proporcao(vot, "autoav_pre", [10])
    mud = vot["clarao_cat"].value_counts()
    estilo.prosa(
        f"No início do formulário, **{_n(dez)}** deram nota 10 ao próprio voto, e a média foi "
        f"{est.fmt(pre.mean())}. No fim, a média caiu para {est.fmt(pos.mean())}.",
        f"{mud.get('Baixou a nota', 0)} pessoas baixaram a nota, {mud.get('Manteve', 0)} mantiveram e "
        f"{mud.get('Subiu a nota', 0)} subiram. A queda é pequena porque a maioria já começou no máximo "
        f"da escala, o que também é um resultado: quem respondeu avalia muito bem o próprio voto.",
    )
    st.page_link("paginas/analises.py", label="Ver o teste estatístico e a relação com o tempo de pesquisa")

    # Quem não votou
    _secao("nao_votou")
    if len(nao) >= cfg.N_MINIMO:
        st.plotly_chart(graf.distribuicao(est.serie_valida(nao, "motivo_nao_votou"), est.NOM, [],
                                          f"Principal motivo para não votar ({len(nao)} pessoas)"),
                        width="stretch", config=graf.CONFIG)
    else:
        estilo.nota(f"Só {len(nao)} pessoas não votaram: poucas demais para exibir os motivos.")

    # O que mudaria
    _secao("mudaria")
    comentarios = df["mudaria"].dropna().astype(str).str.strip()
    estilo.html("".join(f'<div class="comentario">{escape(c)}</div>' for c in comentarios))
    estilo.nota(f"{len(comentarios)} comentários de {len(df)} pessoas.")

    # Limitações
    st.header("O que estes dados não dizem", anchor="limites")
    estilo.prosa(*tx.LIMITACOES)
    st.page_link("paginas/metodologia.py", label="Ver a metodologia completa e baixar os dados")


render()
