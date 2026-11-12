"""Compila o relatório APS (Caps. 1–5 + pré-textuais) em DOCX conforme o manual UNIP."""

from __future__ import annotations

import re
from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Inches, Pt

ROOT = Path(__file__).resolve().parents[1]
REL = ROOT / "docs" / "relatorio"
FIG = ROOT / "docs" / "figuras"
OUT = ROOT / "docs" / "APS_Residuos_Reciclaveis_Letícia_Melo.docx"

INTEGRANTE = "Letícia Mateus Antunes de Melo"
ORIENTADOR = "Mario Quinello"
TITULO = (
    "Classificação e Segmentação de Resíduos Sólidos (Lixo Reciclável) "
    "para Automação de Coleta Seletiva"
)
TEMA_APS = (
    "Aplicação de técnicas de Processamento Digital de Imagens e Visão "
    "Computacional para resolver problemas de sustentabilidade ambiental"
)


def set_run_font(run, *, size=12, bold=False, italic=False) -> None:
    run.font.name = "Arial"
    run._element.rPr.rFonts.set(qn("w:eastAsia"), "Arial")
    run.font.size = Pt(size)
    run.bold = bold
    run.italic = italic


def style_paragraph(p, *, after=6, first_line=True, align=WD_ALIGN_PARAGRAPH.JUSTIFY) -> None:
    p.alignment = align
    pf = p.paragraph_format
    pf.line_spacing_rule = WD_LINE_SPACING.ONE_POINT_FIVE
    pf.space_after = Pt(after)
    pf.space_before = Pt(0)
    if first_line and align == WD_ALIGN_PARAGRAPH.JUSTIFY:
        pf.first_line_indent = Cm(1.25)


def add_page_number(section) -> None:
    footer = section.footer
    footer.is_linked_to_previous = False
    p = footer.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run()
    set_run_font(run, size=10)
    fld_char_begin = OxmlElement("w:fldChar")
    fld_char_begin.set(qn("w:fldCharType"), "begin")
    instr = OxmlElement("w:instrText")
    instr.set(qn("xml:space"), "preserve")
    instr.text = " PAGE "
    fld_char_end = OxmlElement("w:fldChar")
    fld_char_end.set(qn("w:fldCharType"), "end")
    run._r.append(fld_char_begin)
    run._r.append(instr)
    run._r.append(fld_char_end)


def configure_document(doc: Document) -> None:
    section = doc.sections[0]
    section.page_width = Cm(21.0)
    section.page_height = Cm(29.7)
    section.left_margin = Cm(2.5)
    section.right_margin = Cm(2.5)
    section.top_margin = Cm(2.5)
    section.bottom_margin = Cm(2.5)
    add_page_number(section)

    styles = doc.styles
    normal = styles["Normal"]
    normal.font.name = "Arial"
    normal._element.rPr.rFonts.set(qn("w:eastAsia"), "Arial")
    normal.font.size = Pt(12)
    normal.paragraph_format.line_spacing_rule = WD_LINE_SPACING.ONE_POINT_FIVE


def add_centered_lines(doc: Document, lines: list[tuple[str, int, bool]], space_after=8) -> None:
    for text, size, bold in lines:
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.line_spacing_rule = WD_LINE_SPACING.ONE_POINT_FIVE
        p.paragraph_format.space_after = Pt(space_after)
        run = p.add_run(text)
        set_run_font(run, size=size, bold=bold)


def add_page_break(doc: Document) -> None:
    doc.add_page_break()


def clean_md_inline(text: str) -> str:
    text = text.replace("\\(", "").replace("\\)", "")
    text = text.replace("\\[", "").replace("\\]", "")
    text = re.sub(r"\*\*(.+?)\*\*", r"\1", text)
    text = re.sub(r"\*(.+?)\*", r"\1", text)
    text = re.sub(r"`(.+?)`", r"\1", text)
    text = text.replace("——", "—")
    return text.strip()


def add_body_paragraph(doc: Document, text: str, *, first_line=True) -> None:
    text = clean_md_inline(text)
    if not text:
        return
    p = doc.add_paragraph()
    style_paragraph(p, first_line=first_line)
    # italic segments marked previously removed; keep simple
    run = p.add_run(text)
    set_run_font(run)


def add_heading_custom(doc: Document, text: str, level: int) -> None:
    text = clean_md_inline(text)
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p.paragraph_format.line_spacing_rule = WD_LINE_SPACING.ONE_POINT_FIVE
    p.paragraph_format.space_before = Pt(12 if level <= 2 else 8)
    p.paragraph_format.space_after = Pt(8)
    p.paragraph_format.first_line_indent = Cm(0)
    size = 12
    run = p.add_run(text.upper() if level == 1 else text)
    set_run_font(run, size=size, bold=True)


def add_bullet(doc: Document, text: str) -> None:
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.line_spacing_rule = WD_LINE_SPACING.ONE_POINT_FIVE
    p.paragraph_format.left_indent = Cm(1.0)
    p.paragraph_format.first_line_indent = Cm(0)
    p.paragraph_format.space_after = Pt(4)
    run = p.add_run("• " + clean_md_inline(text))
    set_run_font(run)


def add_equation_block(doc: Document, lines: list[str]) -> None:
    for line in lines:
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.line_spacing_rule = WD_LINE_SPACING.ONE_POINT_FIVE
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.first_line_indent = Cm(0)
        run = p.add_run(clean_md_inline(line))
        set_run_font(run, italic=True)


def add_table(doc: Document, headers: list[str], rows: list[list[str]]) -> None:
    table = doc.add_table(rows=1 + len(rows), cols=len(headers))
    table.style = "Table Grid"
    for i, h in enumerate(headers):
        cell = table.rows[0].cells[i]
        cell.text = ""
        p = cell.paragraphs[0]
        run = p.add_run(clean_md_inline(h))
        set_run_font(run, bold=True, size=11)
    for r_idx, row in enumerate(rows):
        for c_idx, val in enumerate(row):
            cell = table.rows[r_idx + 1].cells[c_idx]
            cell.text = ""
            p = cell.paragraphs[0]
            run = p.add_run(clean_md_inline(val))
            set_run_font(run, size=11)
    doc.add_paragraph()


def add_image(doc: Document, path: Path, caption: str) -> None:
    if not path.exists():
        return
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.first_line_indent = Cm(0)
    run = p.add_run()
    run.add_picture(str(path), width=Inches(5.8))
    cap = doc.add_paragraph()
    cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    cap.paragraph_format.space_after = Pt(10)
    cap.paragraph_format.first_line_indent = Cm(0)
    r = cap.add_run(caption)
    set_run_font(r, size=10, italic=True)


def parse_md_file(doc: Document, path: Path, *, skip_title=True) -> None:
    lines = path.read_text(encoding="utf-8").splitlines()
    i = 0
    in_eq = False
    eq_buf: list[str] = []
    table_buf: list[str] = []

    def flush_table() -> None:
        nonlocal table_buf
        if not table_buf:
            return
        rows_raw = [ln for ln in table_buf if not re.match(r"^\|?\s*-+", ln)]
        parsed = []
        for ln in rows_raw:
            cols = [c.strip() for c in ln.strip().strip("|").split("|")]
            parsed.append(cols)
        table_buf = []
        if len(parsed) >= 2:
            add_table(doc, parsed[0], parsed[1:])

    while i < len(lines):
        line = lines[i].rstrip()

        if line.strip().startswith("```"):
            # skip fenced code as indented body
            i += 1
            code_lines = []
            while i < len(lines) and not lines[i].strip().startswith("```"):
                code_lines.append(lines[i])
                i += 1
            for cl in code_lines:
                p = doc.add_paragraph()
                p.paragraph_format.left_indent = Cm(1.0)
                p.paragraph_format.first_line_indent = Cm(0)
                p.paragraph_format.line_spacing_rule = WD_LINE_SPACING.ONE_POINT_FIVE
                run = p.add_run(cl)
                set_run_font(run, size=10)
            i += 1
            continue

        if line.strip() == "$$" or line.strip().startswith("\\["):
            in_eq = True
            eq_buf = []
            i += 1
            continue
        if in_eq and (line.strip() == "$$" or line.strip().startswith("\\]")):
            add_equation_block(doc, eq_buf)
            in_eq = False
            eq_buf = []
            i += 1
            continue
        if in_eq:
            eq_buf.append(line)
            i += 1
            continue

        # display math single line \[...\] already split; also consecutive equation-looking lines starting with empty and \(
        if line.startswith("|") and "|" in line[1:]:
            table_buf.append(line)
            i += 1
            # peek
            while i < len(lines) and lines[i].startswith("|"):
                table_buf.append(lines[i].rstrip())
                i += 1
            flush_table()
            continue

        if not line.strip():
            i += 1
            continue
        if line.strip() == "---":
            i += 1
            continue
        if line.strip().startswith("> "):
            add_body_paragraph(doc, line.strip()[2:], first_line=False)
            i += 1
            continue

        if line.startswith("# "):
            if not skip_title:
                add_heading_custom(doc, line[2:], 1)
            i += 1
            continue
        if line.startswith("## "):
            add_heading_custom(doc, line[3:], 2)
            i += 1
            continue
        if line.startswith("### "):
            add_heading_custom(doc, line[4:], 3)
            i += 1
            continue
        if line.startswith("#### "):
            add_heading_custom(doc, line[5:], 4)
            i += 1
            continue

        if re.match(r"^[-*]\s+", line) or re.match(r"^\d+[.)]\s+", line) or re.match(r"^[a-f]\)\s+", line):
            text = re.sub(r"^[-*]\s+", "", line)
            text = re.sub(r"^\d+[.)]\s+", "", text)
            text = re.sub(r"^[a-f]\)\s+", "", text)
            add_bullet(doc, text)
            i += 1
            continue

        # skip identification blocks already on cover
        if line.startswith("**Identificação**") or line.startswith("**Nota"):
            # skip until blank
            i += 1
            while i < len(lines) and lines[i].strip() and not lines[i].startswith("#"):
                i += 1
            continue
        if line.startswith("**Formatação"):
            i += 1
            continue
        if line.startswith("Integrante:") or line.startswith("Orientador:") or line.startswith("Instituição:") or line.startswith("Curso:") or line.startswith("Disciplina:"):
            i += 1
            continue

        # equation-ish centered lines with many backslashes
        if "\\" in line and any(tok in line for tok in ["frac", "sigma", "omega", "mathrm", "in ", "rightarrow"]):
            add_equation_block(doc, [line])
            i += 1
            continue

        add_body_paragraph(doc, line)
        i += 1


def build_cover(doc: Document) -> None:
    for _ in range(2):
        doc.add_paragraph()
    add_centered_lines(
        doc,
        [
            ("UNIVERSIDADE PAULISTA — UNIP", 14, True),
            ("Instituto de Ciências Exatas e Tecnologia", 12, False),
            ("Curso de Ciência da Computação", 12, False),
        ],
        space_after=6,
    )
    for _ in range(4):
        doc.add_paragraph()
    add_centered_lines(
        doc,
        [
            (INTEGRANTE.upper(), 12, True),
        ],
    )
    for _ in range(4):
        doc.add_paragraph()
    add_centered_lines(
        doc,
        [
            (TITULO, 14, True),
        ],
        space_after=12,
    )
    for _ in range(6):
        doc.add_paragraph()
    add_centered_lines(
        doc,
        [
            ("Atividades Práticas Supervisionadas (APS)", 12, False),
            ("5º/6º semestre — Ciência da Computação", 12, False),
            ("Orientador: " + ORIENTADOR, 12, False),
        ],
    )
    for _ in range(6):
        doc.add_paragraph()
    add_centered_lines(doc, [("2026", 12, False)])


def build_rosto(doc: Document) -> None:
    add_centered_lines(doc, [(INTEGRANTE.upper(), 12, True)])
    for _ in range(3):
        doc.add_paragraph()
    add_centered_lines(doc, [(TITULO, 14, True)], space_after=18)
    for _ in range(2):
        doc.add_paragraph()

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.left_indent = Cm(6)
    p.paragraph_format.line_spacing_rule = WD_LINE_SPACING.ONE_POINT_FIVE
    run = p.add_run(
        "Relatório acadêmico apresentado como requisito parcial para avaliação "
        "da disciplina Atividades Práticas Supervisionadas (APS) do curso de "
        "Ciência da Computação da Universidade Paulista — UNIP, sob orientação "
        f"do Prof. {ORIENTADOR}."
    )
    set_run_font(run, size=12)

    for _ in range(8):
        doc.add_paragraph()
    add_centered_lines(
        doc,
        [
            (f"Orientador: Prof. {ORIENTADOR}", 12, False),
            ("2026", 12, False),
        ],
    )


def build_resumo(doc: Document) -> None:
    add_heading_custom(doc, "RESUMO", 1)
    add_body_paragraph(
        doc,
        "Este trabalho apresenta o desenvolvimento de uma aplicação em Python para "
        "classificação e segmentação de resíduos sólidos recicláveis (garrafa PET, "
        "lata de alumínio e papelão), com vistas à automação da coleta seletiva. "
        "O sistema implementa um pipeline modular de Processamento Digital de Imagens "
        "com aquisição e redimensionamento, filtragem (Gaussiano e mediana), "
        "segmentação (Otsu e limiar adaptativo), operações morfológicas, extração de "
        "características geométricas e classificação por regras interpretáveis, "
        "exposto por interface Streamlit. Em dataset sintético de 36 imagens, a "
        "configuração Gaussiano+Otsu obteve acurácia de 88,89%. O relatório fundamenta "
        "teoricamente as escolhas metodológicas e propõe evolução para modelos "
        "supervisionados de Visão Computacional.",
    )
    p = doc.add_paragraph()
    style_paragraph(p, first_line=False)
    run = p.add_run("Palavras-chave: ")
    set_run_font(run, bold=True)
    run2 = p.add_run(
        "processamento digital de imagens; visão computacional; reciclagem; "
        "segmentação; OpenCV; sustentabilidade."
    )
    set_run_font(run2)


def build_sumario(doc: Document) -> None:
    add_heading_custom(doc, "SUMÁRIO", 1)
    items = [
        "1 INTRODUÇÃO",
        "1.1 Definição do problema",
        "1.2 Contexto ecológico e social",
        "1.3 Objetivos",
        "2 REFERENCIAL TEÓRICO",
        "2.1 Descrição formal do problema computacional",
        "2.2 Aquisição de imagens digitais",
        "2.3 Manipulação e representação de imagens",
        "2.4 Filtragem no domínio espacial",
        "2.5 Segmentação",
        "2.6 Operações morfológicas",
        "2.7 Extração de características e classificação",
        "2.8 Proposta teórica de modelo de Visão Computacional",
        "3 PROPOSTA DO PROJETO",
        "3.1 Solução baseada em Processamento Digital de Imagens",
        "3.2 Modelagem e algoritmos de inteligência adequados",
        "3.3 Síntese da proposta",
        "4 DESENVOLVIMENTO",
        "4.1 Ferramentas utilizadas",
        "4.2 Arquitetura do software",
        "4.3 Implementação das etapas do pipeline",
        "4.4 Metodologia de testes",
        "4.5 Resultados qualitativos (imagens antes/depois)",
        "4.6 Resultados quantitativos",
        "4.7 Discussão e limitações",
        "4.8 Interface de demonstração",
        "5 CONCLUSÃO",
        "REFERÊNCIAS",
        "APÊNDICE A — Código-fonte do programa desenvolvido",
        "ANEXO — Ficha de Atividades Práticas Supervisionadas",
    ]
    for item in items:
        p = doc.add_paragraph()
        p.paragraph_format.line_spacing_rule = WD_LINE_SPACING.ONE_POINT_FIVE
        p.paragraph_format.space_after = Pt(2)
        p.paragraph_format.first_line_indent = Cm(0)
        run = p.add_run(item)
        set_run_font(run)


def build_lista_figuras(doc: Document) -> None:
    add_heading_custom(doc, "LISTA DE FIGURAS", 1)
    figs = [
        "Figura 1 — Mosaico do pipeline para amostra sintética de PET",
        "Figura 2 — Mosaico do pipeline para amostra sintética de lata",
        "Figura 3 — Mosaico do pipeline para amostra sintética de papelão",
    ]
    for f in figs:
        p = doc.add_paragraph()
        p.paragraph_format.line_spacing_rule = WD_LINE_SPACING.ONE_POINT_FIVE
        run = p.add_run(f)
        set_run_font(run)


def insert_result_figures(doc: Document) -> None:
    add_heading_custom(doc, "4.5 Resultados qualitativos (imagens antes/depois) — figuras", 2)
    add_body_paragraph(
        doc,
        "As figuras a seguir foram geradas automaticamente pelo pipeline "
        "(configuração Gaussiano + Otsu) sobre o dataset sintético descrito na "
        "metodologia. Cada mosaico apresenta as etapas: original, filtrada, escala "
        "de cinza, binária, morfologia e contorno/classe.",
        first_line=True,
    )
    mapping = [
        (FIG / "PET_synth_pet_00.png", "Figura 1 — Pipeline em amostra sintética da classe PET."),
        (FIG / "Lata_synth_lata_00.png", "Figura 2 — Pipeline em amostra sintética da classe lata."),
        (FIG / "Papelao_synth_papelao_00.png", "Figura 3 — Pipeline em amostra sintética da classe papelão."),
    ]
    for path, cap in mapping:
        add_image(doc, path, cap)


def build_appendix(doc: Document) -> None:
    add_heading_custom(doc, "APÊNDICE A — Código-fonte do programa desenvolvido", 1)
    add_body_paragraph(
        doc,
        "O código-fonte completo do sistema encontra-se no repositório do projeto "
        "aps-residuos-reciclaveis, organizado de forma modular. A estrutura principal é:",
    )
    for item in [
        "src/residuos_aps/ — núcleo do pipeline (aquisição, filtragem, segmentação, morfologia, features, classificador);",
        "app/gui_streamlit.py — interface gráfica Streamlit;",
        "app/cli.py — interface de linha de comando;",
        "scripts/generate_synthetic_dataset.py e scripts/evaluate_dataset.py — geração e avaliação do dataset;",
        "tests/ — testes automatizados (pytest).",
    ]:
        add_bullet(doc, item)
    add_body_paragraph(
        doc,
        "Por economia de espaço tipográfico, o apêndice remete ao código versionado "
        "entregue juntamente com este relatório. Trechos relevantes das etapas de "
        "filtragem, segmentação e classificação foram discutidos no Capítulo 4.",
    )


def build_ficha(doc: Document) -> None:
    add_heading_custom(doc, "ANEXO — Ficha de Atividades Práticas Supervisionadas", 1)
    add_body_paragraph(
        doc,
        f"Tema: {TITULO}. Integrante: {INTEGRANTE}. Orientador: {ORIENTADOR}.",
        first_line=False,
    )
    headers = ["Etapa", "Atividade", "Situação"]
    rows = [
        ["1", "Escolha do problema e alinhamento ao edital APS", "Concluída"],
        ["2", "Arquitetura do software + GUI Streamlit", "Concluída"],
        ["3", "Redação do Capítulo 1 (Introdução)", "Concluída"],
        ["4", "Referencial teórico e Proposta (Caps. 2 e 3)", "Concluída"],
        ["5", "Dataset sintético, testes e Cap. 4", "Concluída (sintético)"],
        ["6", "Capítulo 5 (Conclusão)", "Concluída"],
        ["7", "Coleta de fotos reais e reavaliação", "Pendente"],
        ["8", "Apresentação em sala (10–15 min)", "Pendente"],
        ["9", "Postagem em trabalhosacademicos.unip.br", "Pendente"],
    ]
    add_table(doc, headers, rows)
    add_body_paragraph(
        doc,
        "Tema institucional da APS: " + TEMA_APS + ".",
        first_line=False,
    )


def main() -> int:
    doc = Document()
    configure_document(doc)

    build_cover(doc)
    add_page_break(doc)
    build_rosto(doc)
    add_page_break(doc)
    build_resumo(doc)
    add_page_break(doc)
    build_lista_figuras(doc)
    add_page_break(doc)
    build_sumario(doc)
    add_page_break(doc)

    # Chapters
    parse_md_file(doc, REL / "01_introducao.md")
    add_page_break(doc)
    parse_md_file(doc, REL / "02_referencial_teorico.md")
    add_page_break(doc)
    parse_md_file(doc, REL / "03_proposta.md")
    add_page_break(doc)
    parse_md_file(doc, REL / "04_desenvolvimento.md")
    insert_result_figures(doc)
    add_page_break(doc)
    parse_md_file(doc, REL / "05_conclusao.md")
    add_page_break(doc)

    # References — rewrite clean
    add_heading_custom(doc, "REFERÊNCIAS", 1)
    refs = [
        "BRASIL. Lei nº 12.305, de 2 de agosto de 2010. Institui a Política Nacional de Resíduos Sólidos. Diário Oficial da União: seção 1, Brasília, DF, 3 ago. 2010.",
        "GONZALEZ, R. C.; WOODS, R. E. Processamento digital de imagens. 3. ed. São Paulo: Pearson, 2010.",
        "OPENCV. OpenCV documentation. Disponível em: https://docs.opencv.org/. Acesso em: 12 nov. 2026.",
        "PEDRINI, H.; SCHWARTZ, W. R. Análise de imagens digitais: princípios, algoritmos e aplicações. São Paulo: Thomson Learning, 2008.",
        "SOLOMON, C.; BRECKON, T. Fundamentos de processamento digital de imagens: uma abordagem prática com exemplos em Matlab. Rio de Janeiro: LTC, 2013.",
    ]
    for ref in refs:
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p.paragraph_format.line_spacing_rule = WD_LINE_SPACING.ONE_POINT_FIVE
        p.paragraph_format.left_indent = Cm(0.75)
        p.paragraph_format.first_line_indent = Cm(-0.75)
        p.paragraph_format.space_after = Pt(8)
        run = p.add_run(ref)
        set_run_font(run)

    add_page_break(doc)
    build_appendix(doc)
    add_page_break(doc)
    build_ficha(doc)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    # Avoid OneDrive lock issues with accented names if needed — also save ASCII copy
    doc.save(str(OUT))
    alt = ROOT / "docs" / "APS_Residuos_Reciclaveis_Leticia_Melo.docx"
    if alt != OUT:
        doc.save(str(alt))
    print(f"DOCX gerado: {OUT}")
    print(f"Cópia: {alt}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
