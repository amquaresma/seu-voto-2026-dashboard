"""Funções usadas por várias páginas: carregar a base e filtrar respostas."""
import pandas as pd
import streamlit as st

import config as cfg
import preparar_dados as prep

FILTROS = ["grupo_idade", "faixa_etaria", "escolaridade", "fonte_info", "eh_votante"]


@st.cache_data
def carregar() -> pd.DataFrame:
    return prep.carregar_limpo()


def rotulo(chave: str) -> str:
    return cfg.POR_CHAVE[chave]["curto"]


def recorte(prefixo: str) -> tuple[pd.DataFrame, dict]:
    """
    Filtros num painel recolhível. Devolve (base filtrada, filtros escolhidos).
    Campo vazio significa "todos".
    """
    base = carregar()
    filtros = {}
    ativos = sum(bool(st.session_state.get(f"{prefixo}_{c}")) for c in FILTROS)
    titulo = "Filtrar respostas" + (f" ({ativos} filtro{'s' if ativos > 1 else ''} ativo{'s' if ativos > 1 else ''})" if ativos else "")
    with st.popover(titulo):
        st.caption("Deixe em branco para incluir todos.")
        for chave in FILTROS:
            opcoes = [c for c in base[chave].cat.categories if (base[chave] == c).any()]
            filtros[chave] = st.multiselect(rotulo(chave), opcoes, placeholder="Todos",
                                            key=f"{prefixo}_{chave}")
    df = base
    for chave, valores in filtros.items():
        if valores:
            df = df[df[chave].isin(valores)]
    return df, {k: v for k, v in filtros.items() if v}


def aviso_amostra_pequena(n: int) -> bool:
    """Mostra o aviso e devolve True se o recorte for pequeno demais para exibir."""
    if n < cfg.N_MINIMO:
        st.warning(f"Este recorte tem {n} resposta(s). Abaixo de {cfg.N_MINIMO}, os resultados ficam "
                   "ocultos para proteger o anonimato e evitar conclusões tiradas de poucas pessoas.")
        return True
    return False
