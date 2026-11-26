"""
Identidade visual do site: CSS editorial, a "tela da urna" do topo e o rodapé.

As cores de borda e fundo usam currentColor, então funcionam nos dois temas
(claro e escuro) sem precisar saber qual está ativo.
"""
from html import escape

import streamlit as st

AUTOR = "Matheus Rodrigues Quaresma"
DISCIPLINA = "Projeto da disciplina Ciência de Dados"
CURSO = "Engenharia de Computação, Senac"
GITHUB = "https://github.com/amquaresma"
LINKEDIN = "https://www.linkedin.com/in/matheus-quaresma-/"
REPOSITORIO = "https://github.com/amquaresma/seu-voto-2026-dashboard"

CSS = """
<style>
/* Largura de leitura e respiro */
.block-container { max-width: 1060px; padding-top: 2.5rem; padding-bottom: 2rem; }
h1, h2, h3 { letter-spacing: -0.01em; }
h2 { margin-top: 2.6rem !important; }
[data-testid="stHeaderActionElements"] { display: none; }   /* ícone de link nos títulos */

/* Texto corrido */
.prosa { max-width: 66ch; }
.prosa p { font-size: 1.06rem !important; line-height: 1.65 !important; margin: 0 0 0.9rem 0 !important; }
p.nota { font-size: 0.88rem !important; opacity: 0.72; max-width: 70ch; line-height: 1.5 !important; }

/* Tela da urna */
.urna {
  margin: 0.5rem 0 2.2rem 0; padding: 1.3rem 1.5rem 1.4rem;
  border: 1px solid color-mix(in srgb, currentColor 22%, transparent);
  background: color-mix(in srgb, currentColor 4%, transparent);
  border-radius: 6px; max-width: 560px;
}
.urna-cargo { font-size: 1.05rem; font-weight: 600; margin-bottom: 1rem; }
.urna-linha { display: flex; align-items: center; gap: 1rem; margin: 0.4rem 0; font-size: 0.95rem; }
.urna-rotulo { width: 4.2rem; opacity: 0.75; }
.urna-digitos { display: flex; gap: 0.45rem; }
.urna-digito {
  width: 2.6rem; height: 3.3rem; border: 2px solid color-mix(in srgb, currentColor 55%, transparent);
  border-radius: 3px; display: flex; align-items: center; justify-content: center;
}
.urna-digito.ativo::after {
  content: ""; width: 2px; height: 1.7rem; background: currentColor;
  animation: piscar 1.1s steps(1) infinite;
}
.urna-nome { flex: 1; border-bottom: 2px solid color-mix(in srgb, currentColor 30%, transparent); height: 1.4rem; }
@keyframes piscar { 50% { opacity: 0; } }
@media (prefers-reduced-motion: reduce) { .urna-digito.ativo::after { animation: none; } }

/* Título principal */
h1.manchete {
  font-family: "Literata", Georgia, serif !important; font-weight: 600 !important;
  font-size: clamp(2.2rem, 5vw, 3.6rem) !important; line-height: 1.08 !important;
  max-width: 17ch; margin: 0 0 1.1rem 0 !important; padding: 0 !important;
}
p.linha-fina { font-size: 1.2rem !important; line-height: 1.55 !important; max-width: 52ch;
               opacity: 0.85; margin-bottom: 2.6rem !important; }

/* Achado principal: frase com o número dentro */
p.achado-principal {
  font-family: "Literata", Georgia, serif !important; font-size: clamp(1.45rem, 2.8vw, 2rem) !important;
  line-height: 1.35 !important; max-width: 32ch; margin: 0 0 0.7rem 0 !important;
  padding-left: 1.1rem; border-left: 3px solid #2a78d6;
}
.achado-principal strong { font-weight: 700; }

/* Princípios da pesquisa */
.principios { display: grid; grid-template-columns: repeat(3, 1fr); gap: 2rem; margin: 1rem 0 2.2rem; }
.principio h4 { font-family: "Literata", Georgia, serif !important; font-size: 1.2rem !important;
                font-weight: 600 !important; margin: 0 0 0.4rem 0 !important; padding: 0 !important; }
.principio p { font-size: 0.97rem !important; line-height: 1.55 !important; margin: 0 !important; opacity: 0.88; }
@media (max-width: 720px) { .principios { grid-template-columns: 1fr; gap: 1.2rem; } }

/* Lista de achados */
.achado { padding: 1rem 0; border-top: 1px solid color-mix(in srgb, currentColor 16%, transparent); }
.achado-frase { font-size: 1.08rem; line-height: 1.5; max-width: 62ch; font-family: "Literata", Georgia, serif; }
.achado-meta { font-size: 0.85rem; opacity: 0.7; margin-top: 0.3rem; }
.barra { height: 6px; border-radius: 3px; margin-top: 0.55rem; max-width: 420px;
         background: color-mix(in srgb, currentColor 12%, transparent); overflow: hidden; }
.barra > span { display: block; height: 100%; background: #2a78d6; }

/* Frase gerada no explorador */
p.frase-gerada {
  font-family: "Literata", Georgia, serif !important; font-size: clamp(1.3rem, 2.4vw, 1.75rem) !important;
  line-height: 1.4 !important; max-width: 40ch; padding: 1.2rem 0 0 1.1rem !important; margin: 0.6rem 0 0.6rem !important;
  border-left: 3px solid #2a78d6;
}

/* Comentários abertos */
.comentario { font-family: "Literata", Georgia, serif; font-size: 1.02rem; line-height: 1.5;
              padding: 0.7rem 0; border-top: 1px solid color-mix(in srgb, currentColor 12%, transparent);
              max-width: 62ch; }

/* Links para outras páginas */
[data-testid="stPageLink"] a { padding-left: 0 !important; }
[data-testid="stPageLink"] p { font-weight: 600 !important; text-decoration: underline;
                              text-underline-offset: 3px; font-size: 1rem !important; }

/* Rodapé */
.rodape { margin-top: 4.5rem; padding-top: 1.6rem;
          border-top: 1px solid color-mix(in srgb, currentColor 18%, transparent);
          display: flex; flex-wrap: wrap; justify-content: space-between; gap: 1.5rem; font-size: 0.92rem; }
.rodape-nome { font-weight: 600; font-size: 1rem; margin-bottom: 0.2rem; }
.rodape p { margin: 0.1rem 0; opacity: 0.8; }
.rodape-links { display: flex; gap: 1.4rem; align-items: flex-start; }
.rodape-links a { text-decoration: none; font-weight: 500; }
.rodape-links a:hover, .rodape-links a:focus-visible { text-decoration: underline; }
</style>
"""


def aplicar():
    st.markdown(CSS, unsafe_allow_html=True)


def html(conteudo: str):
    st.markdown(conteudo, unsafe_allow_html=True)


def prosa(*paragrafos: str):
    """Parágrafos de texto em coluna de leitura. Aceita **negrito** simples."""
    partes = []
    for p in paragrafos:
        p = escape(p)
        while "**" in p:
            p = p.replace("**", "<strong>", 1).replace("**", "</strong>", 1)
        partes.append(f"<p>{p}</p>")
    html(f'<div class="prosa">{"".join(partes)}</div>')


def nota(texto: str):
    html(f'<p class="nota">{escape(texto)}</p>')


def urna(cargo: str = "Deputado federal", digitos: int = 4):
    caixas = "".join(f'<div class="urna-digito{" ativo" if i == 0 else ""}"></div>' for i in range(digitos))
    html(f"""
<div class="urna" role="img" aria-label="Tela da urna eletrônica com o número do candidato em branco">
  <div class="urna-cargo">{escape(cargo)}</div>
  <div class="urna-linha"><span class="urna-rotulo">Número</span><div class="urna-digitos">{caixas}</div></div>
  <div class="urna-linha"><span class="urna-rotulo">Nome</span><div class="urna-nome"></div></div>
</div>""")


def barra_html(fracao: float) -> str:
    return f'<div class="barra"><span style="width:{max(0, min(1, fracao)) * 100:.1f}%"></span></div>'


def rodape():
    html(f"""
<footer class="rodape">
  <div>
    <div class="rodape-nome">{AUTOR}</div>
    <p>{DISCIPLINA}</p>
    <p>{CURSO}, 2026</p>
    <p>Código aberto sob licença MIT. Dados anonimizados.</p>
  </div>
  <nav class="rodape-links" aria-label="Contato e código">
    <a href="{GITHUB}" target="_blank" rel="noopener">GitHub</a>
    <a href="{LINKEDIN}" target="_blank" rel="noopener">LinkedIn</a>
    <a href="{REPOSITORIO}" target="_blank" rel="noopener">Código do projeto</a>
  </nav>
</footer>""")
