"""Metodologia: como foi feito, questionário, tratamento, limitações e download."""
import pandas as pd
import streamlit as st

import config as cfg
import estilo
import preparar_dados as prep
import textos as tx
from comum import carregar, rotulo

TIPOS = {"quantitativa": "Quantitativa", "ordinal": "Qualitativa ordinal",
         "nominal": "Qualitativa nominal", "texto": "Texto aberto", "data": "Data e hora"}
PUBLICO = {"votantes": "Quem votou", "nao_votantes": "Quem não votou", "todos": "Todos"}


def render():
    df = carregar()
    rel = prep.relatorio_qualidade(df)
    st.title("Metodologia e dados")

    st.header("Como a pesquisa foi feita")
    blocos = "".join(f'<div class="principio"><h4>{t}</h4><p>{d}</p></div>' for t, d in tx.PRINCIPIOS)
    estilo.html(f'<div class="principios">{blocos}</div>')
    inicio, fim = rel["periodo"]
    estilo.prosa(*[p.format(inicio=f"{inicio:%d/%m}", fim=f"{fim:%d/%m/%Y}") for p in tx.COMO_FOI_FEITO])

    st.header("O questionário")
    linhas = [dict(Pergunta=tx.PERGUNTAS_COMPLETAS.get(p["chave"], p["curto"]),
                   Tipo=TIPOS[p["tipo"]], Respondida_por=PUBLICO[p["publico"]])
              for p in cfg.PERGUNTAS if p["tipo"] != "data"]
    st.dataframe(pd.DataFrame(linhas).rename(columns={"Respondida_por": "Respondida por"}),
                 hide_index=True, width="stretch")
    estilo.nota("O tipo de cada pergunta define quais medidas estatísticas podem ser usadas nela. "
                "Quem não votou pulou direto para a seção final.")

    st.header("Variáveis criadas na análise")
    derivadas = pd.DataFrame([dict(Variável=p["curto"], Descrição=tx.PERGUNTAS_COMPLETAS.get(p["chave"], ""),
                                   Tipo=TIPOS[p["tipo"]]) for p in cfg.DERIVADAS])
    st.dataframe(derivadas, hide_index=True, width="stretch")
    estilo.nota("Índice de memória: lembrar o nome vale 2, lembrar vagamente vale 1 e não lembrar vale 0, "
                "para deputado federal, estadual e senadores. A média vira uma nota de 0 a 10. Branco, nulo "
                "e voto só no partido não entram na conta.")

    st.header("Tratamento dos dados")
    rec = rel["recodificados"]
    estilo.prosa(
        f"**Nenhuma resposta foi excluída.** As {rel['total']} pessoas estão em todas as análises.",
        f"**{rel['comentarios_removidos']} comentário** da pergunta aberta foi retirado por conter discurso "
        f"violento. A pessoa continua na amostra com as outras respostas.",
        f"**{sum(rec.values())} respostas digitadas em “Outro”** foram agrupadas na categoria "
        f"correspondente: {rec['o_que_pesou']} em “O que mais pesou”, {rec['motivo_nao_votou']} em "
        f"“Motivo de não ter votado” e {rec['debate']} respostas “Não se aplica” na pergunta sobre "
        f"debates, tratadas como “não assistiu”, porque a opção “Não assisti” não estava no formulário.",
        f"**Respostas inconsistentes foram sinalizadas, não apagadas**: "
        f"{rel['alerta_2turno_lembra_deputado']} pessoa votou só no 2º turno e disse lembrar do deputado, "
        f"que é eleito no 1º; {rel['alerta_branco_pesquisou']} votaram em branco ou nulo para deputado "
        f"federal e disseram ter pesquisado o candidato.",
    )

    st.header("Limitações")
    estilo.prosa(*tx.LIMITACOES)

    st.header("Os dados")
    so_alertas = st.toggle("Mostrar só as respostas sinalizadas")
    tabela = df[df["tem_alerta"]] if so_alertas else df
    st.dataframe(tabela.rename(columns={p["chave"]: p["curto"] for p in cfg.TODAS}),
                 width="stretch", hide_index=True)
    st.download_button("Baixar a base tratada (CSV)", df.to_csv(index=False).encode("utf-8"),
                       file_name="seu_voto_2026_respostas.csv", mime="text/csv")
    estilo.nota("A base não tem nome, e-mail nem outro dado que identifique as pessoas. "
                "O comentário removido também não está nela.")


render()
