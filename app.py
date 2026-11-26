"""
Seu voto em 2026: o quanto você lembra?
Site da pesquisa. Cada página fica em paginas/.

Rodar:  streamlit run app.py
"""
import streamlit as st

import estilo

st.set_page_config(page_title="Seu voto em 2026", page_icon=estilo.favicon(), layout="wide")
estilo.aplicar()

PAGINAS = [
    st.Page("paginas/dossie.py", title="Dossiê", default=True),
    st.Page("paginas/explorar.py", title="Explorar achados", url_path="achados"),
    st.Page("paginas/laboratorio.py", title="Laboratório", url_path="laboratorio"),
    st.Page("paginas/analises.py", title="Análises", url_path="analises"),
    st.Page("paginas/metodologia.py", title="Metodologia", url_path="metodologia"),
]

atual = st.navigation(PAGINAS, position="hidden")
estilo.cabecalho(PAGINAS)
atual.run()
estilo.rodape(PAGINAS)
