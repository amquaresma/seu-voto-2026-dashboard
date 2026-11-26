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

/* Urna ilustrativa (animação, não interativa) */
.urna-wrap { pointer-events: none; user-select: none; cursor: default; margin: 0.4rem 0 0; }
.urna-corpo {
  display: grid; grid-template-columns: 1.45fr 1fr; gap: 0.8rem; padding: 0.9rem;
  border-radius: 12px; border: 1px solid color-mix(in srgb, currentColor 18%, transparent);
  background: color-mix(in srgb, currentColor 7%, transparent);
  box-shadow: 0 1px 0 color-mix(in srgb, currentColor 10%, transparent) inset;
}
.urna-tela {
  background: #fbfbf8; color: #1c1f22; border-radius: 6px; padding: 0.75rem 0.8rem 0.6rem;
  border: 3px solid #3a3d42; font-size: 0.78rem; line-height: 1.3; display: flex; flex-direction: column;
  min-height: 11.5rem;
}
.tela-topo { font-size: 0.62rem; letter-spacing: 0.04em; opacity: 0.7; }
.tela-cargo { font-weight: 700; font-size: 0.95rem; margin: 0.15rem 0 0.7rem; }
.tela-linha { display: flex; align-items: center; gap: 0.5rem; margin: 0.25rem 0; }
.tela-rot { width: 3.2rem; flex: none; opacity: 0.8; }
.tela-digitos { display: flex; gap: 0.25rem; }
.tela-dig { position: relative; width: 1.45rem; height: 1.85rem; border: 1.5px solid #1c1f22;
            display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 1rem; }
.tela-dig i { font-style: normal; opacity: 0; }
.tela-dig.d1 i { animation: urna-d1 9s infinite; }
.tela-dig.d2 i { animation: urna-d2 9s infinite; }
.tela-dig.d3 i { animation: urna-d3 9s infinite; }
.tela-dig.d4 i { animation: urna-d4 9s infinite; }
.tela-dig.d1::after { content: ""; position: absolute; width: 1.5px; height: 1.1rem; background: #1c1f22;
                      animation: urna-cursor 9s infinite; }
.tela-nome { opacity: 0; font-style: italic; animation: urna-nome 9s infinite; }
.tela-rodape { margin-top: auto; padding-top: 0.5rem; border-top: 1px solid #1c1f2233; font-size: 0.6rem;
               opacity: 0; animation: urna-nome 9s infinite; }
.urna-teclado { display: grid; grid-template-columns: repeat(3, 1fr); gap: 0.3rem; align-content: center; }
.tecla { background: #2a2c30; color: #f2f2ee; border-radius: 4px; text-align: center; font-size: 0.8rem;
         font-weight: 600; padding: 0.28rem 0; }
.tecla.zero { grid-column: 2; }
.teclas-voto { grid-column: 1 / -1; display: grid; grid-template-columns: repeat(3, 1fr); gap: 0.3rem; margin-top: 0.3rem; }
.tecla-voto { border-radius: 4px; text-align: center; font-size: 0.46rem; font-weight: 700; padding: 0.45rem 0;
              color: #1c1f22; white-space: nowrap; overflow: hidden; }
.tecla-voto.branco { background: #fbfbf8; }
.tecla-voto.corrige { background: #f08a4b; animation: urna-aperta 9s infinite; }
.tecla-voto.confirma { background: #2fbf71; }
.urna-legenda { font-size: 0.78rem !important; opacity: 0.6; margin: 0.5rem 0 0 !important; text-align: right; }
@keyframes urna-d1 { 0%, 10% { opacity: 0; } 11%, 68% { opacity: 1; } 70%, 100% { opacity: 0; } }
@keyframes urna-d2 { 0%, 18% { opacity: 0; } 19%, 68% { opacity: 1; } 70%, 100% { opacity: 0; } }
@keyframes urna-d3 { 0%, 26% { opacity: 0; } 27%, 68% { opacity: 1; } 70%, 100% { opacity: 0; } }
@keyframes urna-d4 { 0%, 34% { opacity: 0; } 35%, 68% { opacity: 1; } 70%, 100% { opacity: 0; } }
@keyframes urna-nome { 0%, 42% { opacity: 0; } 46%, 68% { opacity: 1; } 70%, 100% { opacity: 0; } }
@keyframes urna-cursor { 0%, 4%, 8%, 74%, 82%, 90%, 98% { opacity: 1; } 2%, 6%, 10.9%, 78%, 86%, 94% { opacity: 0; }
                         11%, 72% { opacity: 0; } 100% { opacity: 1; } }
@keyframes urna-aperta { 0%, 58% { transform: none; filter: none; }
                         61%, 64% { transform: translateY(2px) scale(0.96); filter: brightness(0.82); }
                         67%, 100% { transform: none; filter: none; } }
@media (prefers-reduced-motion: reduce) {
  .tela-dig i, .tela-nome, .tela-rodape { animation: none; opacity: 1; }
  .tela-dig.d1::after, .tecla-voto.corrige { animation: none; }
  .tela-dig.d1::after { opacity: 0; }
}

/* Título principal */
h1.manchete {
  font-family: "Literata", Georgia, serif !important; font-weight: 600 !important;
  font-size: clamp(2.2rem, 5vw, 3.6rem) !important; line-height: 1.08 !important;
  max-width: 17ch; margin: 0.2rem 0 1.1rem 0 !important; padding: 0 !important;
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

/* Cabeçalho do Streamlit: some o fundo, fica só o menu de três pontos */
[data-testid="stHeader"] { background: transparent; height: 2.6rem; }
[data-testid="stDecoration"] { display: none; }
.block-container { padding-top: 1.2rem !important; }

/* Cabeçalho do site */
.st-key-cabecalho {
  padding: 0.4rem 0 0.9rem; margin-bottom: 2.2rem;
  border-bottom: 1px solid color-mix(in srgb, currentColor 14%, transparent);
}
.marca { display: flex; align-items: center; gap: 0.7rem; text-decoration: none !important; color: inherit !important; }
.marca svg { width: 2.1rem; height: 2.1rem; flex: none; }
.marca-nome { display: block; font-family: "Literata", Georgia, serif; font-weight: 600; font-size: 1.2rem; line-height: 1.1; }
.marca-sub { display: block; font-size: 0.78rem; opacity: 0.68; margin-top: 0.15rem; }
.st-key-cabecalho p { margin: 0 !important; }
.st-key-menu { gap: 0.15rem !important; }
.st-key-menu [data-testid="stPageLink"] a {
  padding: 0.4rem 0.75rem !important; border-radius: 999px; transition: background 0.15s;
}
.st-key-menu [data-testid="stPageLink"] p { font-size: 0.95rem !important; font-weight: 500 !important;
  text-decoration: none !important; white-space: nowrap; }
.st-key-menu [data-testid="stPageLink"] a:hover { background: color-mix(in srgb, currentColor 8%, transparent); }
.st-key-menu [data-testid="stPageLink"] a[aria-current="page"],
.st-key-menu [data-testid="stPageLink"] a.active {
  background: color-mix(in srgb, #2a78d6 16%, transparent);
}
.st-key-menu [data-testid="stPageLink"] a[aria-current="page"] p { font-weight: 700 !important; }
@media (max-width: 860px) {
  .st-key-cabecalho { flex-direction: column !important; align-items: flex-start !important; gap: 0.6rem !important; }
  .st-key-menu { width: 100% !important; flex-wrap: nowrap !important; overflow-x: auto;
                 scrollbar-width: none; margin: 0 -0.2rem; }
  .st-key-menu::-webkit-scrollbar { display: none; }
}

/* Laboratório: blocos de medida */
.medidas { display: grid; grid-template-columns: repeat(auto-fill, minmax(165px, 1fr)); gap: 0.75rem; margin: 0.4rem 0 1.2rem; }
.medida { padding: 0.85rem 1rem; border-radius: 6px;
          border: 1px solid color-mix(in srgb, currentColor 14%, transparent); }
.medida-nome { font-size: 0.8rem; opacity: 0.7; margin-bottom: 0.25rem; }
.medida-valor { font-size: 1.35rem; font-weight: 600; line-height: 1.25; font-variant-numeric: tabular-nums;
                overflow-wrap: anywhere; }
.medida-valor.texto { font-size: 1rem; font-weight: 500; }
.ficha { display: flex; flex-wrap: wrap; gap: 0.5rem 1.6rem; font-size: 0.92rem; margin: 0.2rem 0 1rem; }
.ficha span { opacity: 0.68; margin-right: 0.35rem; }

/* Rodapé */
.rodape { margin-top: 5rem; padding: 2.2rem 0 0.5rem;
          border-top: 1px solid color-mix(in srgb, currentColor 18%, transparent); font-size: 0.92rem; }
.rodape-grade { display: grid; grid-template-columns: 1.6fr 1fr 1fr 1fr; gap: 2rem; }
.rodape h5 { font-size: 0.82rem !important; font-weight: 600 !important; opacity: 0.6; margin: 0 0 0.7rem !important;
             padding: 0 !important; font-family: inherit !important; }
.rodape ul { list-style: none; padding: 0 !important; margin: 0 !important; }
.rodape li { margin: 0 0 0.45rem !important; padding: 0 !important; }
.rodape a { color: inherit !important; text-decoration: none; opacity: 0.85; }
.rodape a:hover, .rodape a:focus-visible { opacity: 1; text-decoration: underline; }
.rodape-sobre p { margin: 0.6rem 0 0; opacity: 0.75; line-height: 1.55; max-width: 34ch; }
.rodape-redes a { display: inline-flex; align-items: center; gap: 0.45rem; }
.rodape-redes svg { width: 1rem; height: 1rem; fill: currentColor; }
.rodape-base { margin-top: 2rem; padding-top: 1rem; display: flex; flex-wrap: wrap; justify-content: space-between;
               gap: 0.6rem; font-size: 0.82rem; opacity: 0.62;
               border-top: 1px solid color-mix(in srgb, currentColor 10%, transparent); }
@media (max-width: 860px) { .rodape-grade { grid-template-columns: 1fr 1fr; } .rodape-sobre { grid-column: 1 / -1; } }
@media (max-width: 480px) { .rodape-grade { grid-template-columns: 1fr; } }
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


def urna(cargo: str = "Deputado federal"):
    """
    Ilustração animada da tela da urna: a pessoa tenta digitar o número, não lembra
    e aperta CORRIGE. Não é interativa (sem clique) e não usa número de partido real.
    """
    digitos = "".join(f'<span class="tela-dig d{i}"><i>?</i></span>' for i in range(1, 5))
    teclas = "".join(f'<span class="tecla">{n}</span>' for n in range(1, 10)) + '<span class="tecla zero">0</span>'
    html(f"""<div class="urna-wrap" aria-hidden="true">
<div class="urna-corpo">
<div class="urna-tela">
<div class="tela-topo">SEU VOTO PARA</div>
<div class="tela-cargo">{escape(cargo)}</div>
<div class="tela-linha"><span class="tela-rot">Número:</span><span class="tela-digitos">{digitos}</span></div>
<div class="tela-linha"><span class="tela-rot">Nome:</span><span class="tela-nome">não lembro...</span></div>
<div class="tela-rodape">Aperte a tecla CORRIGE para reiniciar este voto</div>
</div>
<div class="urna-teclado">{teclas}
<span class="teclas-voto"><span class="tecla-voto branco">BRANCO</span><span class="tecla-voto corrige">CORRIGE</span><span class="tecla-voto confirma">CONFIRMA</span></span>
</div>
</div>
</div>
<p class="urna-legenda">Animação ilustrativa, não é clicável.</p>""")


def barra_html(fracao: float) -> str:
    return f'<div class="barra"><span style="width:{max(0, min(1, fracao)) * 100:.1f}%"></span></div>'


# Marca: a urna estilizada (tela + teclas BRANCO, CORRIGE e CONFIRMA)
LOGO_SVG = """<svg viewBox="0 0 64 64" aria-hidden="true">
  <rect x="2" y="2" width="60" height="60" rx="14" fill="#2a5db0"/>
  <rect x="11" y="11" width="42" height="21" rx="4" fill="#ffffff"/>
  <rect x="16" y="16" width="7" height="11" rx="1.5" fill="none" stroke="#2a5db0" stroke-width="2"/>
  <rect x="25" y="16" width="7" height="11" rx="1.5" fill="none" stroke="#2a5db0" stroke-width="2"/>
  <rect x="34" y="16" width="7" height="11" rx="1.5" fill="none" stroke="#2a5db0" stroke-width="2"/>
  <rect x="11" y="39" width="12" height="13" rx="3" fill="#ffffff"/>
  <rect x="26" y="39" width="12" height="13" rx="3" fill="#f08a4b"/>
  <rect x="41" y="39" width="12" height="13" rx="3" fill="#2fbf71"/>
</svg>"""

ICONE_GITHUB = ('<svg viewBox="0 0 16 16" aria-hidden="true"><path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 '
                '5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13'
                '-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64'
                '-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 '
                '1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 '
                '3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.01 8.01 0 0 0 16 8c0-4.42-3.58-8-8-8z"/></svg>')
ICONE_LINKEDIN = ('<svg viewBox="0 0 16 16" aria-hidden="true"><path d="M0 1.15C0 .52.52 0 1.18 0h13.64C15.48 0 16 '
                  '.52 16 1.15v13.7c0 .63-.52 1.15-1.18 1.15H1.18C.52 16 0 15.48 0 14.85V1.15zM4.95 13.39V6.17H2.55v7.22h2.4z'
                  'M3.75 5.18c.84 0 1.36-.55 1.36-1.25-.02-.71-.52-1.25-1.34-1.25-.82 0-1.36.54-1.36 1.25 0 .7.52 1.25 1.33 '
                  '1.25h.01zm2.53 8.21h2.4V9.36c0-.22.02-.43.08-.59.17-.43.57-.88 1.23-.88.87 0 1.22.66 1.22 1.63v3.87h2.4V9.25'
                  'c0-2.22-1.18-3.25-2.77-3.25-1.28 0-1.84.7-2.16 1.2v.03h-.02l.02-.03V6.17h-2.4c.03.68 0 7.22 0 7.22z"/></svg>')


def favicon():
    """Ícone da aba: a mesma urna do logo, desenhada em alta resolução e reduzida."""
    from PIL import Image, ImageDraw
    k = 8                                    # desenha 8x maior para suavizar as bordas
    img = Image.new("RGBA", (64 * k, 64 * k), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    r = lambda x, y, w, h, raio, cor, borda=None: d.rounded_rectangle(
        [x * k, y * k, (x + w) * k, (y + h) * k], radius=raio * k, fill=cor,
        outline=borda, width=(2 * k if borda else 0))
    r(2, 2, 60, 60, 14, "#2a5db0")
    r(11, 11, 42, 21, 4, "#ffffff")
    for x in (16, 25, 34):
        r(x, 16, 7, 11, 1.5, None, "#2a5db0")
    r(11, 39, 12, 13, 3, "#ffffff")
    r(26, 39, 12, 13, 3, "#f08a4b")
    r(41, 39, 12, 13, 3, "#2fbf71")
    return img.resize((64, 64), Image.LANCZOS)


def cabecalho(paginas: list):
    """Nome do site à esquerda e menu de páginas à direita (vira uma linha rolável no celular)."""
    with st.container(key="cabecalho", horizontal=True, vertical_alignment="center",
                      horizontal_alignment="distribute"):
        html('<a class="marca" href="./" target="_self"><span><span class="marca-nome">Seu voto em 2026'
             '</span><span class="marca-sub">Pesquisa sobre memória e escolha do voto</span></span></a>')
        with st.container(key="menu", horizontal=True, width="content", vertical_alignment="center"):
            for p in paginas:
                st.page_link(p, label=p.title)


def rodape(paginas: list):
    links = "".join(f'<li><a href="./{p.url_path}" target="_self">{p.title}</a></li>' for p in paginas)
    html(f"""
<footer class="rodape">
  <div class="rodape-grade">
    <div class="rodape-sobre">
      <a class="marca" href="./" target="_self">{LOGO_SVG}<div class="marca-nome">Seu voto em 2026</div></a>
      <p>Pesquisa anônima e apartidária sobre como as pessoas escolhem e lembram o próprio voto.</p>
    </div>
    <div><h5>Páginas</h5><ul>{links}</ul></div>
    <div><h5>Projeto</h5><ul>
      <li>{DISCIPLINA}</li><li>{CURSO}</li>
      <li><a href="{REPOSITORIO}" target="_blank" rel="noopener">Código e dados</a></li></ul></div>
    <div class="rodape-redes"><h5>Contato</h5><ul>
      <li><a href="{GITHUB}" target="_blank" rel="noopener">{ICONE_GITHUB}GitHub</a></li>
      <li><a href="{LINKEDIN}" target="_blank" rel="noopener">{ICONE_LINKEDIN}LinkedIn</a></li></ul></div>
  </div>
  <div class="rodape-base">
    <span>© 2026 {AUTOR}</span>
    <span>Código sob licença MIT. Nenhum dado pessoal foi coletado.</span>
  </div>
</footer>""")
