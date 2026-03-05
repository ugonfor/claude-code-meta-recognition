"""
Generate arXiv tech-report style PDF for v2 experiment.
Two-column layout, LaTeX-like formatting, embedded figures.
"""
import json
from pathlib import Path
from datetime import datetime

from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch, cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.colors import black, HexColor, white
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle,
    PageBreak, KeepTogether, Frame, PageTemplate, BaseDocTemplate,
    FrameBreak, NextPageTemplate
)
from reportlab.platypus.frames import Frame
from reportlab.platypus.doctemplate import PageTemplate
from reportlab.lib.fonts import addMapping

# Try to register Korean font
try:
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    pdfmetrics.registerFont(TTFont('Malgun', 'C:/Windows/Fonts/malgun.ttf'))
    pdfmetrics.registerFont(TTFont('Malgun-Bold', 'C:/Windows/Fonts/malgunbd.ttf'))
    addMapping('Malgun', 0, 0, 'Malgun')
    addMapping('Malgun', 1, 0, 'Malgun-Bold')
    BASE_FONT = 'Malgun'
    BOLD_FONT = 'Malgun-Bold'
except:
    BASE_FONT = 'Helvetica'
    BOLD_FONT = 'Helvetica-Bold'

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
FIGURES_DIR = PROJECT_ROOT / "figures" / "v2"
SUMMARY_PATH = PROJECT_ROOT / "data" / "processed" / "v2" / "summary_v2.json"
SCORES_PATH = PROJECT_ROOT / "data" / "processed" / "v2" / "scores_v2.json"
OUTPUT_PATH = PROJECT_ROOT / "report" / "v2" / "harness_meta_recognition_v2.pdf"

# Load data
with open(SUMMARY_PATH, 'r', encoding='utf-8') as f:
    summary = json.load(f)
with open(SCORES_PATH, 'r', encoding='utf-8') as f:
    scores = json.load(f)

# Page dimensions
PAGE_W, PAGE_H = letter  # 8.5 x 11 inches
MARGIN = 0.75 * inch
COL_GAP = 0.3 * inch
COL_W = (PAGE_W - 2 * MARGIN - COL_GAP) / 2

# Colors
ACCENT = HexColor('#2c3e50')
LINK_COLOR = HexColor('#2980b9')


def get_styles():
    """Create arXiv-like paragraph styles."""
    styles = getSampleStyleSheet()

    # Title
    styles.add(ParagraphStyle(
        'ArxivTitle', fontName=BOLD_FONT, fontSize=16, leading=20,
        alignment=TA_CENTER, spaceAfter=6, textColor=black,
    ))
    # Authors
    styles.add(ParagraphStyle(
        'Authors', fontName=BASE_FONT, fontSize=10, leading=13,
        alignment=TA_CENTER, spaceAfter=4, textColor=HexColor('#555555'),
    ))
    # Abstract heading
    styles.add(ParagraphStyle(
        'AbstractHead', fontName=BOLD_FONT, fontSize=10, leading=12,
        alignment=TA_CENTER, spaceAfter=4,
    ))
    # Abstract body
    styles.add(ParagraphStyle(
        'AbstractBody', fontName=BASE_FONT, fontSize=9, leading=12,
        alignment=TA_JUSTIFY, leftIndent=30, rightIndent=30, spaceAfter=10,
    ))
    # Section heading
    styles.add(ParagraphStyle(
        'SectionHead', fontName=BOLD_FONT, fontSize=11, leading=14,
        spaceBefore=10, spaceAfter=4, textColor=ACCENT,
    ))
    # Subsection heading
    styles.add(ParagraphStyle(
        'SubsectionHead', fontName=BOLD_FONT, fontSize=9.5, leading=12,
        spaceBefore=6, spaceAfter=3, textColor=ACCENT,
    ))
    # Body text
    styles.add(ParagraphStyle(
        'Body', fontName=BASE_FONT, fontSize=9, leading=11.5,
        alignment=TA_JUSTIFY, spaceAfter=4,
    ))
    # Body bold
    styles.add(ParagraphStyle(
        'BodyBold', fontName=BOLD_FONT, fontSize=9, leading=11.5,
        alignment=TA_JUSTIFY, spaceAfter=4,
    ))
    # Caption
    styles.add(ParagraphStyle(
        'Caption', fontName=BASE_FONT, fontSize=8, leading=10,
        alignment=TA_CENTER, spaceAfter=6, textColor=HexColor('#444444'),
    ))
    # Table cell
    styles.add(ParagraphStyle(
        'TableCell', fontName=BASE_FONT, fontSize=7.5, leading=9,
        alignment=TA_CENTER,
    ))
    # Footnote
    styles.add(ParagraphStyle(
        'Footnote', fontName=BASE_FONT, fontSize=7, leading=9,
        textColor=HexColor('#666666'),
    ))
    return styles


def build_title_page(styles):
    """Build title, authors, abstract as single-column header."""
    elements = []

    # Title
    elements.append(Spacer(1, 0.3 * inch))
    elements.append(Paragraph(
        "Does Claude Know How Its Harness Looks Like?<br/>"
        "<font size=11>A Systematic Evaluation of LLM Self-Knowledge<br/>"
        "About Its Deployment Interface</font>",
        styles['ArxivTitle']
    ))
    elements.append(Spacer(1, 0.15 * inch))

    # Authors
    elements.append(Paragraph(
        "Hyogon Ryu<br/>"
        "<font size=8>KRAFTON Inc.</font>",
        styles['Authors']
    ))
    elements.append(Spacer(1, 0.05 * inch))
    elements.append(Paragraph(
        f"<font size=8>March 2026</font>",
        styles['Authors']
    ))
    elements.append(Spacer(1, 0.15 * inch))

    # Abstract
    elements.append(Paragraph("Abstract", styles['AbstractHead']))

    o = summary['overall']
    elements.append(Paragraph(
        f"We investigate whether large language models possess accurate knowledge about the visual "
        f"appearance of their deployment interface. Specifically, we test Claude (Sonnet 4.6) on its "
        f"knowledge of the Claude Code CLI — the terminal-based harness through which it is deployed. "
        f"We design 55 prompts spanning 10 mutually exclusive domains and 5 cognitive demand types "
        f"(free recall, forced choice, true/false, spatial reasoning, exact detail). "
        f"Our structured evaluation reveals <b>{o['objective_accuracy']*100:.1f}% objective accuracy</b> "
        f"on 28 forced-choice and true/false items, with an average confidence of {o['avg_confidence']:.3f} "
        f"and calibration error of {o['avg_calibration_error']:.3f}. "
        f"The model achieves perfect accuracy on negative knowledge probes (correctly identifying "
        f"non-existent features) but struggles with navigation shortcuts (33%) and recently-added features "
        f"like Vim mode and output styles. These results suggest LLMs have structured but incomplete "
        f"meta-knowledge of their deployment environment, with systematic blind spots in visual-only "
        f"and feature-specific details.",
        styles['AbstractBody']
    ))
    elements.append(Spacer(1, 0.1 * inch))

    # Keywords
    elements.append(Paragraph(
        "<b>Keywords:</b> LLM self-knowledge, meta-cognition, hallucination, "
        "Claude Code, deployment interface, confidence calibration",
        ParagraphStyle('KW', fontName=BASE_FONT, fontSize=8, leading=10,
                       alignment=TA_CENTER, textColor=HexColor('#666666'))
    ))
    elements.append(Spacer(1, 0.15 * inch))

    return elements


def build_section(num, title, content_paragraphs, styles):
    """Build a numbered section."""
    elements = []
    elements.append(Paragraph(f"{num}. {title}", styles['SectionHead']))
    elements.extend(content_paragraphs)
    return elements


def build_subsection(num, title, content_paragraphs, styles):
    """Build a numbered subsection."""
    elements = []
    elements.append(Paragraph(f"{num} {title}", styles['SubsectionHead']))
    elements.extend(content_paragraphs)
    return elements


def add_figure(fig_name, caption, styles, width=None):
    """Add a figure with caption."""
    elements = []
    fig_path = FIGURES_DIR / fig_name
    if fig_path.exists():
        w = width or COL_W
        img = Image(str(fig_path), width=w, height=w * 0.6)
        elements.append(img)
    elements.append(Paragraph(caption, styles['Caption']))
    elements.append(Spacer(1, 4))
    return elements


def build_results_table(styles):
    """Build main results table."""
    domains = [
        ("D1", "Startup Screen", "67%", "16", "0.52"),
        ("D2", "Input Area", "67%", "14", "0.58"),
        ("D3", "Output Display", "67%", "12", "0.77"),
        ("D4", "Permission Dialogs", "100%", "13", "0.67"),
        ("D5", "Status Line", "100%", "10", "0.43"),
        ("D6", "Navigation", "33%", "15", "0.37"),
        ("D7", "Theming", "100%", "9", "0.20"),
        ("D8", "Diff/Editing", "100%", "9", "0.50"),
        ("D9", "Error States", "100%", "8", "0.40"),
        ("D10", "Negative (Control)", "100%", "0", "0.94"),
    ]

    data = [["Domain", "Description", "Obj. Acc.", "Claims", "Avg Conf."]]
    for row in domains:
        data.append(list(row))

    # Add overall row
    o = summary['overall']
    data.append(["Overall", "—",
                 f"{o['objective_accuracy']*100:.1f}%",
                 str(o['claims_total']),
                 f"{o['avg_confidence']:.2f}"])

    t = Table(data, colWidths=[0.5*inch, 1.1*inch, 0.6*inch, 0.5*inch, 0.6*inch])
    t.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, 0), BOLD_FONT),
        ('FONTNAME', (0, 1), (-1, -2), BASE_FONT),
        ('FONTNAME', (0, -1), (-1, -1), BOLD_FONT),
        ('FONTSIZE', (0, 0), (-1, -1), 7.5),
        ('LEADING', (0, 0), (-1, -1), 9),
        ('ALIGN', (2, 0), (-1, -1), 'CENTER'),
        ('ALIGN', (0, 0), (1, -1), 'LEFT'),
        ('GRID', (0, 0), (-1, -1), 0.5, HexColor('#cccccc')),
        ('BACKGROUND', (0, 0), (-1, 0), HexColor('#ecf0f1')),
        ('BACKGROUND', (0, -1), (-1, -1), HexColor('#ecf0f1')),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
        # Color code accuracy
        ('TEXTCOLOR', (2, 4), (2, 4), HexColor('#27ae60')),  # D4 100%
        ('TEXTCOLOR', (2, 5), (2, 5), HexColor('#27ae60')),  # D5 100%
        ('TEXTCOLOR', (2, 6), (2, 6), HexColor('#e74c3c')),  # D6 33%
        ('TEXTCOLOR', (2, 7), (2, 7), HexColor('#27ae60')),  # D7 100%
        ('TEXTCOLOR', (2, 8), (2, 8), HexColor('#27ae60')),  # D8 100%
        ('TEXTCOLOR', (2, 9), (2, 9), HexColor('#27ae60')),  # D9 100%
        ('TEXTCOLOR', (2, 10), (2, 10), HexColor('#27ae60')), # D10 100%
    ]))
    return t


def build_wrong_answers_table(styles):
    """Build wrong answers detail table."""
    wrong = [
        ("P06", "D1", "T/F", "False", "True", "0.55",
         "Personalized greeting exists"),
        ("P13", "D2", "MC", "A", "D", "0.55",
         "All multiline methods work"),
        ("P19", "D3", "T/F", "False", "True", "0.80",
         "3 output styles exist"),
        ("P33", "D6", "T/F", "False", "True", "0.45",
         "Vim mode exists"),
        ("P36", "D6", "MC", "A(Ctrl+E)", "B(Ctrl+G)", "0.40",
         "External editor shortcut"),
    ]

    data = [["ID", "Dom.", "Type", "Given", "Expected", "Conf.", "Note"]]
    for row in wrong:
        data.append(list(row))

    t = Table(data, colWidths=[0.35*inch, 0.35*inch, 0.3*inch, 0.55*inch, 0.6*inch, 0.35*inch, 1.1*inch])
    t.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, 0), BOLD_FONT),
        ('FONTNAME', (0, 1), (-1, -1), BASE_FONT),
        ('FONTSIZE', (0, 0), (-1, -1), 6.5),
        ('LEADING', (0, 0), (-1, -1), 8),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('ALIGN', (-1, 0), (-1, -1), 'LEFT'),
        ('GRID', (0, 0), (-1, -1), 0.5, HexColor('#cccccc')),
        ('BACKGROUND', (0, 0), (-1, 0), HexColor('#ecf0f1')),
        ('TOPPADDING', (0, 0), (-1, -1), 1.5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 1.5),
        ('BACKGROUND', (3, 1), (3, -1), HexColor('#ffeaea')),
        ('BACKGROUND', (4, 1), (4, -1), HexColor('#eaffea')),
    ]))
    return t


def generate_report():
    styles = get_styles()
    S = styles

    # Use two-column template
    doc = BaseDocTemplate(
        str(OUTPUT_PATH),
        pagesize=letter,
        leftMargin=MARGIN, rightMargin=MARGIN,
        topMargin=MARGIN, bottomMargin=MARGIN,
    )

    # Single-column frame for title/abstract
    single_frame = Frame(
        MARGIN, MARGIN, PAGE_W - 2*MARGIN, PAGE_H - 2*MARGIN,
        id='single'
    )

    # Two-column frames
    left_frame = Frame(
        MARGIN, MARGIN, COL_W, PAGE_H - 2*MARGIN,
        id='left'
    )
    right_frame = Frame(
        MARGIN + COL_W + COL_GAP, MARGIN, COL_W, PAGE_H - 2*MARGIN,
        id='right'
    )

    # Full-width frame for figures
    full_frame = Frame(
        MARGIN, MARGIN, PAGE_W - 2*MARGIN, PAGE_H - 2*MARGIN,
        id='full'
    )

    title_template = PageTemplate(id='title', frames=[single_frame])
    two_col_template = PageTemplate(id='twocol', frames=[left_frame, right_frame])
    full_template = PageTemplate(id='full', frames=[full_frame])

    doc.addPageTemplates([title_template, two_col_template, full_template])

    story = []

    # ===== TITLE PAGE (single column) =====
    story.extend(build_title_page(S))
    story.append(NextPageTemplate('twocol'))
    story.append(PageBreak())

    # ===== 1. INTRODUCTION =====
    story.extend(build_section(1, "Introduction", [
        Paragraph(
            "Large language models (LLMs) are increasingly deployed through specialized "
            "interfaces — terminal CLIs, web applications, IDE integrations — that mediate "
            "the user experience. Yet we know little about whether these models possess "
            "accurate knowledge of the interfaces that host them. This question has "
            "practical implications: if an LLM can describe its own interface, it may "
            "better assist users with interface-related tasks; if it cannot, it risks "
            "confidently hallucinating visual details that mislead users.",
            S['Body']
        ),
        Paragraph(
            "We address the research question: <b>Does Claude know how its harness "
            "(Claude Code CLI) looks like?</b> We systematically evaluate Claude's "
            "knowledge across 10 interface domains using 55 carefully designed prompts "
            "spanning 5 cognitive demand types. This extends prior work on LLM "
            "self-knowledge by focusing specifically on <i>visual and spatial</i> "
            "knowledge of the deployment environment.",
            S['Body']
        ),
        Paragraph(
            "Our key contributions are: (1) a structured evaluation framework with "
            "MECE domain taxonomy and mixed prompt types; (2) a ground truth database "
            "of 74 verified facts about Claude Code; (3) empirical results showing "
            "82.1% objective accuracy with systematic blind spots in navigation and "
            "recently-added features; and (4) analysis of confidence calibration "
            "revealing appropriate uncertainty in knowledge gaps.",
            S['Body']
        ),
    ], S))

    # ===== 2. RELATED WORK =====
    story.extend(build_section(2, "Related Work", [
        Paragraph(
            "<b>LLM Self-Knowledge.</b> Prior studies have examined whether LLMs know "
            "their own capabilities, training data composition, and knowledge boundaries "
            "(Kadavath et al., 2022; Yin et al., 2023). Our work extends this to "
            "<i>deployment-context</i> knowledge — what the model knows about the "
            "interface wrapping it.",
            S['Body']
        ),
        Paragraph(
            "<b>Hallucination in Visual Descriptions.</b> LLMs frequently hallucinate "
            "visual details when asked to describe images or interfaces they have not "
            "seen (Ji et al., 2023). Our prompts are designed to detect such "
            "hallucinations through forced-choice items and negative probes.",
            S['Body']
        ),
        Paragraph(
            "<b>Confidence Calibration.</b> Well-calibrated models express appropriate "
            "uncertainty when they lack knowledge (Guo et al., 2017). We analyze "
            "per-item confidence alongside accuracy to assess calibration quality.",
            S['Body']
        ),
    ], S))

    # ===== 3. METHODOLOGY =====
    story.extend(build_section(3, "Methodology", [], S))

    story.extend(build_subsection("3.1", "Target Interface", [
        Paragraph(
            "Claude Code v2.1.66 is Anthropic's official terminal-based CLI for Claude. "
            "It features a rich text interface with Unicode box-drawing, two-column startup "
            "layout, permission dialogs, diff views, 6 color themes, and extensive keyboard "
            "shortcuts. It is built with Ink (React for CLI) and runs on macOS, Linux, "
            "and Windows.",
            S['Body']
        ),
    ], S))

    story.extend(build_subsection("3.2", "Domain Taxonomy", [
        Paragraph(
            "We organize interface knowledge into 10 mutually exclusive, collectively "
            "exhaustive (MECE) domains: D1 Startup/Welcome Screen, D2 Input Area, "
            "D3 Output Display, D4 Permission Dialogs, D5 Status Line, D6 Navigation, "
            "D7 Theming, D8 Diff/Editing, D9 Error States, and D10 Negative Space "
            "(features that do <i>not</i> exist, serving as a control condition).",
            S['Body']
        ),
    ], S))

    story.extend(build_subsection("3.3", "Cognitive Type Taxonomy", [
        Paragraph(
            "Each prompt employs one of five cognitive demand types: "
            "<b>T1 Free Recall</b> (open-ended 'describe X'); "
            "<b>T2 Forced Choice</b> (4-option multiple choice, 25% chance); "
            "<b>T3 True/False</b> (binary, 50% chance); "
            "<b>T4 Spatial Reasoning</b> ('what is above/below X'); "
            "<b>T5 Exact Detail</b> ('what exact character is used for Y'). "
            "This design controls for guessing by including prompt types with known "
            "chance baselines.",
            S['Body']
        ),
    ], S))

    story.extend(build_subsection("3.4", "Prompt Design", [
        Paragraph(
            "We designed 55 prompts (Table 1) covering all cells of the 10×5 domain-type "
            "matrix. Prompts include hallucination probes (e.g., P03 tests the known "
            "'CLAUDE CODE' ASCII banner hallucination), negative knowledge probes "
            "(D10 tests features that don't exist), and detail-accuracy probes "
            "(e.g., P09 tests the exact prompt character). All prompts enforce "
            "structured JSON output with per-claim confidence scores.",
            S['Body']
        ),
    ], S))

    story.extend(build_subsection("3.5", "Ground Truth", [
        Paragraph(
            "We compile a ground truth database of 74 verified facts from three sources: "
            "(1) <b>Screenshot analysis</b> of an actual Claude Code v2.1.66 startup screen, "
            "confirming visual elements like the two-column layout, ❯ prompt character, "
            "and small abstract logo; "
            "(2) <b>Official documentation</b> at code.claude.com covering 25 UI categories; "
            "(3) <b>Empirical session observation</b> including system prompt inspection and "
            "CLI help output. Each fact is tagged with source, domain, and confidence level.",
            S['Body']
        ),
    ], S))

    story.extend(build_subsection("3.6", "Evaluation Protocol", [
        Paragraph(
            "We evaluate Claude Sonnet 4.6 using subagent instances with explicit instructions "
            "to answer from training knowledge only (no tool use). Objective prompts (T2, T3) "
            "are scored by direct answer comparison against the GT database. Free-recall prompts "
            "(T1, T4, T5) are scored using keyword-based claim matching. Per-claim confidence "
            "enables calibration analysis.",
            S['Body']
        ),
    ], S))

    # ===== 4. RESULTS =====
    story.extend(build_section(4, "Results", [], S))

    story.extend(build_subsection("4.1", "Overall Performance", [
        Paragraph(
            f"Claude achieves <b>{summary['overall']['objective_accuracy']*100:.1f}% objective "
            f"accuracy</b> on 28 forced-choice and true/false items, substantially above both "
            f"T/F chance (50%) and 4-choice chance (25%). The model produced 106 atomic claims "
            f"in free-recall responses, with 86 verified correct and 20 unverifiable against "
            f"our GT database. Average stated confidence is {summary['overall']['avg_confidence']:.3f}, "
            f"with calibration error of {summary['overall']['avg_calibration_error']:.3f}.",
            S['Body']
        ),
    ], S))

    # Insert results table
    story.append(Spacer(1, 4))
    story.append(Paragraph("<b>Table 1.</b> Results by domain.", S['Caption']))
    story.append(build_results_table(S))
    story.append(Spacer(1, 6))

    story.extend(build_subsection("4.2", "Domain Analysis", [
        Paragraph(
            "<b>Strongest domains:</b> D10 (Negative Space, 100%), D4 (Permission, 100%), "
            "D5 (Status, 100%), D7 (Theming, 100%), D8 (Diff, 100%), D9 (Error, 100%). "
            "The model excels at both negative knowledge (knowing what <i>doesn't</i> exist) "
            "and functional knowledge about permission systems and diff views.",
            S['Body']
        ),
        Paragraph(
            "<b>Weakest domain:</b> D6 (Navigation, 33%) — below T/F chance. The model "
            "incorrectly denied the existence of Vim mode (/vim command), chose Ctrl+E "
            "instead of Ctrl+G for the external editor shortcut, and incorrectly guessed "
            "Ctrl+R for permission mode cycling (correct: Shift+Tab).",
            S['Body']
        ),
        Paragraph(
            "<b>Moderate domains:</b> D1 (Startup, 67%), D2 (Input, 67%), D3 (Output, 67%). "
            "The model correctly identified the two-column startup layout and ❯ prompt character "
            "but missed the personalized greeting, all multiline input methods, and the existence "
            "of three output styles.",
            S['Body']
        ),
    ], S))

    story.extend(build_subsection("4.3", "Error Analysis", [
        Paragraph(
            "Table 2 details all 5 wrong answers. A clear pattern emerges: the model "
            "lacks knowledge of <b>recently-added features</b> (Vim mode added ~2025, "
            "output styles, personalized greeting) and <b>specific keyboard shortcuts</b> "
            "(Ctrl+G vs Ctrl+E). Notably, wrong answers tend to have <i>lower</i> confidence "
            "(mean 0.55) than correct ones (mean 0.60), suggesting partial calibration.",
            S['Body']
        ),
    ], S))

    # Wrong answers table
    story.append(Spacer(1, 4))
    story.append(Paragraph("<b>Table 2.</b> Detailed wrong answers.", S['Caption']))
    story.append(build_wrong_answers_table(S))
    story.append(Spacer(1, 6))

    story.extend(build_subsection("4.4", "Confidence Calibration", [
        Paragraph(
            "The model shows meaningful but imperfect calibration. Average confidence for "
            "correct answers (0.60) exceeds that for incorrect ones (0.55), demonstrating "
            "some metacognitive awareness. However, the calibration error of 0.430 indicates "
            "systematic overconfidence on wrong answers and underconfidence on correct ones. "
            "The D10 (Negative Space) domain shows the best calibration with 0.94 average "
            "confidence on items answered correctly. The D7 (Theming) domain shows the poorest "
            "calibration: correct answers given with only 0.20 confidence.",
            S['Body']
        ),
    ], S))

    story.extend(build_subsection("4.5", "Cognitive Type Analysis", [
        Paragraph(
            "Forced-choice accuracy (84.6%, n=13) slightly exceeds true/false accuracy "
            "(80.0%, n=15), with both substantially above chance baselines. This suggests "
            "the model possesses genuine knowledge rather than randomly guessing, since "
            "forced-choice items have only 25% chance rate. Free-recall prompts yield "
            "the richest data — 51 claims from 9 prompts — but are harder to score "
            "automatically.",
            S['Body']
        ),
    ], S))

    # ===== 5. DISCUSSION =====
    story.extend(build_section(5, "Discussion", [], S))

    story.extend(build_subsection("5.1", "Knowledge Hierarchy", [
        Paragraph(
            "Our results reveal a clear <b>knowledge hierarchy</b>: "
            "(1) <i>Negative knowledge</i> — the model accurately knows what its interface "
            "is NOT (no sidebar, no avatars, no inline images); "
            "(2) <i>Structural knowledge</i> — general architecture (terminal-based, "
            "inline dialogs, diff coloring) is well-understood; "
            "(3) <i>Specific features</i> — recently-added or lesser-known features "
            "(Vim mode, output styles, personalized greeting) form blind spots. "
            "This hierarchy likely reflects training data coverage: older, more-documented "
            "features are better represented.",
            S['Body']
        ),
    ], S))

    story.extend(build_subsection("5.2", "Calibration Quality", [
        Paragraph(
            "The model demonstrates appropriate epistemic humility in uncertain domains "
            "(D7 Theming: 0.20 confidence, D6 Navigation: 0.37 confidence) while showing "
            "high confidence in well-known areas (D10 Negative: 0.94, D3 Output: 0.77). "
            "However, the 0.80 confidence on P19 (output styles, wrong answer) suggests "
            "calibration failures can occur when the model confuses absence of knowledge "
            "with confident disbelief.",
            S['Body']
        ),
    ], S))

    story.extend(build_subsection("5.3", "Implications", [
        Paragraph(
            "For <b>LLM deployment:</b> Models may confidently describe their interface "
            "incorrectly to users, particularly for features added after training data cutoff. "
            "For <b>user trust:</b> The 82% accuracy means roughly 1 in 5 interface-related "
            "claims may be wrong. For <b>model development:</b> Including deployment interface "
            "documentation in training data could improve self-knowledge accuracy.",
            S['Body']
        ),
    ], S))

    # ===== 6. LIMITATIONS =====
    story.extend(build_section(6, "Limitations", [
        Paragraph(
            "<b>Single trial:</b> Each prompt was evaluated once (N=1). Repeated trials "
            "would enable consistency analysis and more robust statistics. "
            "<b>Heuristic claim scoring:</b> Free-recall claims were scored using keyword "
            "matching rather than LLM-based judgment, likely underestimating both correct "
            "and incorrect claims. "
            "<b>Context contamination:</b> Subagents inherit the Claude Code system prompt, "
            "which contains information about available tools and platform details. This may "
            "inflate accuracy for prompts testable via system prompt inference. "
            "<b>Single model:</b> Only Sonnet 4.6 was tested; Opus and Haiku may differ. "
            "<b>Version specificity:</b> Results apply to Claude Code v2.1.66; newer versions "
            "may have different interfaces.",
            S['Body']
        ),
    ], S))

    # ===== 7. CONCLUSION =====
    story.extend(build_section(7, "Conclusion", [
        Paragraph(
            f"Claude demonstrates structured but incomplete knowledge of the Claude Code CLI, "
            f"achieving {summary['overall']['objective_accuracy']*100:.1f}% accuracy on "
            f"objective questions. The model excels at negative knowledge (100%) and "
            f"structural understanding, but has systematic blind spots in navigation shortcuts "
            f"and recently-added features. Confidence calibration shows meaningful but imperfect "
            f"metacognitive awareness. Future work should extend this evaluation to multiple "
            f"models, harness types (web UI, IDE plugins), and include repeated trials for "
            f"statistical robustness.",
            S['Body']
        ),
    ], S))

    # ===== FIGURES PAGE (full width) =====
    story.append(NextPageTemplate('full'))
    story.append(PageBreak())

    story.append(Paragraph("Appendix: Figures", S['SectionHead']))
    story.append(Spacer(1, 8))

    # Two figures per row
    fig_pairs = [
        ('fig1_domain_accuracy.png', 'Figure 1: Objective accuracy by domain.'),
        ('fig2_heatmap.png', 'Figure 2: Domain × Cognitive type accuracy heatmap.'),
        ('fig8_radar.png', 'Figure 3: Radar chart of domain performance.'),
        ('fig4_type_accuracy.png', 'Figure 4: Accuracy by cognitive type.'),
        ('fig5_confidence_dist.png', 'Figure 5: Confidence distribution (correct vs incorrect).'),
        ('fig3_calibration.png', 'Figure 6: Confidence calibration curve.'),
        ('fig7_wrong_answers.png', 'Figure 7: Wrong answers detail analysis.'),
        ('fig6_overall_summary.png', 'Figure 8: Overall results summary dashboard.'),
    ]

    full_w = PAGE_W - 2 * MARGIN
    for i in range(0, len(fig_pairs), 2):
        row_data = []
        for j in range(2):
            idx = i + j
            if idx < len(fig_pairs):
                fname, cap = fig_pairs[idx]
                fpath = FIGURES_DIR / fname
                if fpath.exists():
                    img = Image(str(fpath), width=full_w * 0.48, height=full_w * 0.30)
                    cell = [img, Paragraph(cap, S['Caption'])]
                else:
                    cell = [Paragraph(f"[{fname} not found]", S['Caption'])]
                row_data.append(cell)

        if len(row_data) == 2:
            t = Table([[row_data[0], row_data[1]]],
                      colWidths=[full_w * 0.5, full_w * 0.5])
            t.setStyle(TableStyle([
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('TOPPADDING', (0, 0), (-1, -1), 4),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ]))
            story.append(t)
        elif len(row_data) == 1:
            for elem in row_data[0]:
                story.append(elem)

        story.append(Spacer(1, 6))

    # Footer
    story.append(Spacer(1, 0.2*inch))
    story.append(Paragraph(
        "Code and data available at: "
        "https://github.com/ugonfor/claude-code-meta-recognition",
        ParagraphStyle('Footer', fontName=BASE_FONT, fontSize=8, leading=10,
                       alignment=TA_CENTER, textColor=LINK_COLOR)
    ))

    # Build
    doc.build(story)
    print(f"Report saved to {OUTPUT_PATH}")
    print(f"Size: {OUTPUT_PATH.stat().st_size / 1024:.0f} KB")


if __name__ == "__main__":
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    generate_report()
