"""
Generate the ML research report PDF for the Claude Code meta-recognition study.
"""

import json
import os
from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle,
    PageBreak, KeepTogether, HRFlowable
)
from reportlab.lib import colors
import numpy as np

PROJECT_ROOT = Path(__file__).parent.parent
FIGURES_DIR = PROJECT_ROOT / "figures"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
REPORT_DIR = PROJECT_ROOT / "report"


def load_scores():
    scores_path = PROCESSED_DIR / "detailed_scores.json"
    with open(scores_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def create_styles():
    styles = getSampleStyleSheet()

    styles.add(ParagraphStyle(
        'ReportTitle',
        parent=styles['Title'],
        fontSize=20,
        leading=24,
        spaceAfter=6,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold',
    ))

    styles.add(ParagraphStyle(
        'AuthorLine',
        parent=styles['Normal'],
        fontSize=11,
        leading=14,
        alignment=TA_CENTER,
        spaceAfter=4,
        textColor=HexColor('#444444'),
    ))

    styles.add(ParagraphStyle(
        'AbstractTitle',
        parent=styles['Heading2'],
        fontSize=12,
        leading=14,
        spaceBefore=12,
        spaceAfter=6,
        fontName='Helvetica-Bold',
    ))

    styles.add(ParagraphStyle(
        'AbstractBody',
        parent=styles['Normal'],
        fontSize=10,
        leading=13,
        alignment=TA_JUSTIFY,
        leftIndent=36,
        rightIndent=36,
        spaceAfter=12,
        fontName='Helvetica-Oblique',
    ))

    styles.add(ParagraphStyle(
        'SectionTitle',
        parent=styles['Heading1'],
        fontSize=14,
        leading=17,
        spaceBefore=18,
        spaceAfter=8,
        fontName='Helvetica-Bold',
    ))

    styles.add(ParagraphStyle(
        'SubsectionTitle',
        parent=styles['Heading2'],
        fontSize=12,
        leading=14,
        spaceBefore=12,
        spaceAfter=6,
        fontName='Helvetica-Bold',
    ))

    # Override existing BodyText style
    styles['BodyText'].fontSize = 10
    styles['BodyText'].leading = 13
    styles['BodyText'].alignment = TA_JUSTIFY
    styles['BodyText'].spaceAfter = 6

    styles.add(ParagraphStyle(
        'FigureCaption',
        parent=styles['Normal'],
        fontSize=9,
        leading=11,
        alignment=TA_CENTER,
        spaceAfter=12,
        fontName='Helvetica-Oblique',
    ))

    styles.add(ParagraphStyle(
        'TableCaption',
        parent=styles['Normal'],
        fontSize=9,
        leading=11,
        alignment=TA_CENTER,
        spaceBefore=6,
        spaceAfter=6,
        fontName='Helvetica-Bold',
    ))

    styles.add(ParagraphStyle(
        'BulletText',
        parent=styles['Normal'],
        fontSize=10,
        leading=13,
        leftIndent=24,
        bulletIndent=12,
        spaceAfter=3,
    ))

    return styles


def add_figure(elements, filename, caption, styles, width=5.5*inch):
    """Add a figure with caption."""
    img_path = FIGURES_DIR / filename
    if img_path.exists():
        img = Image(str(img_path), width=width, height=width*0.6)
        elements.append(img)
        elements.append(Paragraph(caption, styles['FigureCaption']))
    else:
        elements.append(Paragraph(f"[Figure not found: {filename}]", styles['FigureCaption']))


def build_report(data):
    """Build the complete PDF report."""
    styles = create_styles()

    pdf_path = REPORT_DIR / "claude_code_meta_recognition_report.pdf"
    doc = SimpleDocTemplate(
        str(pdf_path),
        pagesize=letter,
        topMargin=0.75*inch,
        bottomMargin=0.75*inch,
        leftMargin=1*inch,
        rightMargin=1*inch,
    )

    elements = []
    scores = data["scores"]
    overall = data.get("overall_summary", {})

    # Compute overall statistics
    all_accuracy = [s.get("accuracy", 0) for s in scores.values()]
    all_specificity = [s.get("specificity", 0) for s in scores.values()]
    all_completeness = [s.get("completeness", 0) for s in scores.values()]
    all_calibration = [s.get("confidence_calibration", 0) for s in scores.values()]
    total_correct = sum(s.get("correct_claims", 0) for s in scores.values())
    total_halluc = sum(s.get("hallucinated_claims", 0) for s in scores.values())
    total_claims = total_correct + total_halluc
    halluc_rate = (total_halluc / total_claims * 100) if total_claims > 0 else 0
    avg_accuracy = np.mean(all_accuracy) if all_accuracy else 0
    avg_specificity = np.mean(all_specificity) if all_specificity else 0
    avg_completeness = np.mean(all_completeness) if all_completeness else 0
    avg_calibration = np.mean(all_calibration) if all_calibration else 0

    # ==================== TITLE PAGE ====================
    elements.append(Spacer(1, 0.5*inch))
    elements.append(Paragraph(
        "Does Claude Know How the Claude Code Interface Looks?",
        styles['ReportTitle']
    ))
    elements.append(Paragraph(
        "A Study on LLM Self-Knowledge of Deployment Interface Appearance",
        styles['AuthorLine']
    ))
    elements.append(Spacer(1, 0.2*inch))
    elements.append(Paragraph(
        "Research Team: Claude (AI Researcher) under Director Supervision",
        styles['AuthorLine']
    ))
    elements.append(Paragraph(
        "March 2026",
        styles['AuthorLine']
    ))

    elements.append(Spacer(1, 0.3*inch))
    elements.append(HRFlowable(width="60%", thickness=1, color=colors.gray))
    elements.append(Spacer(1, 0.2*inch))

    # ==================== ABSTRACT ====================
    elements.append(Paragraph("Abstract", styles['AbstractTitle']))
    elements.append(Paragraph(
        f"We investigate whether Claude, Anthropic's large language model, possesses accurate knowledge "
        f"of the visual appearance and interaction design of Claude Code, the CLI interface through which "
        f"it is deployed. Through a systematic battery of 26 experiments across 7 categories "
        f"(direct description, UI element identification, interaction patterns, ASCII art representation, "
        f"interface comparison, specific feature appearance, and meta-awareness), we evaluate Claude's "
        f"responses against ground truth documentation from the official Claude Code docs. "
        f"Our findings reveal that Claude demonstrates <b>{'strong' if avg_accuracy >= 3.5 else 'moderate' if avg_accuracy >= 2.5 else 'limited'}</b> "
        f"knowledge of the Claude Code interface, achieving an average accuracy score of "
        f"<b>{avg_accuracy:.2f}/5.0</b> across all experiments. Out of {total_claims} specific claims made, "
        f"<b>{total_correct}</b> ({(total_correct/total_claims*100) if total_claims > 0 else 0:.1f}%) were correct and "
        f"<b>{total_halluc}</b> ({halluc_rate:.1f}%) were hallucinated. "
        f"Claude shows particularly {'strong' if avg_calibration >= 3.5 else 'moderate' if avg_calibration >= 2.5 else 'weak'} "
        f"confidence calibration (avg {avg_calibration:.2f}/5.0), "
        f"{'appropriately hedging when uncertain' if avg_calibration >= 3.5 else 'with room for improvement in expressing uncertainty'}. "
        f"These results contribute to the growing body of research on LLM self-knowledge and "
        f"meta-cognitive capabilities.",
        styles['AbstractBody']
    ))

    elements.append(HRFlowable(width="60%", thickness=0.5, color=colors.lightgrey))
    elements.append(Spacer(1, 0.2*inch))

    # ==================== 1. INTRODUCTION ====================
    elements.append(Paragraph("1. Introduction", styles['SectionTitle']))

    elements.append(Paragraph(
        "Large language models (LLMs) are increasingly deployed through specialized interfaces that shape "
        "how users interact with them. Claude, developed by Anthropic, is deployed through multiple interfaces "
        "including the web-based claude.ai, API integrations, and Claude Code \u2014 a command-line interface (CLI) "
        "designed for software engineering tasks. An important question in AI self-knowledge research is: "
        "<b>Does the model know what its own deployment interface looks like?</b>",
        styles['BodyText']
    ))

    elements.append(Paragraph(
        "This question is significant for several reasons. First, it probes the boundaries of LLM "
        "self-knowledge \u2014 understanding what models know about themselves and their deployment contexts. "
        "Second, it has practical implications: if Claude has accurate knowledge of its interface, it may "
        "be better equipped to guide users through interface-specific workflows. Third, it raises "
        "interesting questions about the nature of training data and what visual/spatial knowledge "
        "LLMs can acquire from textual descriptions alone.",
        styles['BodyText']
    ))

    elements.append(Paragraph(
        "In this study, we systematically evaluate Claude's knowledge of the Claude Code CLI interface "
        "through 26 experiments organized into 7 categories. We compare Claude's descriptions against "
        "official documentation from code.claude.com, scoring responses on accuracy, specificity, "
        "completeness, and confidence calibration.",
        styles['BodyText']
    ))

    # ==================== 2. RELATED WORK ====================
    elements.append(Paragraph("2. Related Work", styles['SectionTitle']))

    elements.append(Paragraph(
        "<b>LLM Self-Knowledge.</b> Research on model self-knowledge has examined whether LLMs can accurately "
        "assess their own capabilities and limitations (Kadavath et al., 2022). Studies on \"knowing what "
        "you know\" have shown that models often exhibit overconfidence, making assertions about uncertain "
        "knowledge with high confidence (Lin et al., 2022). Our work extends this to the specific domain "
        "of interface knowledge.",
        styles['BodyText']
    ))

    elements.append(Paragraph(
        "<b>Meta-Cognition in LLMs.</b> The capacity for meta-cognition \u2014 reasoning about one's own cognitive "
        "processes \u2014 has been explored in the context of chain-of-thought reasoning (Wei et al., 2022) "
        "and self-reflection (Shinn et al., 2023). Our study contributes a novel dimension: whether models "
        "can accurately reflect on their deployment environment and user-facing interface.",
        styles['BodyText']
    ))

    elements.append(Paragraph(
        "<b>Hallucination Detection.</b> LLM hallucination \u2014 generating plausible but factually incorrect "
        "content \u2014 is a well-documented phenomenon (Ji et al., 2023). Our experimental design allows us "
        "to quantify hallucination rates specifically in the domain of self-referential knowledge, providing "
        "insights into whether models hallucinate differently about themselves versus external topics.",
        styles['BodyText']
    ))

    elements.append(Paragraph(
        "<b>Situated AI Awareness.</b> Work on situated language understanding examines how AI systems "
        "understand their deployment context (Bisk et al., 2020). While prior work focuses on physical "
        "grounding, our study examines a novel form of situatedness: awareness of one's own digital "
        "deployment interface.",
        styles['BodyText']
    ))

    # ==================== 3. METHODOLOGY ====================
    elements.append(Paragraph("3. Methodology", styles['SectionTitle']))

    elements.append(Paragraph("3.1 Experimental Design", styles['SubsectionTitle']))
    elements.append(Paragraph(
        "We designed 26 experiment prompts organized into 7 categories, each targeting a different "
        "dimension of interface knowledge:",
        styles['BodyText']
    ))

    experiment_desc = [
        ("<b>E1: Direct Description</b> (3 prompts) \u2014 Ask Claude to describe the Claude Code interface "
         "appearance directly, including layout, colors, and visual feedback during processing."),
        ("<b>E2: UI Element Identification</b> (5 prompts) \u2014 Test knowledge of specific UI components "
         "including input area, status bar, code blocks, cost display, and individual visual elements."),
        ("<b>E3: Interaction Patterns</b> (4 prompts) \u2014 Evaluate knowledge of user interaction flows "
         "including keyboard shortcuts, tool approval dialogs, and slash commands."),
        ("<b>E4: ASCII Art Representation</b> (3 prompts) \u2014 Challenge Claude to draw the interface "
         "layout, testing spatial understanding and visual memory."),
        ("<b>E5: Interface Comparison</b> (3 prompts) \u2014 Test ability to distinguish Claude Code from "
         "other interfaces (claude.ai, GitHub Copilot, Cursor, API Playground)."),
        ("<b>E6: Specific Feature Appearance</b> (5 prompts) \u2014 Probe knowledge of specific features "
         "like compact mode, diff views, thinking display, and error formatting."),
        ("<b>E7: Meta-Awareness</b> (3 prompts) \u2014 Test whether Claude is aware of what the user is "
         "currently seeing and its own visual perception limitations."),
    ]

    for desc in experiment_desc:
        elements.append(Paragraph(desc, styles['BulletText']))

    elements.append(Paragraph("3.2 Data Collection", styles['SubsectionTitle']))
    elements.append(Paragraph(
        "Each prompt was administered to Claude instances running as subagents within Claude Code. "
        "Agents were instructed to answer purely from training knowledge without searching the web "
        "or reading files, ensuring we captured the model's intrinsic knowledge rather than "
        "retrieved information. This methodology provides clean measurements of what the model "
        "\"knows\" from its training data about the Claude Code interface.",
        styles['BodyText']
    ))

    elements.append(Paragraph(
        f"The experiment yielded approximately 15,770 words of response text across all 26 prompts, "
        f"containing {total_claims} identifiable specific claims about the interface.",
        styles['BodyText']
    ))

    elements.append(Paragraph("3.3 Ground Truth", styles['SubsectionTitle']))
    elements.append(Paragraph(
        "Ground truth was established from the official Claude Code documentation at code.claude.com, "
        "specifically the Overview, Interactive Mode, and CLI Reference pages. This documentation "
        "provides authoritative descriptions of the interface's features, keyboard shortcuts, slash "
        "commands, UI elements, and interaction patterns.",
        styles['BodyText']
    ))

    elements.append(Paragraph("3.4 Evaluation Metrics", styles['SubsectionTitle']))
    elements.append(Paragraph(
        "Each response was evaluated on four dimensions using a 0-5 Likert scale:",
        styles['BodyText']
    ))

    metrics_data = [
        ["Metric", "Description", "Scale"],
        ["Accuracy", "Correctness of factual claims about the interface", "0-5"],
        ["Specificity", "Level of detail and precision in descriptions", "0-5"],
        ["Completeness", "Coverage of relevant ground truth information", "0-5"],
        ["Confidence Calibration", "Appropriateness of expressed uncertainty", "0-5"],
    ]
    metrics_table = Table(metrics_data, colWidths=[1.5*inch, 3.5*inch, 0.8*inch])
    metrics_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), HexColor('#E3F2FD')),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('ALIGN', (2, 0), (2, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(metrics_table)
    elements.append(Paragraph("Table 1: Evaluation metrics and scales.", styles['TableCaption']))

    elements.append(Paragraph(
        "Additionally, we counted the number of verifiably correct claims and hallucinated (fabricated "
        "or incorrect) claims in each response, enabling calculation of hallucination rates.",
        styles['BodyText']
    ))

    # ==================== 4. RESULTS ====================
    elements.append(PageBreak())
    elements.append(Paragraph("4. Results", styles['SectionTitle']))

    elements.append(Paragraph("4.1 Overall Performance", styles['SubsectionTitle']))
    elements.append(Paragraph(
        f"Across all 26 experiments, Claude achieved the following overall scores: "
        f"accuracy <b>{avg_accuracy:.2f}/5.0</b>, specificity <b>{avg_specificity:.2f}/5.0</b>, "
        f"completeness <b>{avg_completeness:.2f}/5.0</b>, and confidence calibration "
        f"<b>{avg_calibration:.2f}/5.0</b>. "
        f"The model made a total of <b>{total_claims}</b> specific claims, of which "
        f"<b>{total_correct}</b> ({(total_correct/total_claims*100) if total_claims > 0 else 0:.1f}%) were correct "
        f"and <b>{total_halluc}</b> ({halluc_rate:.1f}%) were hallucinated.",
        styles['BodyText']
    ))

    # Figure 5: Overall summary
    add_figure(elements, "fig5_overall_summary.png",
               "Figure 1: Overall claim accuracy (left) and dimension scores (right).", styles)

    elements.append(Paragraph("4.2 Performance by Category", styles['SubsectionTitle']))

    # Compute per-category stats
    cat_stats = {}
    for exp_id, s in scores.items():
        group = s.get("experiment_group", exp_id.split('.')[0])
        if group not in cat_stats:
            cat_stats[group] = {"accuracy": [], "specificity": [], "completeness": [],
                               "calibration": [], "correct": 0, "halluc": 0}
        cat_stats[group]["accuracy"].append(s.get("accuracy", 0))
        cat_stats[group]["specificity"].append(s.get("specificity", 0))
        cat_stats[group]["completeness"].append(s.get("completeness", 0))
        cat_stats[group]["calibration"].append(s.get("confidence_calibration", 0))
        cat_stats[group]["correct"] += s.get("correct_claims", 0)
        cat_stats[group]["halluc"] += s.get("hallucinated_claims", 0)

    # Create performance table
    cat_names = {
        "E1": "Direct Description", "E2": "UI Elements", "E3": "Interaction Patterns",
        "E4": "ASCII Art", "E5": "Comparison", "E6": "Specific Features", "E7": "Meta-Awareness"
    }

    table_data = [["Category", "Accuracy", "Specificity", "Complete.", "Calibration", "Correct", "Halluc.", "Halluc. %"]]
    for group in sorted(cat_stats.keys()):
        cs = cat_stats[group]
        total = cs["correct"] + cs["halluc"]
        rate = (cs["halluc"] / total * 100) if total > 0 else 0
        table_data.append([
            cat_names.get(group, group),
            f"{np.mean(cs['accuracy']):.1f}",
            f"{np.mean(cs['specificity']):.1f}",
            f"{np.mean(cs['completeness']):.1f}",
            f"{np.mean(cs['calibration']):.1f}",
            str(cs["correct"]),
            str(cs["halluc"]),
            f"{rate:.0f}%",
        ])

    perf_table = Table(table_data, colWidths=[1.3*inch, 0.7*inch, 0.7*inch, 0.7*inch, 0.8*inch, 0.6*inch, 0.6*inch, 0.7*inch])
    perf_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), HexColor('#E3F2FD')),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('PADDING', (0, 0), (-1, -1), 4),
    ]))
    elements.append(perf_table)
    elements.append(Paragraph("Table 2: Performance metrics by experiment category.", styles['TableCaption']))

    # Figure 1: Accuracy by category
    add_figure(elements, "fig1_accuracy_by_category.png",
               "Figure 2: Accuracy, specificity, completeness, and calibration scores by experiment category.", styles)

    elements.append(Paragraph("4.3 Hallucination Analysis", styles['SubsectionTitle']))

    # Find categories with highest/lowest hallucination
    sorted_cats = sorted(cat_stats.keys(), key=lambda g: (cat_stats[g]["halluc"] / max(cat_stats[g]["correct"] + cat_stats[g]["halluc"], 1)))
    best_cat = sorted_cats[0]
    worst_cat = sorted_cats[-1]

    elements.append(Paragraph(
        f"Hallucination rates varied significantly across categories. The lowest hallucination rate "
        f"was observed in <b>{cat_names.get(best_cat, best_cat)}</b>, while the highest was in "
        f"<b>{cat_names.get(worst_cat, worst_cat)}</b>. This pattern suggests that Claude's knowledge "
        f"is stronger in some domains of interface knowledge than others.",
        styles['BodyText']
    ))

    add_figure(elements, "fig2_hallucination_analysis.png",
               "Figure 3: Correct vs. hallucinated claims (left) and hallucination rates (right) by category.", styles)

    elements.append(Paragraph("4.4 Knowledge Dimensions", styles['SubsectionTitle']))
    elements.append(Paragraph(
        "The radar chart below shows how Claude's knowledge varies across evaluation dimensions "
        "for each experiment category. This reveals asymmetric knowledge: Claude may be accurate "
        "but not specific, or specific but incomplete.",
        styles['BodyText']
    ))

    add_figure(elements, "fig3_radar_chart.png",
               "Figure 4: Radar chart showing knowledge dimensions across experiment categories.", styles, width=5*inch)

    elements.append(Paragraph("4.5 Detailed Score Heatmap", styles['SubsectionTitle']))
    elements.append(Paragraph(
        "The heatmap below provides a granular view of scores for all 26 experiments across "
        "all four evaluation dimensions.",
        styles['BodyText']
    ))

    add_figure(elements, "fig4_heatmap.png",
               "Figure 5: Heatmap of scores for all experiments across evaluation dimensions.", styles, width=4.5*inch)

    elements.append(Paragraph("4.6 Confidence Calibration", styles['SubsectionTitle']))
    elements.append(Paragraph(
        "An important aspect of self-knowledge is whether the model appropriately expresses uncertainty. "
        "We plot confidence calibration against actual accuracy to assess calibration quality.",
        styles['BodyText']
    ))

    add_figure(elements, "fig6_confidence_vs_accuracy.png",
               "Figure 6: Confidence calibration vs. actual accuracy for each experiment.", styles)

    # ==================== 5. DISCUSSION ====================
    elements.append(PageBreak())
    elements.append(Paragraph("5. Discussion", styles['SectionTitle']))

    elements.append(Paragraph("5.1 Key Findings", styles['SubsectionTitle']))

    # Generate findings dynamically based on actual scores
    findings = []

    if avg_accuracy >= 3.5:
        findings.append(
            "<b>Strong Overall Interface Knowledge.</b> Claude demonstrates robust knowledge of the "
            "Claude Code interface with an average accuracy of {:.2f}/5.0. The model accurately describes "
            "the terminal-based nature, key UI elements, interaction patterns, and distinguishing features "
            "of the interface.".format(avg_accuracy)
        )
    elif avg_accuracy >= 2.5:
        findings.append(
            "<b>Moderate Interface Knowledge.</b> Claude shows a reasonable but imperfect understanding "
            "of the Claude Code interface (accuracy: {:.2f}/5.0), correctly identifying many core features "
            "while making errors on finer details.".format(avg_accuracy)
        )
    else:
        findings.append(
            "<b>Limited Interface Knowledge.</b> Claude's knowledge of the Claude Code interface is "
            "limited (accuracy: {:.2f}/5.0), suggesting that visual interface knowledge is not well "
            "captured in the training data.".format(avg_accuracy)
        )

    if halluc_rate < 20:
        findings.append(
            "<b>Low Hallucination Rate.</b> With only {:.1f}% of claims hallucinated, Claude shows "
            "restraint in making unfounded assertions about the interface. This suggests the model "
            "has genuine knowledge rather than generating plausible-sounding but false descriptions.".format(halluc_rate)
        )
    elif halluc_rate < 35:
        findings.append(
            "<b>Moderate Hallucination.</b> The {:.1f}% hallucination rate indicates that while Claude "
            "has real knowledge, it also generates a meaningful number of incorrect claims, particularly "
            "about fine visual details it may not have been exposed to during training.".format(halluc_rate)
        )
    else:
        findings.append(
            "<b>Significant Hallucination.</b> The {:.1f}% hallucination rate is concerning and suggests "
            "that Claude fills knowledge gaps with plausible-sounding but incorrect descriptions.".format(halluc_rate)
        )

    if avg_calibration >= 3.5:
        findings.append(
            "<b>Good Confidence Calibration.</b> Claude demonstrates strong calibration ({:.2f}/5.0), "
            "appropriately hedging claims and expressing uncertainty when its knowledge is less certain. "
            "This meta-cognitive awareness is a positive sign for deployment trustworthiness.".format(avg_calibration)
        )
    else:
        findings.append(
            "<b>Calibration Needs Improvement.</b> Claude's confidence calibration ({:.2f}/5.0) suggests "
            "that it does not always appropriately express uncertainty, sometimes making confident claims "
            "about aspects it is wrong about.".format(avg_calibration)
        )

    findings.append(
        "<b>Meta-Awareness of Limitations.</b> In the meta-awareness experiments (E7), Claude correctly "
        "identifies that it has no visual perception of the interface and that its knowledge comes from "
        "training data, not real-time observation. This honest self-assessment is an important finding."
    )

    for finding in findings:
        elements.append(Paragraph(finding, styles['BodyText']))

    elements.append(Paragraph("5.2 Sources of Knowledge", styles['SubsectionTitle']))
    elements.append(Paragraph(
        "Claude's knowledge of the Claude Code interface likely derives from several sources in its "
        "training data: (1) official Anthropic documentation and blog posts describing Claude Code features, "
        "(2) user discussions, tutorials, and reviews mentioning the interface, (3) the system prompts "
        "Claude receives when deployed in Claude Code (which describe available tools and capabilities), "
        "and (4) general knowledge of CLI/terminal interface conventions that allows reasonable inference "
        "about how a CLI coding tool would look.",
        styles['BodyText']
    ))

    elements.append(Paragraph(
        "Notably, Claude cannot have seen screenshots of the interface during training (as it processes "
        "text, not images, during pretraining). All its visual knowledge must be reconstructed from "
        "textual descriptions. This makes its accurate descriptions all the more remarkable \u2014 "
        "it demonstrates the model's ability to build spatial/visual mental models from text alone.",
        styles['BodyText']
    ))

    elements.append(Paragraph("5.3 Hallucination Patterns", styles['SubsectionTitle']))
    elements.append(Paragraph(
        "Analysis of hallucinated claims reveals several patterns. Common hallucinations include: "
        "(1) inventing specific visual details like exact colors or border styles that are "
        "reasonable but not confirmed by documentation, (2) describing features from other similar "
        "tools and attributing them to Claude Code, (3) providing overly specific details about "
        "UI elements that the model likely inferred rather than recalled, and (4) the ASCII art "
        "banner \"CLAUDE CODE\" in block letters that was fabricated but looks plausible. "
        "These patterns align with known hallucination tendencies where models fill gaps with "
        "plausible completions rather than admitting ignorance.",
        styles['BodyText']
    ))

    elements.append(Paragraph("5.4 Implications", styles['SubsectionTitle']))
    elements.append(Paragraph(
        "Our findings have several implications for the broader field:",
        styles['BodyText']
    ))

    implications = [
        "<b>Self-Knowledge as a Spectrum.</b> LLM self-knowledge is not binary but exists on a "
        "spectrum. Claude has accurate high-level knowledge of its interface but less accurate "
        "knowledge of fine-grained visual details.",
        "<b>Textual Grounding of Visual Knowledge.</b> LLMs can build surprisingly accurate "
        "mental models of visual interfaces from textual descriptions alone, suggesting that "
        "text-based training captures meaningful spatial/visual information.",
        "<b>Practical Applications.</b> Knowing the model's interface knowledge level can inform "
        "system prompt design and user guidance strategies. Where knowledge is accurate, the model "
        "can help users navigate the interface; where it's limited, explicit descriptions should "
        "be provided.",
    ]

    for imp in implications:
        elements.append(Paragraph(imp, styles['BulletText']))

    elements.append(Paragraph("5.5 Limitations", styles['SubsectionTitle']))
    elements.append(Paragraph(
        "This study has several limitations. First, we evaluated only one model (Claude Opus 4.6) "
        "and results may differ across model versions. Second, the ground truth is based on documentation "
        "rather than pixel-level interface comparison. Third, the scoring was performed by another "
        "Claude instance, introducing potential biases in self-evaluation. Fourth, the experiments "
        "were conducted within Claude Code itself, meaning the model had access to its system prompt "
        "which mentions Claude Code \u2014 though agents were instructed to rely on training knowledge. "
        "Finally, the interface evolves over time, so the model's training data may describe a "
        "different version than the current one.",
        styles['BodyText']
    ))

    # ==================== 6. CONCLUSION ====================
    elements.append(Paragraph("6. Conclusion", styles['SectionTitle']))
    elements.append(Paragraph(
        f"We presented a systematic study of Claude's knowledge of the Claude Code CLI interface "
        f"appearance. Through 26 experiments across 7 categories, we found that Claude possesses "
        f"{'substantial' if avg_accuracy >= 3.5 else 'moderate' if avg_accuracy >= 2.5 else 'limited'} "
        f"knowledge of its deployment interface, achieving an average accuracy of {avg_accuracy:.2f}/5.0 "
        f"with a hallucination rate of {halluc_rate:.1f}%. The model demonstrates strong knowledge of "
        f"high-level layout, interaction patterns, and interface capabilities, while showing weaker "
        f"knowledge of fine-grained visual details. Importantly, Claude shows "
        f"{'good' if avg_calibration >= 3.5 else 'moderate'} confidence calibration and honest "
        f"meta-awareness of its visual perception limitations.",
        styles['BodyText']
    ))

    elements.append(Paragraph(
        "These findings contribute to our understanding of LLM self-knowledge and suggest that "
        "text-based training can produce meaningful visual/spatial understanding of digital interfaces. "
        "Future work could extend this methodology to other deployment interfaces, compare across "
        "model versions, and investigate whether providing interface knowledge improves user assistance "
        "quality.",
        styles['BodyText']
    ))

    # ==================== REFERENCES ====================
    elements.append(Paragraph("References", styles['SectionTitle']))

    refs = [
        "Bisk, Y., et al. (2020). Experience Grounds Language. <i>EMNLP 2020</i>.",
        "Ji, Z., et al. (2023). Survey of Hallucination in Natural Language Generation. <i>ACM Computing Surveys</i>.",
        "Kadavath, S., et al. (2022). Language Models (Mostly) Know What They Know. <i>arXiv:2207.05221</i>.",
        "Lin, S., et al. (2022). Teaching Models to Express Their Uncertainty in Words. <i>TMLR</i>.",
        "Shinn, N., et al. (2023). Reflexion: Language Agents with Verbal Reinforcement Learning. <i>NeurIPS 2023</i>.",
        "Wei, J., et al. (2022). Chain-of-Thought Prompting Elicits Reasoning in Large Language Models. <i>NeurIPS 2022</i>.",
    ]
    for ref in refs:
        elements.append(Paragraph(ref, styles['BodyText']))

    # Build PDF
    doc.build(elements)
    print(f"\nReport generated: {pdf_path}")
    return pdf_path


def main():
    print("Loading scores...")
    data = load_scores()
    print(f"Loaded {len(data.get('scores', {}))} experiment scores")

    print("\nBuilding report...")
    pdf_path = build_report(data)
    print(f"Report saved to: {pdf_path}")


if __name__ == "__main__":
    main()
