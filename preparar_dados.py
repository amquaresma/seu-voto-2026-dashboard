"""
Etapa 1: preparação dos dados.

Lê o CSV baixado do Google Forms, limpa, recodifica, cria as variáveis
derivadas e marca problemas de qualidade. Gera o arquivo que o site usa.

Uso (na raiz do projeto):
    python preparar_dados.py
"""
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd

import config as cfg

LEMBRA_PONTOS = {"Sim, lembro o nome": 2, "Lembro vagamente": 1, "Não lembro": 0}
VOTANTES = ["Votei nos dois turnos", "Votei só no 1º turno", "Votei só no 2º turno"]


def _normalizar(texto: str) -> str:
    """Tira quebras de linha e espaços repetidos, para comparar cabeçalhos."""
    return re.sub(r"\s+", " ", str(texto)).strip().lower()


# ---------------------------------------------------------------------------
# 1. Leitura e conferência das colunas
# ---------------------------------------------------------------------------
def carregar_bruto(caminho: str = cfg.ARQUIVO_BRUTO) -> pd.DataFrame:
    df = pd.read_csv(caminho, dtype=str, keep_default_na=False)

    esperado = len(cfg.PERGUNTAS)
    if df.shape[1] != esperado:
        raise ValueError(
            f"O CSV tem {df.shape[1]} colunas, mas config.py descreve {esperado}. "
            "Alguma pergunta foi adicionada ou removida no Forms?"
        )

    # Confere, coluna por coluna, se o cabeçalho é a pergunta esperada
    erros = []
    for original, p in zip(df.columns, cfg.PERGUNTAS):
        if _normalizar(p["palavra"]) not in _normalizar(original):
            erros.append(f"- coluna '{p['chave']}': esperava algo com '{p['palavra']}', "
                         f"veio '{_normalizar(original)[:60]}...'")
    if erros:
        raise ValueError("Cabeçalhos fora da ordem esperada:\n" + "\n".join(erros))

    df.columns = [p["chave"] for p in cfg.PERGUNTAS]
    return df


# ---------------------------------------------------------------------------
# 2. Limpeza
# ---------------------------------------------------------------------------
def limpar(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # Tira espaços nas pontas e transforma texto vazio em ausente (NaN)
    for col in df.columns:
        df[col] = df[col].str.strip().replace("", np.nan)

    # Guarda o carimbo original como identificador da resposta
    df.insert(0, "id_resposta", range(1, len(df) + 1))
    carimbo_original = df["carimbo"].copy()

    # Data e hora (o Forms exporta no formato "2026/10/27 3:34:05 PM GMT-3")
    df["carimbo"] = pd.to_datetime(
        df["carimbo"].str.replace(r"\s*GMT[+-]\d+", "", regex=True),
        format="%Y/%m/%d %I:%M:%S %p",
    )

    # Escalas numéricas
    for chave in ["autoav_pre", "autoav_pos", "impacto_vida"]:
        df[chave] = pd.to_numeric(df[chave], errors="coerce")

    # Respostas digitadas em "Outro" -> categoria oficial
    for chave, mapa in cfg.RECODIFICAR.items():
        df[chave] = df[chave].replace(mapa)

    # Comentário removido da parte pública (a pessoa continua na amostra)
    removidos = carimbo_original.isin(cfg.COMENTARIOS_REMOVIDOS.keys())
    df.loc[removidos, "mudaria"] = np.nan
    df["flag_comentario_removido"] = removidos

    return df


# ---------------------------------------------------------------------------
# 3. Variáveis derivadas
# ---------------------------------------------------------------------------
def _indice_memoria(linha: pd.Series) -> float:
    """
    Índice de memória do voto, de 0 a 10.
    Usa deputado federal, deputado estadual e senadores:
    lembra o nome = 2, vagamente = 1, não lembra = 0.
    Branco/nulo e voto só no partido não entram na conta.
    """
    pontos = [LEMBRA_PONTOS[v] for v in
              (linha["lembra_dep_federal"], linha["lembra_dep_estadual"], linha["lembra_senadores"])
              if v in LEMBRA_PONTOS]
    if not pontos:
        return np.nan
    return round(np.mean(pontos) / 2 * 10, 2)


def criar_derivadas(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    df["eh_votante"] = np.where(df["votou"].isin(VOTANTES), "Votou", "Não votou")
    df["grupo_idade"] = np.where(df["faixa_etaria"] == "16 a 24", "16 a 24", "25 ou mais")

    # Clarão: quanto a nota do próprio voto mudou depois de refletir
    df["clarao"] = df["autoav_pos"] - df["autoav_pre"]
    df["clarao_cat"] = pd.cut(
        df["clarao"], bins=[-np.inf, -0.5, 0.5, np.inf],
        labels=["Baixou a nota", "Manteve", "Subiu a nota"],
    ).astype("object")

    # Celular x candidato (compara as posições na mesma escala de tempo)
    ordem = {v: i for i, v in enumerate(cfg.TEMPO_PESQUISA)}
    cand = df["tempo_candidato"].map(ordem)
    cel = df["tempo_celular"].map(ordem)
    df["celular_x_candidato"] = np.select(
        [cel > cand, cel == cand, cand > cel],
        ["Pesquisou mais o celular", "Pesquisou igual", "Pesquisou mais o candidato"],
        default=None,
    )
    df.loc[cand.isna() | cel.isna(), "celular_x_candidato"] = np.nan

    df["indice_memoria"] = df.apply(_indice_memoria, axis=1)
    return df


# ---------------------------------------------------------------------------
# 4. Qualidade dos dados (sinaliza, não exclui ninguém)
# ---------------------------------------------------------------------------
def marcar_inconsistencias(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # Deputados são eleitos no 1º turno: quem votou só no 2º não votou para deputado
    df["flag_2turno_lembra_deputado"] = (
        (df["votou"] == "Votei só no 2º turno")
        & df["lembra_dep_federal"].isin(["Sim, lembro o nome", "Lembro vagamente"])
    )

    # Votou branco/nulo para deputado federal, mas diz ter pesquisado o candidato
    df["flag_branco_pesquisou"] = (
        (df["lembra_dep_federal"] == "Votei branco ou nulo")
        & df["tempo_candidato"].notna()
        & (df["tempo_candidato"] != "Nada")
    )

    flags = [c for c in df.columns if c.startswith("flag_")]
    df["tem_alerta"] = df[flags].any(axis=1)
    return df


def relatorio_qualidade(df: pd.DataFrame) -> dict:
    """Resumo usado no terminal e na seção de qualidade do site."""
    fora_das_opcoes = {}
    for p in cfg.PERGUNTAS:
        if p["tipo"] in ("nominal", "ordinal") and p["opcoes"]:
            validos = set(p["opcoes"])
            extra = df[p["chave"]].dropna()
            extra = extra[~extra.isin(validos)]
            if len(extra):
                fora_das_opcoes[p["chave"]] = extra.value_counts().to_dict()

    votantes = df["eh_votante"] == "Votou"
    return {
        "total": len(df),
        "votantes": int(votantes.sum()),
        "nao_votantes": int((~votantes).sum()),
        "periodo": (df["carimbo"].min(), df["carimbo"].max()),
        "comentarios_validos": int(df["mudaria"].notna().sum()),
        "comentarios_removidos": int(df["flag_comentario_removido"].sum()),
        # Quantas respostas caíram em categorias criadas pela recodificação
        "recodificados": {k: int(df[k].isin(set(v.values())).sum())
                          for k, v in cfg.RECODIFICAR.items()},
        "alerta_2turno_lembra_deputado": int(df["flag_2turno_lembra_deputado"].sum()),
        "alerta_branco_pesquisou": int(df["flag_branco_pesquisou"].sum()),
        "fora_das_opcoes": fora_das_opcoes,
        # Votantes que pularam alguma pergunta da seção deles (deveria ser 0)
        "votantes_com_vazio": int(df.loc[votantes, ["autoav_pre", "autoav_pos",
                                                    "lembra_dep_federal"]].isna().any(axis=1).sum()),
    }


# ---------------------------------------------------------------------------
# 5. Carregar a base limpa já com as categorias na ordem certa (usado pelo site)
# ---------------------------------------------------------------------------
def carregar_limpo(caminho: str = cfg.ARQUIVO_LIMPO) -> pd.DataFrame:
    df = pd.read_csv(caminho, parse_dates=["carimbo"])
    for p in cfg.TODAS:
        if p["tipo"] in ("nominal", "ordinal") and p["opcoes"] and p["chave"] in df:
            df[p["chave"]] = pd.Categorical(
                df[p["chave"]], categories=p["opcoes"], ordered=p["tipo"] == "ordinal"
            )
    return df


def preparar(caminho_bruto: str = cfg.ARQUIVO_BRUTO) -> pd.DataFrame:
    df = carregar_bruto(caminho_bruto)
    df = limpar(df)
    df = criar_derivadas(df)
    df = marcar_inconsistencias(df)
    return df


if __name__ == "__main__":
    entrada = sys.argv[1] if len(sys.argv) > 1 else cfg.ARQUIVO_BRUTO
    base = preparar(entrada)

    Path(cfg.ARQUIVO_LIMPO).parent.mkdir(parents=True, exist_ok=True)
    base.to_csv(cfg.ARQUIVO_LIMPO, index=False)

    r = relatorio_qualidade(base)
    print(f"Base limpa salva em {cfg.ARQUIVO_LIMPO}")
    print(f"Respostas: {r['total']} ({r['votantes']} votaram, {r['nao_votantes']} não votaram)")
    print(f"Período: {r['periodo'][0]:%d/%m/%Y} a {r['periodo'][1]:%d/%m/%Y}")
    print(f"Comentários válidos: {r['comentarios_validos']} | removidos: {r['comentarios_removidos']}")
    print(f"Alertas: só 2º turno mas lembra deputado = {r['alerta_2turno_lembra_deputado']}, "
          f"branco/nulo mas pesquisou candidato = {r['alerta_branco_pesquisou']}")
    print(f"Votantes com pergunta em branco: {r['votantes_com_vazio']}")
    if r["fora_das_opcoes"]:
        print("ATENÇÃO, valores fora das opções do config.py:", r["fora_das_opcoes"])
    else:
        print("Todas as respostas batem com as opções do config.py.")
