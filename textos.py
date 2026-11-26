"""
Textos fixos do site. Para mudar uma frase, edite aqui: o código não precisa mudar.
Os números de cada seção são calculados no próprio dossiê, a partir dos dados.
"""

MANCHETE = "Poucas semanas depois da eleição, você lembra em quem votou?"

LINHA_FINA = (
    "Uma pesquisa anônima e apartidária sobre memória, informação e escolha "
    "nas Eleições 2026, com as respostas de {n} pessoas."
)

PRINCIPIOS = [
    ("Anônima",
     "O formulário não pediu nome, e-mail nem qualquer dado que identifique quem respondeu. "
     "Grupos com menos de 5 pessoas nunca são exibidos."),
    ("Apartidária",
     "Ninguém foi perguntado em quem votou, nem sobre partido. As perguntas tratam de como "
     "as pessoas escolhem e lembram, não de quem escolheram."),
    ("Aberta",
     "O código, a base tratada e cada decisão de limpeza estão públicos no GitHub. "
     "Todo número do site mostra de quantas respostas ele saiu."),
]

COMO_FOI_FEITO = [
    "As respostas foram coletadas por um formulário do Google entre {inicio} e {fim}, logo depois "
    "do segundo turno. O link circulou entre conhecidos, grupos de mensagens e redes sociais.",
    "Quem votou respondeu sobre a memória do próprio voto, como decidiu e o clima da campanha. "
    "Quem não votou respondeu sobre o motivo. No começo e no fim, cada pessoa deu uma nota de 0 a 10 "
    "para o próprio voto, o que permite medir se a reflexão mudou essa avaliação.",
    "A análise usa estatística descritiva: frequências, medidas de posição e de dispersão. "
    "Como a amostra é por conveniência, os resultados descrevem quem respondeu e **não representam "
    "o eleitorado brasileiro**.",
]

SECOES = {
    "memoria": dict(
        titulo="A memória do voto",
        intro="A eleição para o Legislativo acontece no primeiro turno e costuma ficar à sombra da "
              "disputa presidencial. A pergunta aqui é simples: o nome ainda está na memória?",
    ),
    "decisao": dict(
        titulo="Como a escolha foi feita",
        intro="Quanto tempo de pesquisa uma escolha que vale quatro anos recebe? Para dar uma referência, "
              "a mesma pergunta foi feita sobre a compra de um celular, com as mesmas opções de resposta.",
    ),
    "clima": dict(
        titulo="O clima da campanha",
        intro="Notícias falsas, conteúdo feito com inteligência artificial, bolhas nas redes e brigas "
              "entre pessoas próximas: o que cada pessoa disse ter vivido durante a campanha.",
    ),
    "antes_depois": dict(
        titulo="Antes e depois de pensar no assunto",
        intro="A mesma pergunta foi feita duas vezes, no início e no fim do formulário: de 0 a 10, "
              "o quanto o seu voto foi consciente e bem pesquisado?",
    ),
    "nao_votou": dict(
        titulo="Quem não votou",
        intro="Uma parte de quem respondeu não foi às urnas. Com poucas respostas, os números abaixo "
              "servem para descrever esse grupo, não para tirar conclusões sobre ele.",
    ),
    "mudaria": dict(
        titulo="O que as pessoas mudariam na política",
        intro="Pergunta aberta e opcional. As respostas aparecem como foram escritas, exceto uma, "
              "removida por conter discurso violento.",
    ),
}

LIMITACOES = [
    "A amostra é por conveniência: responde quem recebeu o link e quis participar. Por isso, ela tem "
    "mais jovens e mais pessoas com ensino superior do que o eleitorado.",
    "As respostas são autodeclaradas. Dizer que lembra o nome do candidato não é o mesmo que lembrar.",
    "Com poucas pessoas em alguns grupos, as diferenças entre eles podem ser fruto do acaso. "
    "Por isso cada número vem com a margem de erro.",
]

# Texto completo de cada pergunta, como apareceu no formulário
PERGUNTAS_COMPLETAS = {
    "faixa_etaria": "Qual sua faixa etária?",
    "escolaridade": "Qual sua escolaridade?",
    "fonte_info": "Durante a campanha, onde você mais se informou sobre a eleição?",
    "votou": "Você votou nas Eleições 2026?",
    "autoav_pre": "De 0 a 10, o quanto você acha que seu voto em 2026 foi consciente e bem pesquisado?",
    "lembra_dep_federal": "Você lembra o nome do(a) candidato(a) a deputado federal em quem votou?",
    "lembra_dep_estadual": "E do(a) candidato(a) a deputado estadual?",
    "lembra_senadores": "Em 2026, cada eleitor votou em dois senadores. Você lembra os nomes dos dois em quem votou?",
    "sabe_eleito_estadual": "Você sabe se o(a) seu(sua) candidato(a) a deputado estadual foi eleito(a)?",
    "sabe_eleito_federal": "Você sabe se o(a) seu(sua) candidato(a) a deputado federal foi eleito(a)?",
    "quando_decidiu": "Quando você decidiu seu voto para deputado federal?",
    "tempo_candidato": "Quanto tempo você pesquisou sobre seu candidato a deputado federal?",
    "tempo_celular": "E quanto tempo você pesquisa antes de comprar um celular novo?",
    "o_que_pesou": "O que mais pesou na sua escolha para deputado federal?",
    "voto_presidente": "Para presidente, seu voto foi mais...",
    "conhece_proposta": "Você conhece alguma proposta concreta do(a) seu(sua) candidato(a) a deputado federal?",
    "debate": "Você assistiu a algum debate presidencial completo?",
    "recebeu_fake": "Durante a campanha, você recebeu notícia falsa ou duvidosa sobre a eleição?",
    "compartilhou_sem_checar": "Você compartilhou algum conteúdo sobre a eleição sem checar se era verdade?",
    "briga": "A eleição causou briga ou afastamento entre você e alguém próximo?",
    "feed": "Durante a campanha, seu feed nas redes sociais mostrava...",
    "viu_ia": "Você viu algum vídeo, foto ou áudio sobre candidatos feito com inteligência artificial?",
    "autoav_pos": "Agora, olhando para trás: de 0 a 10, o quanto você considera seu voto consciente e bem pesquisado?",
    "motivo_nao_votou": "Qual o principal motivo de você não ter votado?",
    "impacto_vida": "O quanto as decisões dos eleitos afetam sua vida (preços, transporte, saúde, emprego)?",
    "vai_acompanhar": "Você pretende acompanhar o que os eleitos fazem nos próximos 4 anos?",
    "mudaria": "Se pudesse mudar uma coisa na política, o que seria?",
    # Variáveis criadas na análise
    "grupo_idade": "Grupo de idade (16 a 24 anos ou 25 anos ou mais)",
    "eh_votante": "Votou ou não votou",
    "clarao": "Diferença entre a nota do voto no fim e no início do formulário",
    "clarao_cat": "A nota do próprio voto mudou do início para o fim do formulário?",
    "celular_x_candidato": "Comparação entre o tempo pesquisando o candidato e o tempo pesquisando um celular",
    "indice_memoria": "Índice de memória do voto (0 a 10), a partir das lembranças de deputados e senadores",
}
