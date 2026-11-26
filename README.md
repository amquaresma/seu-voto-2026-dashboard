# Seu voto em 2026: o quanto você lembra?

Pesquisa anônima e apartidária sobre memória, informação e escolha nas Eleições 2026, com análise em Python e site em Streamlit.

Projeto da disciplina Ciência de Dados, Engenharia de Computação, Senac. Autor: Matheus Rodrigues Quaresma.

## Formulário

As respostas foram coletadas por este formulário do Google, entre 27/10 e 10/11/2026:
[https://forms.gle/euVqne67TD3kJBKo8](https://forms.gle/euVqne67TD3kJBKo8)

A coleta já foi encerrada. O link fica aqui para quem quiser ver as perguntas exatamente como foram feitas.

## Páginas do site

| Página | O que mostra |
|---|---|
| Dossiê | Como a pesquisa foi feita e os principais achados, com gráficos e margem de erro |
| Explorar achados | Monte frases com qualquer pergunta e recorte; ranking dos achados mais fortes |
| Laboratório | Medidas descritivas por tipo de variável, com fórmula e conta passo a passo |
| Análises | Antes x depois (Wilcoxon), correlação de Spearman, qui-quadrado e V de Cramér |
| Metodologia e dados | Questionário, tratamento, limitações e download da base tratada |

## Estrutura

```
app.py                      navegação e rodapé
paginas/                    uma página do site por arquivo
config.py                   perguntas, tipos de variável e recodificações
preparar_dados.py           limpeza, variáveis derivadas e alertas de qualidade
estatisticas.py             medidas descritivas, fórmulas e passo a passo
achados.py                  frases com porcentagem e margem de erro (Wilson, 95%)
avancado.py                 testes e correlações
graficos.py                 gráficos (tema claro e escuro)
estilo.py                   identidade visual e rodapé
textos.py                   textos do site (edite aqui sem mexer no código)
comum.py                    carregamento e filtros
.streamlit/config.toml      tema claro e escuro, fontes
data/respostas_limpas.csv   base tratada e anonimizada
data/bruto/                 CSV original do Forms (fora do Git)
```

## Como rodar

```bash
pip install -r requirements.txt
python preparar_dados.py     # só quando o CSV do Forms mudar
streamlit run app.py
```

## Decisões de tratamento

- Nenhuma resposta excluída (n = 56).
- 1 comentário da pergunta aberta removido por discurso violento; a pessoa continua na amostra.
- Respostas digitadas em "Outro" agrupadas na categoria correspondente.
- No debate, "Não se aplica" foi tratado como "não assistiu" (a opção "Não assisti" não existia no formulário).
- Inconsistências só são sinalizadas (colunas `flag_*`), nunca apagadas.
- Grupos com menos de 5 respostas nunca são exibidos.

## Licença

MIT.
