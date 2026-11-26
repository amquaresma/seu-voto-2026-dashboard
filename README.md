# Seu voto em 2026: o quanto você lembra?

Projeto da disciplina de Ciência de Dados: pesquisa via Google Forms sobre as Eleições 2026 e site-dossiê em Streamlit.

## Estrutura

```
config.py                   perguntas, tipos de variável, ordem das opções e recodificações
preparar_dados.py           limpeza, variáveis derivadas e alertas de qualidade
app.py                      o site (Streamlit)
data/bruto/                 CSV original do Forms (fica fora do Git)
data/respostas_limpas.csv   base tratada que o site usa
```

## Como rodar

```bash
pip install -r requirements.txt
python preparar_dados.py     # só quando o CSV do Forms mudar
streamlit run app.py
```

## Decisões de tratamento

- Nenhuma resposta excluída (n = 56).
- 1 comentário da pergunta 26 removido por discurso violento; a pessoa continua na amostra.
- Respostas digitadas em "Outro" agrupadas na categoria correspondente (ver `RECODIFICAR` em `config.py`).
- No debate, "Não se aplica" foi tratado como "não assistiu" (a opção "Não assisti" não existia no formulário).
- Inconsistências só são sinalizadas (colunas `flag_*`), nunca apagadas.

## Variáveis derivadas

| Variável | O que é |
|---|---|
| `grupo_idade` | 16 a 24 x 25 ou mais (para comparar grupos com n suficiente) |
| `clarao` | nota do voto depois − nota antes |
| `celular_x_candidato` | pesquisou mais o celular, igual, ou mais o candidato |
| `indice_memoria` | 0 a 10, a partir das lembranças de dep. federal, estadual e senadores |
