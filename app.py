"""
Site do projeto. Etapa 1: tela de conferência da base.
(As páginas do Dossiê e o Modo Laboratório entram nas próximas etapas.)

Rodar:  streamlit run app.py
"""
import pandas as pd
import streamlit as st

import config as cfg
import preparar_dados as prep

st.set_page_config(page_title="Seu voto em 2026", page_icon="🗳️", layout="wide")


@st.cache_data
def carregar():
    return prep.carregar_limpo()


df = carregar()
rel = prep.relatorio_qualidade(df)

st.title("Seu voto em 2026: o quanto você lembra?")
st.caption("Etapa 1: conferência da base de dados")

c1, c2, c3, c4 = st.columns(4)
c1.metric("Respostas", rel["total"])
c2.metric("Votaram", rel["votantes"])
c3.metric("Não votaram", rel["nao_votantes"])
c4.metric("Período", f"{rel['periodo'][0]:%d/%m} a {rel['periodo'][1]:%d/%m}")

st.subheader("Qualidade dos dados")
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

st.subheader("Variáveis derivadas (só quem votou)")
v = df[df["eh_votante"] == "Votou"]
d1, d2, d3 = st.columns(3)
with d1:
    st.markdown("**Celular x candidato**")
    st.dataframe(v["celular_x_candidato"].value_counts().rename("pessoas"))
with d2:
    st.markdown("**Mudança da nota (clarão)**")
    st.dataframe(v["clarao_cat"].value_counts().rename("pessoas"))
with d3:
    st.markdown("**Índice de memória (0 a 10)**")
    resumo = v["indice_memoria"].describe().round(2).rename("valor")
    resumo.index = ["n", "média", "desvio padrão", "mínimo", "Q1", "mediana", "Q3", "máximo"]
    st.dataframe(resumo)

st.subheader("Base completa")
so_alertas = st.toggle("Mostrar só respostas com alerta")
tabela = df[df["tem_alerta"]] if so_alertas else df
st.dataframe(
    tabela.rename(columns={p["chave"]: p["curto"] for p in cfg.TODAS}),
    width="stretch", hide_index=True,
)
