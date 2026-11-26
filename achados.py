"""
Achados: transforma os dados em frases verificáveis.

Toda frase sai com a porcentagem, o "k de n" e a margem de erro (intervalo de
Wilson, 95%), para que ninguém precise confiar no texto sem ver o número.
"""
import math

import pandas as pd

import config as cfg
import estatisticas as est

# Achados escritos à mão: pergunta, respostas que contam e como a frase termina.
# "excluir" tira respostas do denominador (ex.: "Não se aplica").
CURADOS = [
    dict(id="celular", chave="celular_x_candidato", respostas=["Pesquisou mais o celular"],
         frase="pesquisam mais antes de comprar um celular do que pesquisaram o candidato a deputado federal em quem votaram"),
    dict(id="fake", chave="recebeu_fake", respostas=["Sim, várias", "Sim, algumas"],
         frase="receberam notícia falsa ou duvidosa sobre a eleição durante a campanha"),
    dict(id="briga", chave="briga", respostas=["Sim, me afastei de alguém", "Sim, briguei mas já passou"],
         frase="brigaram ou se afastaram de alguém próximo por causa da eleição"),
    dict(id="afastou", chave="briga", respostas=["Sim, me afastei de alguém"],
         frase="se afastaram de alguém próximo por causa da eleição"),
    dict(id="bolha", chave="feed", respostas=["Principalmente opiniões parecidas com a minha"],
         excluir=["Não uso redes sociais"],
         frase="viam no feed das redes sociais principalmente opiniões parecidas com as suas"),
    dict(id="decidiu_tarde", chave="quando_decidiu",
         respostas=["Na última semana", "No dia da eleição", "Na hora em frente à urna"],
         frase="só decidiram o voto para deputado federal na última semana, no dia da eleição ou diante da urna"),
    dict(id="proposta", chave="conhece_proposta", respostas=["Sei vagamente", "Não conheço nenhuma"],
         excluir=["Não se aplica"],
         frase="não sabem explicar com segurança nenhuma proposta do deputado federal em quem votaram"),
    dict(id="debate", chave="debate", respostas=["Só vi trechos ou cortes nas redes", "Não assisti / não se aplica"],
         frase="não assistiram a nenhum debate presidencial completo"),
    dict(id="cortes", chave="debate", respostas=["Só vi trechos ou cortes nas redes"],
         frase="acompanharam os debates presidenciais apenas por trechos e cortes nas redes"),
    dict(id="ia", chave="viu_ia", respostas=["Sim, e percebi na hora", "Sim, mas só descobri depois"],
         frase="viram vídeo, foto ou áudio de candidatos feito com inteligência artificial"),
    dict(id="nao_sabe_eleito", chave="sabe_eleito_federal", respostas=["Não sei"], excluir=["Não se aplica"],
         frase="não sabem se o deputado federal em quem votaram foi eleito"),
    dict(id="lembra_fed", chave="lembra_dep_federal", respostas=["Lembro vagamente", "Não lembro"],
         excluir=["Votei branco ou nulo", "Votei só no número do partido"],
         frase="não lembram com certeza o nome do deputado federal em quem votaram"),
    dict(id="nota10", chave="autoav_pre", respostas=[10],
         frase="deram nota 10 ao próprio voto antes de refletir sobre ele"),
    dict(id="baixou", chave="clarao_cat", respostas=["Baixou a nota"],
         frase="baixaram a nota do próprio voto depois de responder às perguntas"),
    dict(id="contra", chave="voto_presidente", respostas=["CONTRA o outro candidato"],
         excluir=["Votei branco ou nulo"],
         frase="votaram para presidente mais contra o outro candidato do que a favor do escolhido"),
    dict(id="sem_checar", chave="compartilhou_sem_checar", respostas=["Sim", "Não lembro"],
         excluir=["Não compartilhei nada"],
         frase="compartilharam conteúdo sobre a eleição sem checar, ou não lembram se checaram"),
    dict(id="impacto", chave="impacto_vida", respostas=[5],
         frase="dizem que as decisões dos eleitos afetam muito a sua vida"),
    dict(id="acompanhar", chave="vai_acompanhar", respostas=["Sim"],
         frase="pretendem acompanhar o que os eleitos fizerem nos próximos quatro anos"),
]
POR_ID = {a["id"]: a for a in CURADOS}


# ---------------------------------------------------------------------------
# Cálculo
# ---------------------------------------------------------------------------
def wilson(k: int, n: int, z: float = 1.96) -> tuple[float, float]:
    """Intervalo de confiança de Wilson para uma proporção (95% por padrão)."""
    if n == 0:
        return (0.0, 0.0)
    p = k / n
    den = 1 + z ** 2 / n
    centro = (p + z ** 2 / (2 * n)) / den
    margem = z * math.sqrt(p * (1 - p) / n + z ** 2 / (4 * n ** 2)) / den
    return (max(0.0, centro - margem), min(1.0, centro + margem))


def proporcao(df: pd.DataFrame, chave: str, respostas: list, excluir: list | None = None) -> dict:
    s = df[chave].dropna()
    if excluir:
        s = s[~s.isin(excluir)]
    n = len(s)
    k = int(s.isin(respostas).sum())
    lo, hi = wilson(k, n)
    return dict(k=k, n=n, p=k / n if n else 0.0, ic=(lo, hi), margem=(hi - lo) / 2)


# ---------------------------------------------------------------------------
# Texto
# ---------------------------------------------------------------------------
def pct(p: float) -> str:
    return f"{round(p * 100):d}%"


def descrever_recorte(filtros: dict) -> str:
    """Transforma os filtros em texto: 'as pessoas de 16 a 24 anos, com ensino médio'."""
    partes = []
    for chave, valores in filtros.items():
        if not valores:
            continue
        v = [str(x) for x in valores]
        if chave == "faixa_etaria":
            itens = [x.replace(" ou mais", " anos ou mais") if "ou mais" in x else f"{x} anos" for x in v]
            partes.append("de " + " ou de ".join(itens))
        elif chave == "grupo_idade":
            partes.append(" ou ".join("de 16 a 24 anos" if x == "16 a 24" else "de 25 anos ou mais" for x in v))
        elif chave == "escolaridade":
            partes.append("com " + " ou ".join(x[0].lower() + x[1:] for x in v))
        elif chave == "fonte_info":
            trechos = []
            for x in v:
                if x == "Não me informei":
                    trechos.append("que não se informaram sobre a eleição")
                elif x == "Conversando com pessoas":
                    trechos.append("que se informaram principalmente conversando com pessoas")
                else:
                    trechos.append(f"que se informaram principalmente por {x}")
            partes.append(" ou ".join(trechos))
        elif chave == "eh_votante":
            partes.append(" ou ".join("que votaram" if x == "Votou" else "que não votaram" for x in v))
    return "as pessoas " + ", ".join(partes) if partes else ""


def sujeito(chave: str) -> str:
    return "dos eleitores" if cfg.POR_CHAVE[chave]["publico"] == "votantes" else "das pessoas"


def frase(achado: dict, r: dict, recorte: str = "") -> str:
    """Frase final em HTML simples (com <strong> no número)."""
    if recorte:
        return f"Entre {recorte}, <strong>{pct(r['p'])}</strong> {achado['frase']}."
    return f"<strong>{pct(r['p'])}</strong> {sujeito(achado['chave'])} {achado['frase']}."


def frase_livre(chave: str, respostas: list, r: dict, recorte: str, texto_pergunta: str) -> str:
    """Frase para combinações que não estão na lista de curados."""
    lista = " ou ".join(f"“{x}”" for x in respostas)
    inicio = f"Entre {recorte}, " if recorte else ""
    return (f"{inicio}<strong>{pct(r['p'])}</strong> responderam {lista} "
            f"à pergunta “{texto_pergunta}”.")


def meta(r: dict) -> str:
    pontos = round(r["margem"] * 100)
    return (f"{r['k']} de {r['n']} respostas. Margem de erro de {pontos} pontos "
            f"para mais ou para menos (intervalo de {pct(r['ic'][0])} a {pct(r['ic'][1])}).")


def curado_para(chave: str, respostas: list) -> dict | None:
    alvo = {str(x) for x in respostas}
    for a in CURADOS:
        if a["chave"] == chave and {str(x) for x in a["respostas"]} == alvo:
            return a
    return None


def ranking(df: pd.DataFrame) -> list[dict]:
    """Todos os achados curados calculados no recorte, do maior para o menor."""
    linhas = []
    for a in CURADOS:
        r = proporcao(df, a["chave"], a["respostas"], a.get("excluir"))
        if r["n"] >= cfg.N_MINIMO:
            linhas.append({**a, **r})
    return sorted(linhas, key=lambda x: x["p"], reverse=True)


def por_grupo(df: pd.DataFrame, chave: str, respostas: list, excluir: list | None,
              grupo: str) -> pd.DataFrame:
    linhas = []
    cats = df[grupo].cat.categories if isinstance(df[grupo].dtype, pd.CategoricalDtype) else sorted(df[grupo].dropna().unique())
    for g in cats:
        r = proporcao(df[df[grupo] == g], chave, respostas, excluir)
        if r["n"] == 0:
            continue
        linhas.append(dict(grupo=str(g), **r, oculto=r["n"] < cfg.N_MINIMO))
    return pd.DataFrame(linhas)
