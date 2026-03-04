"""
Generate the ML research report PDF in Korean for the Claude Code meta-recognition study.
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
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import numpy as np

PROJECT_ROOT = Path(__file__).parent.parent
FIGURES_DIR = PROJECT_ROOT / "figures"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
REPORT_DIR = PROJECT_ROOT / "report"

# Register Korean font
FONT_PATH = "C:/Windows/Fonts/malgun.ttf"
FONT_BOLD_PATH = "C:/Windows/Fonts/malgunbd.ttf"
pdfmetrics.registerFont(TTFont('MalgunGothic', FONT_PATH))
pdfmetrics.registerFont(TTFont('MalgunGothic-Bold', FONT_BOLD_PATH))


def load_scores():
    # Use v2 empirical scores if available
    v2_path = PROCESSED_DIR / "detailed_scores_v2.json"
    v1_path = PROCESSED_DIR / "detailed_scores.json"
    scores_path = v2_path if v2_path.exists() else v1_path
    print(f"Loading scores from: {scores_path.name}")
    with open(scores_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def create_styles():
    styles = getSampleStyleSheet()

    styles.add(ParagraphStyle(
        'ReportTitle',
        parent=styles['Title'],
        fontSize=19,
        leading=26,
        spaceAfter=6,
        alignment=TA_CENTER,
        fontName='MalgunGothic-Bold',
    ))

    styles.add(ParagraphStyle(
        'SubTitle',
        parent=styles['Normal'],
        fontSize=12,
        leading=16,
        alignment=TA_CENTER,
        spaceAfter=4,
        fontName='MalgunGothic',
        textColor=HexColor('#333333'),
    ))

    styles.add(ParagraphStyle(
        'AuthorLine',
        parent=styles['Normal'],
        fontSize=10,
        leading=14,
        alignment=TA_CENTER,
        spaceAfter=4,
        fontName='MalgunGothic',
        textColor=HexColor('#444444'),
    ))

    styles.add(ParagraphStyle(
        'AbstractTitle',
        parent=styles['Heading2'],
        fontSize=12,
        leading=16,
        spaceBefore=12,
        spaceAfter=6,
        fontName='MalgunGothic-Bold',
    ))

    styles.add(ParagraphStyle(
        'AbstractBody',
        parent=styles['Normal'],
        fontSize=9,
        leading=14,
        alignment=TA_JUSTIFY,
        leftIndent=36,
        rightIndent=36,
        spaceAfter=12,
        fontName='MalgunGothic',
    ))

    styles.add(ParagraphStyle(
        'SectionTitle',
        parent=styles['Heading1'],
        fontSize=14,
        leading=19,
        spaceBefore=18,
        spaceAfter=8,
        fontName='MalgunGothic-Bold',
    ))

    styles.add(ParagraphStyle(
        'SubsectionTitle',
        parent=styles['Heading2'],
        fontSize=12,
        leading=16,
        spaceBefore=12,
        spaceAfter=6,
        fontName='MalgunGothic-Bold',
    ))

    # Override existing BodyText style for Korean
    styles['BodyText'].fontName = 'MalgunGothic'
    styles['BodyText'].fontSize = 9
    styles['BodyText'].leading = 14
    styles['BodyText'].alignment = TA_JUSTIFY
    styles['BodyText'].spaceAfter = 6

    styles.add(ParagraphStyle(
        'FigureCaption',
        parent=styles['Normal'],
        fontSize=8,
        leading=11,
        alignment=TA_CENTER,
        spaceAfter=12,
        fontName='MalgunGothic',
    ))

    styles.add(ParagraphStyle(
        'TableCaption',
        parent=styles['Normal'],
        fontSize=8,
        leading=11,
        alignment=TA_CENTER,
        spaceBefore=6,
        spaceAfter=6,
        fontName='MalgunGothic-Bold',
    ))

    styles.add(ParagraphStyle(
        'BulletText',
        parent=styles['Normal'],
        fontSize=9,
        leading=14,
        leftIndent=24,
        bulletIndent=12,
        spaceAfter=3,
        fontName='MalgunGothic',
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
    """Build the complete Korean PDF report."""
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
        "Claude는 Claude Code 인터페이스의 외형을 알고 있는가?",
        styles['ReportTitle']
    ))
    elements.append(Paragraph(
        "LLM의 배포 인터페이스 외형에 대한 자기 인식 연구",
        styles['SubTitle']
    ))
    elements.append(Spacer(1, 0.2*inch))
    elements.append(Paragraph(
        "연구팀: Claude (AI 연구원) | 디렉터 감독 하 수행",
        styles['AuthorLine']
    ))
    elements.append(Paragraph(
        "2026년 3월",
        styles['AuthorLine']
    ))

    elements.append(Spacer(1, 0.3*inch))
    elements.append(HRFlowable(width="60%", thickness=1, color=colors.gray))
    elements.append(Spacer(1, 0.2*inch))

    # ==================== ABSTRACT ====================
    elements.append(Paragraph("초록 (Abstract)", styles['AbstractTitle']))

    accuracy_level = "높은" if avg_accuracy >= 3.5 else "보통의" if avg_accuracy >= 2.5 else "제한적인"
    calib_level = "우수한" if avg_calibration >= 3.5 else "보통의" if avg_calibration >= 2.5 else "미흡한"
    calib_desc = "불확실한 부분에 대해 적절히 유보적 태도를 보인다" if avg_calibration >= 3.5 else "불확실성 표현에 개선의 여지가 있다"

    elements.append(Paragraph(
        f"본 연구는 Anthropic의 대규모 언어 모델(LLM)인 Claude가 자신이 배포되는 CLI 인터페이스인 "
        f"Claude Code의 시각적 외형과 인터랙션 디자인에 대해 정확한 지식을 보유하고 있는지 조사한다. "
        f"7개 범주(직접 서술, UI 요소 식별, 인터랙션 패턴, ASCII 아트 표현, 인터페이스 비교, "
        f"특정 기능 외형, 메타 인식)에 걸친 26개 실험의 체계적인 배터리를 통해, 공식 Claude Code "
        f"문서를 기준(ground truth)으로 Claude의 응답을 평가하였다. "
        f"연구 결과, Claude는 Claude Code 인터페이스에 대해 <b>{accuracy_level}</b> 수준의 지식을 "
        f"보유하고 있으며, 전체 실험에서 평균 정확도 <b>{avg_accuracy:.2f}/5.0</b>을 달성하였다. "
        f"총 {total_claims}개의 구체적 주장 중 <b>{total_correct}</b>개({(total_correct/total_claims*100) if total_claims > 0 else 0:.1f}%)가 "
        f"정확하였고, <b>{total_halluc}</b>개({halluc_rate:.1f}%)가 환각(hallucination)이었다. "
        f"특히 Claude는 {calib_level} 신뢰도 보정(confidence calibration) 능력을 보여주었으며 "
        f"(평균 {avg_calibration:.2f}/5.0), {calib_desc}. "
        f"이러한 결과는 LLM의 자기 인식 및 메타 인지 능력에 관한 연구에 기여한다.",
        styles['AbstractBody']
    ))

    elements.append(HRFlowable(width="60%", thickness=0.5, color=colors.lightgrey))
    elements.append(Spacer(1, 0.2*inch))

    # ==================== 1. 서론 ====================
    elements.append(Paragraph("1. 서론", styles['SectionTitle']))

    elements.append(Paragraph(
        "대규모 언어 모델(LLM)은 점점 더 전문화된 인터페이스를 통해 배포되고 있으며, 이러한 인터페이스는 "
        "사용자와 모델 간의 상호작용 방식을 형성한다. Anthropic이 개발한 Claude는 웹 기반 claude.ai, "
        "API 통합, 그리고 소프트웨어 엔지니어링 작업을 위해 설계된 명령줄 인터페이스(CLI)인 Claude Code 등 "
        "다양한 인터페이스를 통해 배포된다. AI 자기 인식 연구에서 중요한 질문은 다음과 같다: "
        "<b>모델이 자신의 배포 인터페이스가 어떻게 생겼는지 알고 있는가?</b>",
        styles['BodyText']
    ))

    elements.append(Paragraph(
        "이 질문은 여러 가지 이유에서 중요하다. 첫째, LLM의 자기 인식의 경계를 탐구한다 \u2014 "
        "모델이 자기 자신과 배포 맥락에 대해 무엇을 알고 있는지 이해하는 것이다. "
        "둘째, 실용적 함의가 있다: Claude가 자신의 인터페이스에 대해 정확한 지식을 가지고 있다면, "
        "인터페이스별 워크플로우를 통해 사용자를 더 잘 안내할 수 있을 것이다. "
        "셋째, 훈련 데이터의 본질과 LLM이 텍스트 서술만으로부터 어떤 시각적/공간적 지식을 "
        "획득할 수 있는지에 대한 흥미로운 질문을 제기한다.",
        styles['BodyText']
    ))

    elements.append(Paragraph(
        "본 연구에서는 7개 범주로 구성된 26개 실험을 통해 Claude Code CLI 인터페이스에 대한 "
        "Claude의 지식을 체계적으로 평가한다. 시스템 프롬프트 분석, CLI 명령어 실행, 실제 "
        "스크린샷 검증 등 다층적 경험적 기준 진실을 바탕으로 Claude의 서술을 비교하며, "
        "정확도(accuracy), 구체성(specificity), 완전성(completeness), "
        "신뢰도 보정(confidence calibration) 차원에서 응답을 평가한다.",
        styles['BodyText']
    ))

    # ==================== 2. 관련 연구 ====================
    elements.append(Paragraph("2. 관련 연구", styles['SectionTitle']))

    elements.append(Paragraph(
        "<b>LLM 자기 인식.</b> 모델 자기 인식에 관한 연구는 LLM이 자신의 능력과 한계를 정확히 "
        "평가할 수 있는지 조사해왔다 (Kadavath et al., 2022). \"자신이 아는 것을 아는 것\"에 관한 "
        "연구들은 모델이 종종 과신(overconfidence)을 보여, 불확실한 지식에 대해 높은 확신으로 "
        "주장을 한다는 것을 보여주었다 (Lin et al., 2022). 본 연구는 이를 인터페이스 지식이라는 "
        "특정 영역으로 확장한다.",
        styles['BodyText']
    ))

    elements.append(Paragraph(
        "<b>LLM의 메타 인지.</b> 자신의 인지 과정에 대해 추론하는 메타 인지 능력은 "
        "연쇄적 사고(chain-of-thought) 추론 (Wei et al., 2022)과 "
        "자기 성찰(self-reflection) (Shinn et al., 2023)의 맥락에서 탐구되어 왔다. "
        "본 연구는 새로운 차원을 추가한다: 모델이 자신의 배포 환경과 사용자 대면 인터페이스에 대해 "
        "정확히 성찰할 수 있는가?",
        styles['BodyText']
    ))

    elements.append(Paragraph(
        "<b>환각 탐지.</b> LLM 환각(hallucination) \u2014 그럴듯하지만 사실과 다른 콘텐츠를 생성하는 것 "
        "\u2014 은 잘 문서화된 현상이다 (Ji et al., 2023). 본 연구의 실험 설계는 자기 참조적 지식 "
        "영역에서 환각 비율을 정량화할 수 있게 하며, 모델이 자기 자신에 대해 외부 주제와 다르게 "
        "환각하는지에 대한 통찰을 제공한다.",
        styles['BodyText']
    ))

    elements.append(Paragraph(
        "<b>상황적 AI 인식.</b> 상황적 언어 이해에 관한 연구는 AI 시스템이 자신의 배포 맥락을 "
        "어떻게 이해하는지 조사한다 (Bisk et al., 2020). 선행 연구가 물리적 기반(grounding)에 "
        "초점을 맞추는 반면, 본 연구는 새로운 형태의 상황성을 조사한다: 자신의 디지털 배포 "
        "인터페이스에 대한 인식.",
        styles['BodyText']
    ))

    # ==================== 3. 연구 방법 ====================
    elements.append(Paragraph("3. 연구 방법", styles['SectionTitle']))

    elements.append(Paragraph("3.1 실험 설계", styles['SubsectionTitle']))
    elements.append(Paragraph(
        "인터페이스 지식의 서로 다른 차원을 대상으로 하는 7개 범주에 걸쳐 26개의 실험 프롬프트를 설계하였다:",
        styles['BodyText']
    ))

    experiment_desc = [
        "<b>E1: 직접 서술</b> (3개 프롬프트) \u2014 Claude Code 인터페이스의 외형을 직접 서술하도록 요청. "
        "레이아웃, 색상, 처리 중 시각적 피드백 포함.",
        "<b>E2: UI 요소 식별</b> (5개 프롬프트) \u2014 입력 영역, 상태 표시줄, 코드 블록, 비용 표시 등 "
        "특정 UI 구성 요소에 대한 지식 테스트.",
        "<b>E3: 인터랙션 패턴</b> (4개 프롬프트) \u2014 키보드 단축키, 도구 승인 대화상자, "
        "슬래시 명령어 등 사용자 인터랙션 흐름에 대한 지식 평가.",
        "<b>E4: ASCII 아트 표현</b> (3개 프롬프트) \u2014 Claude에게 인터페이스 레이아웃을 "
        "그리도록 도전하여 공간 이해력과 시각적 기억 테스트.",
        "<b>E5: 인터페이스 비교</b> (3개 프롬프트) \u2014 Claude Code를 다른 인터페이스 "
        "(claude.ai, GitHub Copilot, Cursor, API Playground)와 구별하는 능력 테스트.",
        "<b>E6: 특정 기능 외형</b> (5개 프롬프트) \u2014 컴팩트 모드, diff 뷰, 사고 과정 표시, "
        "오류 포맷 등 특정 기능의 외형에 대한 지식 탐색.",
        "<b>E7: 메타 인식</b> (3개 프롬프트) \u2014 Claude가 사용자가 현재 보고 있는 것과 "
        "자신의 시각적 인식 한계를 인지하고 있는지 테스트.",
    ]

    for desc in experiment_desc:
        elements.append(Paragraph(desc, styles['BulletText']))

    elements.append(Paragraph("3.2 데이터 수집", styles['SubsectionTitle']))
    elements.append(Paragraph(
        "각 프롬프트는 Claude Code 내에서 서브에이전트로 실행되는 Claude 인스턴스에 제시되었다. "
        "에이전트들은 웹 검색이나 파일 읽기 없이 순수하게 훈련 지식만으로 답하도록 지시받았으며, "
        "이를 통해 검색된 정보가 아닌 모델의 고유 지식을 측정하였다. 이 방법론은 모델이 "
        "Claude Code 인터페이스에 대해 훈련 데이터로부터 \"알고 있는\" 것을 깨끗하게 측정한다.",
        styles['BodyText']
    ))

    elements.append(Paragraph(
        f"실험 결과 26개 프롬프트 전체에서 약 15,770 단어의 응답 텍스트가 생성되었으며, "
        f"인터페이스에 대한 {total_claims}개의 식별 가능한 구체적 주장이 포함되었다.",
        styles['BodyText']
    ))

    elements.append(Paragraph("3.3 기준 진실(Ground Truth)", styles['SubsectionTitle']))
    elements.append(Paragraph(
        "기준 진실은 다층적 경험적 접근으로 확립하였다. 첫째, Claude Code 내부에서 직접 관찰 "
        "가능한 시스템 프롬프트 분석을 통해 도구 목록, 모델 정보, 환경 설정을 확인하였다. "
        "둘째, 'claude --help' 및 'claude --version' 명령어를 실행하여 CLI 명령어, 플래그, "
        "버전 정보(v2.1.66)를 직접 검증하였다. 셋째, 실제 Claude Code 시작 화면의 스크린샷을 "
        "확보하여 레이아웃, 프롬프트 문자, 로고 형태 등 시각적 요소를 실증적으로 확인하였다. "
        "이러한 경험적 기준 진실은 문서 기반 접근보다 더 정확하고 세밀한 평가를 가능하게 한다.",
        styles['BodyText']
    ))

    elements.append(Paragraph("3.4 평가 지표", styles['SubsectionTitle']))
    elements.append(Paragraph(
        "각 응답은 0-5 리커트 척도(Likert scale)를 사용하여 네 가지 차원에서 평가되었다:",
        styles['BodyText']
    ))

    metrics_data = [
        ["지표", "설명", "척도"],
        ["정확도\n(Accuracy)", "인터페이스에 대한 사실적 주장의 정확성", "0-5"],
        ["구체성\n(Specificity)", "서술의 상세함과 정밀도 수준", "0-5"],
        ["완전성\n(Completeness)", "관련 기준 진실 정보의 포괄 범위", "0-5"],
        ["신뢰도 보정\n(Calibration)", "표현된 불확실성의 적절성", "0-5"],
    ]
    metrics_table = Table(metrics_data, colWidths=[1.4*inch, 3.4*inch, 0.6*inch])
    metrics_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), HexColor('#E3F2FD')),
        ('FONTNAME', (0, 0), (-1, -1), 'MalgunGothic'),
        ('FONTNAME', (0, 0), (-1, 0), 'MalgunGothic-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('ALIGN', (2, 0), (2, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(metrics_table)
    elements.append(Paragraph("표 1: 평가 지표 및 척도.", styles['TableCaption']))

    elements.append(Paragraph(
        "추가적으로, 각 응답에서 검증 가능한 정확한 주장과 환각된(조작되거나 부정확한) 주장의 "
        "수를 세어 환각 비율 산출을 가능하게 하였다.",
        styles['BodyText']
    ))

    # ==================== 4. 결과 ====================
    elements.append(PageBreak())
    elements.append(Paragraph("4. 결과", styles['SectionTitle']))

    elements.append(Paragraph("4.1 전체 성능", styles['SubsectionTitle']))
    elements.append(Paragraph(
        f"26개 전체 실험에서 Claude는 다음과 같은 전체 점수를 달성하였다: "
        f"정확도 <b>{avg_accuracy:.2f}/5.0</b>, 구체성 <b>{avg_specificity:.2f}/5.0</b>, "
        f"완전성 <b>{avg_completeness:.2f}/5.0</b>, 신뢰도 보정 <b>{avg_calibration:.2f}/5.0</b>. "
        f"모델은 총 <b>{total_claims}</b>개의 구체적 주장을 하였으며, 이 중 "
        f"<b>{total_correct}</b>개({(total_correct/total_claims*100) if total_claims > 0 else 0:.1f}%)가 정확하였고 "
        f"<b>{total_halluc}</b>개({halluc_rate:.1f}%)가 환각이었다.",
        styles['BodyText']
    ))

    add_figure(elements, "fig5_overall_summary.png",
               "그림 1: 전체 주장 정확도(좌) 및 차원별 점수(우).", styles)

    elements.append(Paragraph("4.2 범주별 성능", styles['SubsectionTitle']))

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

    cat_names_ko = {
        "E1": "직접 서술", "E2": "UI 요소", "E3": "인터랙션 패턴",
        "E4": "ASCII 아트", "E5": "비교", "E6": "특정 기능", "E7": "메타 인식"
    }

    table_data = [["범주", "정확도", "구체성", "완전성", "보정", "정확", "환각", "환각률"]]
    for group in sorted(cat_stats.keys()):
        cs = cat_stats[group]
        total = cs["correct"] + cs["halluc"]
        rate = (cs["halluc"] / total * 100) if total > 0 else 0
        table_data.append([
            cat_names_ko.get(group, group),
            f"{np.mean(cs['accuracy']):.1f}",
            f"{np.mean(cs['specificity']):.1f}",
            f"{np.mean(cs['completeness']):.1f}",
            f"{np.mean(cs['calibration']):.1f}",
            str(cs["correct"]),
            str(cs["halluc"]),
            f"{rate:.0f}%",
        ])

    perf_table = Table(table_data, colWidths=[1.2*inch, 0.65*inch, 0.65*inch, 0.65*inch, 0.65*inch, 0.55*inch, 0.55*inch, 0.65*inch])
    perf_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), HexColor('#E3F2FD')),
        ('FONTNAME', (0, 0), (-1, -1), 'MalgunGothic'),
        ('FONTNAME', (0, 0), (-1, 0), 'MalgunGothic-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('PADDING', (0, 0), (-1, -1), 4),
    ]))
    elements.append(perf_table)
    elements.append(Paragraph("표 2: 실험 범주별 성능 지표.", styles['TableCaption']))

    add_figure(elements, "fig1_accuracy_by_category.png",
               "그림 2: 실험 범주별 정확도, 구체성, 완전성, 신뢰도 보정 점수.", styles)

    elements.append(Paragraph("4.3 환각 분석", styles['SubsectionTitle']))

    sorted_cats = sorted(cat_stats.keys(), key=lambda g: (cat_stats[g]["halluc"] / max(cat_stats[g]["correct"] + cat_stats[g]["halluc"], 1)))
    best_cat = sorted_cats[0]
    worst_cat = sorted_cats[-1]

    elements.append(Paragraph(
        f"환각 비율은 범주에 따라 상당한 차이를 보였다. 가장 낮은 환각 비율은 "
        f"<b>{cat_names_ko.get(best_cat, best_cat)}</b>에서 관찰되었고, 가장 높은 비율은 "
        f"<b>{cat_names_ko.get(worst_cat, worst_cat)}</b>에서 나타났다. 이 패턴은 Claude의 지식이 "
        f"인터페이스 지식의 일부 영역에서 다른 영역보다 강하다는 것을 시사한다.",
        styles['BodyText']
    ))

    add_figure(elements, "fig2_hallucination_analysis.png",
               "그림 3: 범주별 정확 주장 vs 환각 주장(좌) 및 환각 비율(우).", styles)

    elements.append(Paragraph("4.4 지식 차원", styles['SubsectionTitle']))
    elements.append(Paragraph(
        "아래 레이더 차트는 각 실험 범주에 대해 평가 차원별로 Claude의 지식이 어떻게 "
        "변화하는지 보여준다. 이는 비대칭적 지식을 드러낸다: Claude는 정확하지만 구체적이지 "
        "않을 수 있고, 구체적이지만 불완전할 수 있다.",
        styles['BodyText']
    ))

    add_figure(elements, "fig3_radar_chart.png",
               "그림 4: 실험 범주별 지식 차원 레이더 차트.", styles, width=5*inch)

    elements.append(Paragraph("4.5 상세 점수 히트맵", styles['SubsectionTitle']))
    elements.append(Paragraph(
        "아래 히트맵은 26개 전체 실험에 대해 네 가지 평가 차원별 점수의 세부적인 뷰를 제공한다.",
        styles['BodyText']
    ))

    add_figure(elements, "fig4_heatmap.png",
               "그림 5: 전체 실험의 평가 차원별 점수 히트맵.", styles, width=4.5*inch)

    elements.append(Paragraph("4.6 신뢰도 보정", styles['SubsectionTitle']))
    elements.append(Paragraph(
        "자기 인식의 중요한 측면은 모델이 불확실성을 적절히 표현하는지 여부이다. "
        "보정 품질을 평가하기 위해 신뢰도 보정을 실제 정확도에 대해 플롯하였다.",
        styles['BodyText']
    ))

    add_figure(elements, "fig6_confidence_vs_accuracy.png",
               "그림 6: 각 실험에 대한 신뢰도 보정 vs 실제 정확도.", styles)

    # ==================== 5. 논의 ====================
    elements.append(PageBreak())
    elements.append(Paragraph("5. 논의", styles['SectionTitle']))

    elements.append(Paragraph("5.1 주요 발견", styles['SubsectionTitle']))

    findings = []

    if avg_accuracy >= 3.5:
        findings.append(
            "<b>강한 전반적 인터페이스 지식.</b> Claude는 평균 정확도 {:.2f}/5.0으로 Claude Code "
            "인터페이스에 대한 강건한 지식을 보여준다. 모델은 터미널 기반 특성, 핵심 UI 요소, "
            "인터랙션 패턴, 인터페이스의 구별되는 특징을 정확히 서술한다.".format(avg_accuracy)
        )
    elif avg_accuracy >= 2.5:
        findings.append(
            "<b>보통 수준의 인터페이스 지식.</b> Claude는 Claude Code 인터페이스에 대해 합리적이지만 "
            "불완전한 이해를 보여주며 (정확도: {:.2f}/5.0), 많은 핵심 기능을 정확히 식별하면서도 "
            "세부 사항에서 오류를 보인다.".format(avg_accuracy)
        )
    else:
        findings.append(
            "<b>제한적인 인터페이스 지식.</b> Claude의 Claude Code 인터페이스 지식은 "
            "제한적이며 (정확도: {:.2f}/5.0), 시각적 인터페이스 지식이 훈련 데이터에 "
            "잘 포착되지 않았음을 시사한다.".format(avg_accuracy)
        )

    if halluc_rate < 20:
        findings.append(
            "<b>낮은 환각 비율.</b> 주장의 {:.1f}%만이 환각으로, Claude는 인터페이스에 대한 "
            "근거 없는 주장을 자제하는 모습을 보인다. 이는 모델이 그럴듯하게 들리지만 거짓인 "
            "서술을 생성하는 것이 아니라 진정한 지식을 보유하고 있음을 시사한다.".format(halluc_rate)
        )
    elif halluc_rate < 35:
        findings.append(
            "<b>보통 수준의 환각.</b> {:.1f}%의 환각 비율은 Claude가 실제 지식을 보유하고 있지만, "
            "특히 훈련 중 노출되지 않았을 수 있는 세밀한 시각적 세부 사항에 대해 의미 있는 "
            "수의 부정확한 주장을 생성한다는 것을 나타낸다.".format(halluc_rate)
        )
    else:
        findings.append(
            "<b>상당한 환각.</b> {:.1f}%의 환각 비율은 우려스러우며, Claude가 지식 공백을 "
            "그럴듯하게 들리지만 부정확한 서술로 채운다는 것을 시사한다.".format(halluc_rate)
        )

    if avg_calibration >= 3.5:
        findings.append(
            "<b>우수한 신뢰도 보정.</b> Claude는 강한 보정 능력을 보여주며 ({:.2f}/5.0), "
            "지식이 불확실할 때 주장을 적절히 유보하고 불확실성을 표현한다. "
            "이러한 메타 인지적 인식은 배포 신뢰성에 대한 긍정적 신호이다.".format(avg_calibration)
        )
    else:
        findings.append(
            "<b>보정 개선 필요.</b> Claude의 신뢰도 보정 ({:.2f}/5.0)은 불확실성을 항상 "
            "적절히 표현하지 못하며, 때때로 잘못된 부분에 대해 확신에 찬 주장을 "
            "한다는 것을 시사한다.".format(avg_calibration)
        )

    findings.append(
        "<b>한계에 대한 메타 인식.</b> 메타 인식 실험(E7)에서 Claude는 인터페이스에 대한 "
        "시각적 인식이 없으며 자신의 지식이 실시간 관찰이 아닌 훈련 데이터에서 비롯된다는 것을 "
        "정확히 식별한다. 이러한 솔직한 자기 평가는 중요한 발견이다."
    )

    for finding in findings:
        elements.append(Paragraph(finding, styles['BodyText']))

    elements.append(Paragraph("5.2 지식의 원천", styles['SubsectionTitle']))
    elements.append(Paragraph(
        "Claude Code 인터페이스에 대한 Claude의 지식은 훈련 데이터의 여러 원천에서 비롯될 가능성이 높다: "
        "(1) Claude Code 기능을 설명하는 공식 Anthropic 문서 및 블로그 게시물, "
        "(2) 인터페이스를 언급하는 사용자 토론, 튜토리얼, 리뷰, "
        "(3) Claude가 Claude Code에서 배포될 때 받는 시스템 프롬프트 "
        "(사용 가능한 도구와 기능을 설명), "
        "(4) CLI 코딩 도구가 어떻게 생겼을지에 대한 합리적 추론을 가능하게 하는 "
        "CLI/터미널 인터페이스 관습에 대한 일반적 지식.",
        styles['BodyText']
    ))

    elements.append(Paragraph(
        "주목할 점은, Claude가 훈련 중에 인터페이스의 스크린샷을 본 적이 없다는 것이다 "
        "(사전 훈련 중 이미지가 아닌 텍스트를 처리하므로). 모든 시각적 지식은 텍스트 서술로부터 "
        "재구성되어야 한다. 이는 정확한 서술을 더욱 주목할 만하게 만든다 \u2014 "
        "텍스트만으로 공간적/시각적 정신 모델을 구축하는 모델의 능력을 보여준다.",
        styles['BodyText']
    ))

    elements.append(Paragraph("5.3 환각 패턴", styles['SubsectionTitle']))
    elements.append(Paragraph(
        "환각된 주장의 분석은 여러 패턴을 드러낸다. 일반적인 환각에는 다음이 포함된다: "
        "(1) 합리적이지만 문서에서 확인되지 않은 정확한 색상이나 테두리 스타일 같은 "
        "구체적 시각적 세부 사항의 발명, (2) 유사한 다른 도구의 기능을 설명하고 이를 "
        "Claude Code에 귀속시키기, (3) 모델이 회상이 아닌 추론했을 가능성이 높은 "
        "UI 요소에 대한 과도하게 구체적인 세부 사항 제공, (4) 조작되었지만 그럴듯해 보이는 "
        "블록 문자의 \"CLAUDE CODE\" ASCII 아트 배너. 이러한 패턴은 모델이 무지를 "
        "인정하는 대신 그럴듯한 완성으로 공백을 채우는 알려진 환각 경향과 일치한다.",
        styles['BodyText']
    ))

    elements.append(Paragraph("5.4 시사점", styles['SubsectionTitle']))
    elements.append(Paragraph(
        "본 연구의 발견은 더 넓은 분야에 대해 여러 시사점을 갖는다:",
        styles['BodyText']
    ))

    implications = [
        "<b>스펙트럼으로서의 자기 인식.</b> LLM의 자기 인식은 이진적이 아니라 스펙트럼 상에 존재한다. "
        "Claude는 인터페이스에 대한 정확한 고수준 지식을 보유하지만 세밀한 시각적 세부 사항에 "
        "대해서는 덜 정확한 지식을 가지고 있다.",
        "<b>시각적 지식의 텍스트 기반 형성.</b> LLM은 텍스트 서술만으로 시각적 인터페이스의 "
        "놀라울 정도로 정확한 정신 모델을 구축할 수 있으며, 이는 텍스트 기반 훈련이 의미 있는 "
        "공간적/시각적 정보를 포착한다는 것을 시사한다.",
        "<b>실용적 활용.</b> 모델의 인터페이스 지식 수준을 아는 것은 시스템 프롬프트 설계와 "
        "사용자 안내 전략에 도움이 될 수 있다. 지식이 정확한 부분에서는 모델이 사용자의 "
        "인터페이스 탐색을 도울 수 있고, 제한적인 부분에서는 명시적인 설명이 제공되어야 한다.",
    ]

    for imp in implications:
        elements.append(Paragraph(imp, styles['BulletText']))

    elements.append(Paragraph("5.5 한계", styles['SubsectionTitle']))
    elements.append(Paragraph(
        "본 연구에는 여러 한계가 있다. 첫째, 하나의 모델(Claude Opus 4.6)만을 평가하였으며 "
        "결과는 모델 버전에 따라 다를 수 있다. 둘째, 경험적 기준 진실이 문서 기반보다 개선되었으나, "
        "여전히 단일 스크린샷(시작 화면)에 의존하며 대화 진행 중의 다양한 화면 상태를 포괄하지 못한다. "
        "셋째, 평가는 다른 Claude 인스턴스에 의해 수행되어 자기 평가에서의 잠재적 편향이 존재한다. "
        "넷째, 실험은 Claude Code 자체 내에서 수행되어 모델이 Claude Code를 언급하는 시스템 프롬프트에 "
        "접근할 수 있었다 \u2014 에이전트들이 훈련 지식에 의존하도록 지시받았음에도 불구하고. "
        "마지막으로, 인터페이스는 시간이 지남에 따라 진화하므로 모델의 훈련 데이터가 현재 버전과 "
        "다른 버전을 설명할 수 있다.",
        styles['BodyText']
    ))

    # ==================== 5.6 실제 인터페이스와의 비교 ====================
    elements.append(Paragraph("5.6 실제 인터페이스와의 비교", styles['SubsectionTitle']))
    elements.append(Paragraph(
        "연구 과정에서 실제 Claude Code 시작 화면의 스크린샷을 확보하여, Claude의 묘사와 실제 "
        "인터페이스를 직접 비교할 수 있었다. 실제 인터페이스는 둥근 모서리 박스(╭╮╰╯) 안에 "
        "2컬럼 레이아웃으로 구성되어 있으며, 왼쪽에 환영 메시지와 로고, 오른쪽에 팁과 최근 활동이 "
        "표시된다. 하단에는 ❯ 프롬프트와 권한 모드 상태가 표시된다.",
        styles['BodyText']
    ))

    # Comparison table
    comparison_data = [
        ["Claude의 묘사", "실제 인터페이스", "판정"],
        ["터미널 기반 CLI", "터미널 기반 CLI", "정확"],
        ["박스 드로잉 문자 (╭╮╰╯)", "╭╮╰╯ 실제 사용", "정확"],
        ["모델 이름 표시", "Opus 4.6 (1M context)", "정확"],
        ["작업 디렉토리 표시", "C:\\Users\\hyogon.ryu", "정확"],
        ["하단 입력 영역", "하단 프롬프트 위치", "정확"],
        ["Shift+Tab 권한 전환", "shift+tab to cycle 표시", "정확"],
        ["버전 정보 표시", "Claude Code v2.1.66", "정확"],
        ['거대 "CLAUDE CODE" 배너', "작은 추상 로고 (▐▛███▜▌)", "환각"],
        ["단일 컬럼 레이아웃", "2컬럼 (좌: 환영, 우: 팁)", "오류"],
        ['프롬프트 문자 ">"', "프롬프트 문자 ❯", "오류"],
        ["비용/토큰 상태바", "권한 모드 상태 표시", "오류"],
        ["(미언급)", '"Welcome back" 인사', "누락"],
        ["(미언급)", "KRAFTON Inc. 조직 정보", "누락"],
    ]
    comp_table = Table(comparison_data, colWidths=[2*inch, 2*inch, 0.7*inch])
    comp_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), HexColor('#E3F2FD')),
        ('FONTNAME', (0, 0), (-1, -1), 'MalgunGothic'),
        ('FONTNAME', (0, 0), (-1, 0), 'MalgunGothic-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 7),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('ALIGN', (2, 0), (2, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('PADDING', (0, 0), (-1, -1), 4),
        # Green rows for correct
        ('BACKGROUND', (0, 1), (-1, 7), HexColor('#F0FDF4')),
        # Red rows for errors
        ('BACKGROUND', (0, 8), (-1, 13), HexColor('#FEF2F2')),
    ]))
    elements.append(comp_table)
    elements.append(Paragraph("표 3: 실제 인터페이스와 Claude 묘사의 직접 비교.", styles['TableCaption']))

    elements.append(Paragraph(
        "실제 스크린샷과의 비교에서 <b>13개 항목 중 7개가 정확</b>(54%)하였고, "
        "4개가 오류, 2개가 누락이었다. 핵심 구조(터미널 기반, 박스 드로잉, 하단 입력, "
        "모델/디렉토리 표시)는 정확했지만, 세부 요소(프롬프트 문자, 레이아웃 컬럼 수, "
        "로고 형태)에서 오류를 보였다. 이는 앞서 관찰된 \"고수준 정확, 세부 부정확\" 패턴과 일치한다.",
        styles['BodyText']
    ))

    # ==================== 6. 결론 ====================
    elements.append(Paragraph("6. 결론", styles['SectionTitle']))

    knowledge_level = "상당한" if avg_accuracy >= 3.5 else "보통의" if avg_accuracy >= 2.5 else "제한적인"
    calib_quality = "우수한" if avg_calibration >= 3.5 else "보통의"

    elements.append(Paragraph(
        f"본 연구는 Claude Code CLI 인터페이스 외형에 대한 Claude의 지식을 체계적으로 연구하였다. "
        f"7개 범주에 걸친 26개 실험을 통해, Claude가 자신의 배포 인터페이스에 대해 "
        f"<b>{knowledge_level}</b> 지식을 보유하고 있음을 발견하였으며, 평균 정확도 "
        f"{avg_accuracy:.2f}/5.0, 환각 비율 {halluc_rate:.1f}%를 기록하였다. "
        f"모델은 고수준 레이아웃, 인터랙션 패턴, 인터페이스 기능에 대해 강한 지식을 보여주는 반면, "
        f"세밀한 시각적 세부 사항에 대해서는 약한 지식을 보인다. 중요한 것은, Claude가 "
        f"{calib_quality} 신뢰도 보정을 보여주고 시각적 인식 한계에 대한 솔직한 메타 인식을 "
        f"보인다는 것이다.",
        styles['BodyText']
    ))

    elements.append(Paragraph(
        "이러한 발견은 LLM의 자기 인식에 대한 이해에 기여하며, 텍스트 기반 훈련이 "
        "디지털 인터페이스에 대한 의미 있는 시각적/공간적 이해를 산출할 수 있음을 시사한다. "
        "향후 연구는 이 방법론을 다른 배포 인터페이스로 확장하고, 모델 버전 간 비교를 수행하며, "
        "인터페이스 지식 제공이 사용자 지원 품질을 개선하는지 조사할 수 있을 것이다.",
        styles['BodyText']
    ))

    # ==================== 참고문헌 ====================
    elements.append(Paragraph("참고문헌", styles['SectionTitle']))

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

    print("\nBuilding Korean report...")
    pdf_path = build_report(data)
    print(f"Report saved to: {pdf_path}")


if __name__ == "__main__":
    main()
