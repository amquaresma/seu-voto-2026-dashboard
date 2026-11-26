"""
Configuração central do projeto "Seu voto em 2026: o quanto você lembra?".

Tudo que descreve as perguntas fica aqui: código da coluna, texto curto para o
site, seção, tipo de variável e a ordem correta das opções. O resto do código
lê este arquivo, então para mudar um rótulo ou uma ordem basta editar aqui.

Tipos de variável (definem quais medidas estatísticas são válidas):
    "quantitativa" -> escala numérica 0 a 10 (média, desvio padrão etc.)
    "ordinal"      -> categorias com ordem (mediana, quartis, moda)
    "nominal"      -> categorias sem ordem (moda e frequências)
    "texto"        -> resposta aberta (análise de palavras)
    "data"         -> carimbo de data/hora
"""

# ---------------------------------------------------------------------------
# Arquivos
# ---------------------------------------------------------------------------
ARQUIVO_BRUTO = "data/bruto/respostas_forms.csv"   # CSV baixado do Forms (fica fora do Git)
ARQUIVO_LIMPO = "data/respostas_limpas.csv"        # gerado por preparar_dados.py (usado pelo site)

# Menor número de respostas para exibir um resultado filtrado
N_MINIMO = 5

# ---------------------------------------------------------------------------
# Escalas reutilizadas
# ---------------------------------------------------------------------------
LEMBRANCA = [
    "Sim, lembro o nome",
    "Lembro vagamente",
    "Não lembro",
    "Votei só no número do partido",
    "Votei branco ou nulo",
]
SABE_ELEITO = ["Sim, foi eleito(a)", "Sim, não foi eleito(a)", "Não sei", "Não se aplica"]
TEMPO_PESQUISA = ["Nada", "Menos de 30 minutos", "De 30 minutos a 2 horas", "Mais de 2 horas"]
ESCALA_0_10 = list(range(0, 11))

# ---------------------------------------------------------------------------
# Perguntas, na mesma ordem das colunas do CSV do Forms (28 colunas)
#   chave      -> nome da coluna no pandas
#   curto      -> rótulo usado nos gráficos e filtros
#   secao      -> página/seção do dossiê
#   tipo       -> ver docstring
#   opcoes     -> ordem oficial das categorias (None para numéricas/texto)
#   publico    -> "todos", "votantes" ou "nao_votantes" (quem viu a pergunta)
#   palavra    -> trecho que precisa existir no cabeçalho original (validação)
# ---------------------------------------------------------------------------
PERGUNTAS = [
    dict(chave="carimbo", curto="Data e hora da resposta", secao="Metodologia",
         tipo="data", opcoes=None, publico="todos", palavra="Carimbo"),

    # Seção 1: Quem é você
    dict(chave="faixa_etaria", curto="Faixa etária", secao="Perfil",
         tipo="ordinal", publico="todos", palavra="faixa etária",
         opcoes=["16 a 24", "25 a 34", "35 a 44", "45 a 59", "60 ou mais"]),
    dict(chave="escolaridade", curto="Escolaridade", secao="Perfil",
         tipo="ordinal", publico="todos", palavra="escolaridade",
         opcoes=["Até ensino fundamental", "Ensino médio", "Superior incompleto",
                 "Superior completo", "Pós-graduação"]),
    dict(chave="fonte_info", curto="Principal fonte de informação", secao="Perfil",
         tipo="nominal", publico="todos", palavra="MAIS se informou",
         opcoes=["Instagram ou TikTok", "X (Twitter)", "YouTube ou podcasts",
                 "WhatsApp ou Telegram", "TV ou rádio", "Sites e jornais",
                 "Conversando com pessoas", "Não me informei"]),
    dict(chave="votou", curto="Votou nas Eleições 2026", secao="Perfil",
         tipo="nominal", publico="todos", palavra="Você votou",
         opcoes=["Votei nos dois turnos", "Votei só no 1º turno",
                 "Votei só no 2º turno", "Não votei"]),

    # Seção 2: Antes de refletir
    dict(chave="autoav_pre", curto="Nota do próprio voto (antes)", secao="Antes x Depois",
         tipo="quantitativa", publico="votantes", palavra="acha que seu voto",
         opcoes=ESCALA_0_10),

    # Seção 3: Memória do voto
    dict(chave="lembra_dep_federal", curto="Lembra o deputado federal", secao="Memória do voto",
         tipo="nominal", publico="votantes", palavra="DEPUTADO FEDERAL", opcoes=LEMBRANCA),
    dict(chave="lembra_dep_estadual", curto="Lembra o deputado estadual", secao="Memória do voto",
         tipo="nominal", publico="votantes", palavra="DEPUTADO ESTADUAL", opcoes=LEMBRANCA),
    dict(chave="lembra_senadores", curto="Lembra os senadores", secao="Memória do voto",
         tipo="nominal", publico="votantes", palavra="senadores", opcoes=LEMBRANCA),
    dict(chave="sabe_eleito_estadual", curto="Sabe se o dep. estadual foi eleito", secao="Memória do voto",
         tipo="nominal", publico="votantes", palavra="deputado estadual foi eleito", opcoes=SABE_ELEITO),
    dict(chave="sabe_eleito_federal", curto="Sabe se o dep. federal foi eleito", secao="Memória do voto",
         tipo="nominal", publico="votantes", palavra="deputado federal foi eleito", opcoes=SABE_ELEITO),

    # Seção 4: Como você decidiu
    dict(chave="quando_decidiu", curto="Quando decidiu o voto (dep. federal)", secao="Como decidiu",
         tipo="ordinal", publico="votantes", palavra="Quando você decidiu",
         opcoes=["Mais de um mês antes", "No último mês", "Na última semana",
                 "No dia da eleição", "Na hora em frente à urna"]),
    dict(chave="tempo_candidato", curto="Tempo pesquisando o candidato", secao="Como decidiu",
         tipo="ordinal", publico="votantes", palavra="pesquisou sobre seu candidato",
         opcoes=TEMPO_PESQUISA),
    dict(chave="tempo_celular", curto="Tempo pesquisando um celular", secao="Como decidiu",
         tipo="ordinal", publico="votantes", palavra="celular", opcoes=TEMPO_PESQUISA),
    dict(chave="o_que_pesou", curto="O que mais pesou (dep. federal)", secao="Como decidiu",
         tipo="nominal", publico="votantes", palavra="MAIS pesou",
         opcoes=["Indicação de família ou amigos", "Propostas do candidato",
                 "Histórico do candidato", "Partido do candidato",
                 "Conteúdo nas redes sociais", "Propaganda ou santinho",
                 "Escolhi na hora", "Não votou para deputado / branco ou nulo"]),
    dict(chave="voto_presidente", curto="Voto para presidente foi mais...", secao="Como decidiu",
         tipo="nominal", publico="votantes", palavra="Para presidente",
         opcoes=["A FAVOR de quem eu escolhi", "CONTRA o outro candidato",
                 "Os dois na mesma medida", "Votei branco ou nulo"]),
    dict(chave="conhece_proposta", curto="Conhece proposta do dep. federal", secao="Como decidiu",
         tipo="nominal", publico="votantes", palavra="proposta concreta",
         opcoes=["Sim, sei explicar pelo menos uma", "Sei vagamente",
                 "Não conheço nenhuma", "Não se aplica"]),
    dict(chave="debate", curto="Assistiu a debate presidencial", secao="Como decidiu",
         tipo="nominal", publico="votantes", palavra="debate",
         opcoes=["Sim, mais de um", "Sim, um", "Só vi trechos ou cortes nas redes",
                 "Não assisti / não se aplica"]),

    # Seção 5: O clima da eleição
    dict(chave="recebeu_fake", curto="Recebeu notícia falsa ou duvidosa", secao="Clima da eleição",
         tipo="nominal", publico="votantes", palavra="notícia falsa",
         opcoes=["Sim, várias", "Sim, algumas", "Não", "Não sei identificar"]),
    dict(chave="compartilhou_sem_checar", curto="Compartilhou sem checar", secao="Clima da eleição",
         tipo="nominal", publico="votantes", palavra="sem checar",
         opcoes=["Sim", "Não", "Não lembro", "Não compartilhei nada"]),
    dict(chave="briga", curto="Briga ou afastamento", secao="Clima da eleição",
         tipo="nominal", publico="votantes", palavra="briga",
         opcoes=["Sim, me afastei de alguém", "Sim, briguei mas já passou", "Não"]),
    dict(chave="feed", curto="O que o feed mostrava", secao="Clima da eleição",
         tipo="nominal", publico="votantes", palavra="feed",
         opcoes=["Principalmente opiniões parecidas com a minha", "Opiniões dos dois lados",
                 "Principalmente opiniões contrárias à minha", "Não reparei",
                 "Não uso redes sociais"]),
    dict(chave="viu_ia", curto="Viu conteúdo feito com IA", secao="Clima da eleição",
         tipo="nominal", publico="votantes", palavra="inteligência artificial",
         opcoes=["Sim, e percebi na hora", "Sim, mas só descobri depois",
                 "Acho que não vi", "Não sei dizer"]),
    dict(chave="autoav_pos", curto="Nota do próprio voto (depois)", secao="Antes x Depois",
         tipo="quantitativa", publico="votantes", palavra="olhando para trás",
         opcoes=ESCALA_0_10),

    # Seção 6: Quem não votou
    dict(chave="motivo_nao_votou", curto="Motivo de não ter votado", secao="Quem não votou",
         tipo="nominal", publico="nao_votantes", palavra="não ter votado",
         opcoes=["Não estava na minha cidade", "Não tenho interesse",
                 "Acho que não muda nada", "Problema com título ou documentação",
                 "Trabalho ou compromisso", "Voto facultativo pela idade", "Outro motivo"]),

    # Seção 7: Para fechar
    dict(chave="impacto_vida", curto="Quanto a política afeta a vida (1 a 5)", secao="Para fechar",
         tipo="ordinal", publico="todos", palavra="afetam sua vida",
         opcoes=[1, 2, 3, 4, 5]),
    dict(chave="vai_acompanhar", curto="Vai acompanhar os eleitos", secao="Para fechar",
         tipo="ordinal", publico="todos", palavra="acompanhar",
         opcoes=["Não", "Talvez", "Sim"]),
    dict(chave="mudaria", curto="O que mudaria na política", secao="Para fechar",
         tipo="texto", opcoes=None, publico="todos", palavra="mudar uma coisa"),
]

# ---------------------------------------------------------------------------
# Recodificação das respostas digitadas em "Outro"
# (texto original, já sem espaços nas pontas -> categoria oficial)
# ---------------------------------------------------------------------------
RECODIFICAR = {
    "o_que_pesou": {
        "Votei branco": "Não votou para deputado / branco ou nulo",
        "Nenhum dos dois me representa": "Não votou para deputado / branco ou nulo",
        "não votei para deputados pois só votei no segundo turno":
            "Não votou para deputado / branco ou nulo",
    },
    "motivo_nao_votou": {
        "Idade não obrigatória.": "Voto facultativo pela idade",
    },
    # A opção "Não assisti" não existia no formulário publicado; quem marcou
    # "Não se aplica" na pergunta do debate é tratado como não tendo assistido.
    "debate": {
        "Não se aplica": "Não assisti / não se aplica",
    },
}

# Comentários removidos da parte pública (identificados pelo carimbo de data/hora,
# para o texto não ficar registrado no código). A pessoa continua na amostra.
COMENTARIOS_REMOVIDOS = {
    "2026/10/28 8:36:25 AM GMT-3": "discurso violento contra figura política",
}

# ---------------------------------------------------------------------------
# Variáveis derivadas criadas em preparar_dados.py
# ---------------------------------------------------------------------------
DERIVADAS = [
    dict(chave="grupo_idade", curto="Grupo de idade (16 a 24 x 25+)", secao="Perfil",
         tipo="nominal", publico="todos", opcoes=["16 a 24", "25 ou mais"]),
    dict(chave="eh_votante", curto="Votou (sim/não)", secao="Perfil",
         tipo="nominal", publico="todos", opcoes=["Votou", "Não votou"]),
    dict(chave="clarao", curto="Clarão (nota depois − nota antes)", secao="Antes x Depois",
         tipo="quantitativa", publico="votantes", opcoes=None),
    dict(chave="clarao_cat", curto="Mudança da nota", secao="Antes x Depois",
         tipo="ordinal", publico="votantes", opcoes=["Baixou a nota", "Manteve", "Subiu a nota"]),
    dict(chave="celular_x_candidato", curto="Celular x candidato", secao="Como decidiu",
         tipo="nominal", publico="votantes",
         opcoes=["Pesquisou mais o celular", "Pesquisou igual", "Pesquisou mais o candidato"]),
    dict(chave="indice_memoria", curto="Índice de memória do voto (0 a 10)", secao="Memória do voto",
         tipo="quantitativa", publico="votantes", opcoes=None),
]

# Atalhos usados pelo resto do código
TODAS = PERGUNTAS + DERIVADAS
POR_CHAVE = {p["chave"]: p for p in TODAS}
