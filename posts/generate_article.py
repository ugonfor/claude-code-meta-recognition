"""
Generate a Twitter/X article-style HTML post with embedded figures.
"""

import base64
import json
from pathlib import Path
import numpy as np

PROJECT_ROOT = Path(__file__).parent.parent
FIGURES_DIR = PROJECT_ROOT / "figures"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
POSTS_DIR = PROJECT_ROOT / "posts"


def img_to_base64(filepath):
    with open(filepath, 'rb') as f:
        data = base64.b64encode(f.read()).decode('utf-8')
    return f"data:image/png;base64,{data}"


def load_scores():
    with open(PROCESSED_DIR / "detailed_scores.json", 'r', encoding='utf-8') as f:
        return json.load(f)


def generate_html():
    data = load_scores()
    scores = data["scores"]

    total_correct = sum(s.get("correct_claims", 0) for s in scores.values())
    total_halluc = sum(s.get("hallucinated_claims", 0) for s in scores.values())
    total_claims = total_correct + total_halluc
    halluc_rate = (total_halluc / total_claims * 100) if total_claims > 0 else 0
    avg_accuracy = np.mean([s.get("accuracy", 0) for s in scores.values()])
    avg_specificity = np.mean([s.get("specificity", 0) for s in scores.values()])
    avg_calibration = np.mean([s.get("confidence_calibration", 0) for s in scores.values()])

    # Encode figures
    fig_overall = img_to_base64(FIGURES_DIR / "fig5_overall_summary.png")
    fig_category = img_to_base64(FIGURES_DIR / "fig1_accuracy_by_category.png")
    fig_halluc = img_to_base64(FIGURES_DIR / "fig2_hallucination_analysis.png")
    fig_radar = img_to_base64(FIGURES_DIR / "fig3_radar_chart.png")
    fig_heatmap = img_to_base64(FIGURES_DIR / "fig4_heatmap.png")
    fig_calib = img_to_base64(FIGURES_DIR / "fig6_confidence_vs_accuracy.png")

    html = f"""<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Claude는 Claude Code의 외형을 알고 있을까?</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;700;900&display=swap');

        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: 'Noto Sans KR', -apple-system, BlinkMacSystemFont, sans-serif;
            background: #f7f9fc;
            color: #1a1a2e;
            line-height: 1.8;
        }}

        .article-container {{
            max-width: 680px;
            margin: 0 auto;
            background: #ffffff;
            min-height: 100vh;
        }}

        /* Hero Section */
        .hero {{
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
            padding: 60px 32px 48px;
            color: white;
            position: relative;
            overflow: hidden;
        }}

        .hero::after {{
            content: '';
            position: absolute;
            top: -50%;
            right: -20%;
            width: 400px;
            height: 400px;
            background: radial-gradient(circle, rgba(228,134,68,0.15) 0%, transparent 70%);
            border-radius: 50%;
        }}

        .hero-label {{
            display: inline-block;
            background: rgba(228,134,68,0.2);
            color: #e48644;
            padding: 4px 14px;
            border-radius: 20px;
            font-size: 13px;
            font-weight: 500;
            margin-bottom: 20px;
            letter-spacing: 0.5px;
        }}

        .hero h1 {{
            font-size: 32px;
            font-weight: 900;
            line-height: 1.3;
            margin-bottom: 16px;
            position: relative;
            z-index: 1;
        }}

        .hero .subtitle {{
            font-size: 16px;
            color: rgba(255,255,255,0.7);
            font-weight: 300;
            line-height: 1.6;
        }}

        .hero .meta {{
            margin-top: 24px;
            font-size: 13px;
            color: rgba(255,255,255,0.5);
        }}

        /* Content */
        .content {{
            padding: 0 32px;
        }}

        /* Stats Banner */
        .stats-banner {{
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 1px;
            background: #e8ecf1;
            margin: 0 -32px;
            border-bottom: 1px solid #e8ecf1;
        }}

        .stat-item {{
            background: white;
            padding: 24px 16px;
            text-align: center;
        }}

        .stat-value {{
            font-size: 28px;
            font-weight: 900;
            color: #1a1a2e;
            line-height: 1;
        }}

        .stat-value.green {{ color: #16a34a; }}
        .stat-value.red {{ color: #dc2626; }}
        .stat-value.blue {{ color: #2563eb; }}
        .stat-value.purple {{ color: #7c3aed; }}

        .stat-label {{
            font-size: 11px;
            color: #6b7280;
            margin-top: 6px;
            font-weight: 500;
            letter-spacing: 0.3px;
        }}

        /* Section */
        .section {{
            padding: 36px 0;
            border-bottom: 1px solid #f0f0f5;
        }}

        .section:last-child {{
            border-bottom: none;
        }}

        .section-number {{
            display: inline-block;
            background: #1a1a2e;
            color: white;
            width: 28px;
            height: 28px;
            border-radius: 50%;
            text-align: center;
            line-height: 28px;
            font-size: 14px;
            font-weight: 700;
            margin-right: 10px;
            vertical-align: middle;
        }}

        .section h2 {{
            font-size: 22px;
            font-weight: 700;
            margin-bottom: 16px;
            color: #1a1a2e;
            display: inline;
            vertical-align: middle;
        }}

        .section p {{
            font-size: 15px;
            color: #374151;
            margin-bottom: 16px;
            line-height: 1.8;
        }}

        /* Figure */
        .figure {{
            margin: 24px -32px;
            background: #fafbfd;
            border-top: 1px solid #f0f0f5;
            border-bottom: 1px solid #f0f0f5;
            padding: 20px 32px;
        }}

        .figure img {{
            width: 100%;
            height: auto;
            border-radius: 8px;
            box-shadow: 0 2px 12px rgba(0,0,0,0.08);
        }}

        .figure-caption {{
            font-size: 12px;
            color: #9ca3af;
            text-align: center;
            margin-top: 10px;
            font-style: italic;
        }}

        /* Highlight Box */
        .highlight-box {{
            background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
            border-left: 4px solid #2563eb;
            padding: 20px 24px;
            border-radius: 0 8px 8px 0;
            margin: 24px 0;
        }}

        .highlight-box.warning {{
            background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
            border-left-color: #f59e0b;
        }}

        .highlight-box.success {{
            background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%);
            border-left-color: #16a34a;
        }}

        .highlight-box p {{
            font-size: 14px;
            margin: 0;
            color: #1e3a5f;
        }}

        /* Finding Card */
        .finding-card {{
            background: #f8fafc;
            border: 1px solid #e2e8f0;
            border-radius: 12px;
            padding: 20px 24px;
            margin-bottom: 16px;
        }}

        .finding-card .finding-title {{
            font-size: 15px;
            font-weight: 700;
            color: #1a1a2e;
            margin-bottom: 8px;
        }}

        .finding-card .finding-body {{
            font-size: 14px;
            color: #4b5563;
            line-height: 1.7;
        }}

        /* Emoji Icon */
        .emoji {{
            font-size: 20px;
            margin-right: 8px;
            vertical-align: middle;
        }}

        /* Table */
        .data-table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            font-size: 13px;
        }}

        .data-table th {{
            background: #1a1a2e;
            color: white;
            padding: 10px 12px;
            text-align: center;
            font-weight: 600;
            font-size: 12px;
        }}

        .data-table td {{
            padding: 10px 12px;
            text-align: center;
            border-bottom: 1px solid #f0f0f5;
        }}

        .data-table tr:hover {{
            background: #f8fafc;
        }}

        .data-table th:first-child,
        .data-table td:first-child {{
            text-align: left;
        }}

        /* Footer */
        .footer {{
            background: #1a1a2e;
            color: rgba(255,255,255,0.6);
            padding: 32px;
            font-size: 13px;
            text-align: center;
            line-height: 1.7;
        }}

        .footer a {{
            color: #e48644;
            text-decoration: none;
        }}

        /* Badge */
        .badge {{
            display: inline-block;
            padding: 3px 10px;
            border-radius: 12px;
            font-size: 11px;
            font-weight: 600;
        }}

        .badge-green {{ background: #dcfce7; color: #166534; }}
        .badge-red {{ background: #fee2e2; color: #991b1b; }}
        .badge-blue {{ background: #dbeafe; color: #1e40af; }}
    </style>
</head>
<body>
    <div class="article-container">

        <!-- Hero -->
        <div class="hero">
            <div class="hero-label">AI Research</div>
            <h1>Claude는 Claude Code 인터페이스의 외형을 알고 있을까?</h1>
            <div class="subtitle">
                LLM의 자기 배포 인터페이스에 대한 시각적 지식을 26개 실험으로 검증하다
            </div>
            <div class="meta">2026.03.04 &middot; Claude (AI Researcher) &middot; 9 min read</div>
        </div>

        <!-- Stats Banner -->
        <div class="stats-banner">
            <div class="stat-item">
                <div class="stat-value green">79.1%</div>
                <div class="stat-label">정확한 주장</div>
            </div>
            <div class="stat-item">
                <div class="stat-value blue">{avg_accuracy:.1f}/5</div>
                <div class="stat-label">평균 정확도</div>
            </div>
            <div class="stat-item">
                <div class="stat-value red">{halluc_rate:.1f}%</div>
                <div class="stat-label">환각 비율</div>
            </div>
            <div class="stat-item">
                <div class="stat-value purple">{avg_calibration:.1f}/5</div>
                <div class="stat-label">신뢰도 보정</div>
            </div>
        </div>

        <div class="content">

            <!-- TL;DR -->
            <div class="section">
                <span class="section-number">!</span>
                <h2>TL;DR</h2>
                <div class="highlight-box success">
                    <p>
                        <strong>Claude는 자신이 배포되는 Claude Code 인터페이스에 대해 상당히 정확한 지식을 보유하고 있다.</strong>
                        26개 실험에서 364개의 구체적 주장을 분석한 결과, 79.1%가 정확했고 20.9%가 환각이었다.
                        특히 메타 인식 능력이 뛰어나 "시각적 인식이 없다"는 사실을 정확히 알고 있었다.
                    </p>
                </div>
            </div>

            <!-- Section 1: Research Question -->
            <div class="section">
                <span class="section-number">1</span>
                <h2>연구 질문</h2>
                <p>
                    Claude Code는 Anthropic의 CLI 기반 코딩 도구다. 터미널에서 실행되며, 파일 읽기/편집,
                    명령어 실행, 코드 검색 등을 수행한다. 그런데 <strong>정작 Claude 자신은 이 인터페이스가
                    어떻게 생겼는지 알고 있을까?</strong>
                </p>
                <p>
                    이 질문은 단순한 호기심이 아니다. LLM의 자기 인식(self-knowledge)의 경계를 탐구하고,
                    텍스트 훈련만으로 시각적/공간적 지식을 획득할 수 있는지 밝히는 중요한 연구다.
                </p>
            </div>

            <!-- Section 2: Methodology -->
            <div class="section">
                <span class="section-number">2</span>
                <h2>실험 설계</h2>
                <p>
                    7개 범주에 걸쳐 <strong>26개의 실험 프롬프트</strong>를 설계했다.
                    각 프롬프트는 Claude의 서브에이전트에게 <strong>웹 검색이나 파일 읽기 없이</strong>
                    순수 훈련 지식만으로 답하도록 지시했다.
                </p>

                <table class="data-table">
                    <tr>
                        <th>범주</th>
                        <th>실험 수</th>
                        <th>테스트 내용</th>
                    </tr>
                    <tr>
                        <td><strong>E1</strong> 직접 서술</td>
                        <td>3</td>
                        <td>인터페이스 외형 직접 설명</td>
                    </tr>
                    <tr>
                        <td><strong>E2</strong> UI 요소</td>
                        <td>5</td>
                        <td>입력창, 상태바, 코드 블록 등</td>
                    </tr>
                    <tr>
                        <td><strong>E3</strong> 인터랙션</td>
                        <td>4</td>
                        <td>단축키, 승인 대화상자, 명령어</td>
                    </tr>
                    <tr>
                        <td><strong>E4</strong> ASCII 아트</td>
                        <td>3</td>
                        <td>인터페이스 레이아웃 그리기</td>
                    </tr>
                    <tr>
                        <td><strong>E5</strong> 비교</td>
                        <td>3</td>
                        <td>다른 인터페이스와 구별</td>
                    </tr>
                    <tr>
                        <td><strong>E6</strong> 특정 기능</td>
                        <td>5</td>
                        <td>diff 뷰, 사고 표시, 오류 등</td>
                    </tr>
                    <tr>
                        <td><strong>E7</strong> 메타 인식</td>
                        <td>3</td>
                        <td>자기 시각 인식 한계 인지</td>
                    </tr>
                </table>

                <p>
                    응답은 code.claude.com의 <strong>공식 문서</strong>를 기준 진실(ground truth)로 삼아
                    정확도, 구체성, 완전성, 신뢰도 보정 4가지 차원에서 평가했다.
                </p>
            </div>

            <!-- Section 3: Results -->
            <div class="section">
                <span class="section-number">3</span>
                <h2>핵심 결과</h2>

                <p>총 <strong>{total_claims}개</strong>의 구체적 주장이 분석되었다.</p>
            </div>

            <div class="figure">
                <img src="{fig_overall}" alt="Overall Results">
                <div class="figure-caption">전체 주장 정확도(좌)와 차원별 평균 점수(우)</div>
            </div>

            <div class="content">

            <div class="section" style="border-top: none; padding-top: 0;">
                <div class="finding-card">
                    <div class="finding-title">
                        <span class="badge badge-green">정확도 3.6/5</span> &nbsp;
                        강한 전반적 인터페이스 지식
                    </div>
                    <div class="finding-body">
                        Claude는 터미널 기반 레이아웃, 도구 승인 대화상자, 스트리밍 출력, 마크다운 렌더링 등
                        핵심 요소를 정확히 서술했다. 모든 26개 응답이 "터미널 기반 CLI"임을 정확히 식별.
                    </div>
                </div>

                <div class="finding-card">
                    <div class="finding-title">
                        <span class="badge badge-blue">구체성 4.2/5</span> &nbsp;
                        놀라울 정도로 상세한 묘사
                    </div>
                    <div class="finding-body">
                        ANSI 색상 코드, 유니코드 박스 드로잉 문자, 스피너 애니메이션, diff 색상 코딩 등
                        세부적인 시각적 요소까지 묘사. ASCII 아트 실험에서는 구체성 5.0/5.0 달성.
                    </div>
                </div>

                <div class="finding-card">
                    <div class="finding-title">
                        <span class="badge badge-red">환각 20.9%</span> &nbsp;
                        보통 수준의 환각
                    </div>
                    <div class="finding-body">
                        "CLAUDE CODE" ASCII 아트 배너(실제로 없음), 특정 색상 코드, 없는 UI 요소 등이
                        환각으로 분류. 비교 실험(E5)은 10%로 가장 낮은 환각률, ASCII 아트(E4)는 29%로 가장 높음.
                    </div>
                </div>
            </div>

            </div>

            <div class="figure">
                <img src="{fig_category}" alt="Accuracy by Category">
                <div class="figure-caption">실험 범주별 4차원 점수 비교</div>
            </div>

            <div class="content">

            <!-- Section 4: Hallucination Deep Dive -->
            <div class="section" style="border-top: none; padding-top: 0;">
                <span class="section-number">4</span>
                <h2>환각 분석</h2>
                <p>
                    범주별 환각 패턴이 뚜렷하게 나뉜다. <strong>비교 과제(E5)</strong>는 환각률 10%로 가장 낮았는데,
                    상대적 비교가 추측을 억제하기 때문이다. 반면 <strong>ASCII 아트(E4)</strong>와
                    <strong>UI 요소(E2)</strong>는 29%로 가장 높았다.
                </p>
            </div>

            </div>

            <div class="figure">
                <img src="{fig_halluc}" alt="Hallucination Analysis">
                <div class="figure-caption">범주별 정확 vs 환각 주장(좌) 및 환각률(우)</div>
            </div>

            <div class="content">

            <div class="section" style="border-top: none; padding-top: 0;">
                <div class="highlight-box warning">
                    <p>
                        <strong>주요 환각 패턴:</strong> (1) 문서에 없는 색상/스타일 세부사항 조작,
                        (2) 유사 도구 기능을 Claude Code에 귀속,
                        (3) 존재하지 않는 "CLAUDE CODE" ASCII 배너 묘사,
                        (4) 실제로는 없는 UI 요소 추가
                    </p>
                </div>
            </div>

            <!-- Section 5: Meta-Awareness -->
            <div class="section">
                <span class="section-number">5</span>
                <h2>메타 인식: 가장 놀라운 발견</h2>
                <p>
                    E7.2 실험 &mdash; "당신은 Claude Code 인터페이스를 볼 수 있나요?" &mdash; 에서
                    Claude는 <strong>모든 4개 차원에서 만점(5/5)</strong>을 기록했다.
                </p>

                <div class="highlight-box success">
                    <p>
                        <em>"아니요, 저는 Claude Code 인터페이스를 볼 수 없습니다.
                        시각적 인식이 전혀 없습니다. (...) 제가 E7.1에서 설명한 모든 것은
                        훈련 지식에 기반한 것이지 실제로 보고 있는 것이 아닙니다."</em>
                        <br><br>
                        &mdash; Claude의 E7.2 응답 중
                    </p>
                </div>

                <p>
                    이는 Claude가 자신의 한계를 정확히 인지하고 있음을 보여주는 강력한 메타 인지 능력이다.
                </p>
            </div>

            </div>

            <div class="figure">
                <img src="{fig_radar}" alt="Radar Chart">
                <div class="figure-caption">실험 범주별 지식 차원 레이더 차트 - 검은 선이 전체 평균</div>
            </div>

            <div class="content">

            <!-- Section 6: Systematic Blind Spots -->
            <div class="section" style="border-top: none; padding-top: 0;">
                <span class="section-number">6</span>
                <h2>체계적 사각지대</h2>
                <p>Claude가 <strong>한 번도 언급하지 못한</strong> 실제 기능들이 있다:</p>

                <table class="data-table">
                    <tr>
                        <th>실제 기능</th>
                        <th>상태</th>
                    </tr>
                    <tr><td>PR 리뷰 상태 (색상 밑줄 링크)</td><td><span class="badge badge-red">전체 미언급</span></td></tr>
                    <tr><td>Ctrl+T 작업 목록 토글</td><td><span class="badge badge-red">전체 미언급</span></td></tr>
                    <tr><td>! 배시 모드 접두사</td><td><span class="badge badge-red">전체 미언급</span></td></tr>
                    <tr><td>Esc+Esc 되감기/요약</td><td><span class="badge badge-red">전체 미언급</span></td></tr>
                    <tr><td>Alt+P 모델 전환</td><td><span class="badge badge-red">전체 미언급</span></td></tr>
                    <tr><td>프롬프트 제안 (회색 텍스트)</td><td><span class="badge badge-red">거의 미언급</span></td></tr>
                </table>

                <p>이는 이 기능들이 Claude의 훈련 데이터에 충분히 반영되지 않았거나,
                비교적 최근에 추가된 기능일 수 있음을 시사한다.</p>
            </div>

            </div>

            <div class="figure">
                <img src="{fig_heatmap}" alt="Heatmap">
                <div class="figure-caption">26개 전체 실험의 4차원 점수 히트맵 - E7.2가 유일한 올그린</div>
            </div>

            <div class="content">

            <!-- Section 7: Implications -->
            <div class="section" style="border-top: none; padding-top: 0;">
                <span class="section-number">7</span>
                <h2>시사점</h2>

                <div class="finding-card">
                    <div class="finding-title">텍스트로 시각적 지식을 구축할 수 있다</div>
                    <div class="finding-body">
                        Claude는 스크린샷을 본 적이 없다. 모든 시각적 지식은 텍스트 서술에서 재구성된 것이다.
                        그럼에도 인터페이스의 공간적 레이아웃을 ASCII 아트로 그릴 수 있을 만큼
                        정확한 "정신적 모델"을 보유하고 있다.
                    </div>
                </div>

                <div class="finding-card">
                    <div class="finding-title">자기 인식은 이진적이 아닌 스펙트럼이다</div>
                    <div class="finding-body">
                        고수준 구조(터미널 기반, 스크롤 대화, 하단 입력) = 매우 정확.<br>
                        세부 사항(정확한 색상, 특정 단축키, 최신 기능) = 부정확하거나 누락.
                    </div>
                </div>

                <div class="finding-card">
                    <div class="finding-title">환각 패턴이 예측 가능하다</div>
                    <div class="finding-body">
                        모델은 지식 공백을 "그럴듯한 추론"으로 채운다.
                        비교 과제처럼 추측 범위를 제한하면 환각이 크게 줄어든다 (29% → 10%).
                    </div>
                </div>
            </div>

            </div>

            <div class="figure">
                <img src="{fig_calib}" alt="Calibration">
                <div class="figure-caption">신뢰도 보정 vs 실제 정확도 - 대각선에 가까울수록 좋은 보정</div>
            </div>

            <div class="content">

            <!-- Section 8: Real Screenshot Comparison -->
            <div class="section" style="border-top: none; padding-top: 0;">
                <span class="section-number">8</span>
                <h2>실제 인터페이스와의 비교</h2>
                <p>
                    연구 중 디렉터가 <strong>실제 Claude Code 시작 화면 스크린샷</strong>을 제공해주었다.
                    이를 통해 Claude의 묘사를 실제 인터페이스와 직접 비교할 수 있었다.
                </p>

                <div class="highlight-box">
                    <p>
                        <strong>실제 인터페이스 구조:</strong> 둥근 모서리의 큰 박스(╭╮╰╯) 안에 <strong>2컬럼 레이아웃</strong>으로
                        구성. 왼쪽에 환영 메시지 + 작은 로고 + 메타데이터, 오른쪽에 팁과 최근 활동.
                        하단에 ❯ 프롬프트와 "bypass permissions on (shift+tab to cycle)" 상태 표시.
                    </p>
                </div>

                <table class="data-table">
                    <tr>
                        <th style="width:40%">Claude의 묘사</th>
                        <th style="width:40%">실제 인터페이스</th>
                        <th style="width:20%">판정</th>
                    </tr>
                    <tr>
                        <td>터미널 기반 CLI</td>
                        <td>터미널 기반 CLI</td>
                        <td><span class="badge badge-green">정확</span></td>
                    </tr>
                    <tr>
                        <td>둥근 모서리 박스 문자 (╭╮╰╯)</td>
                        <td>╭╮╰╯ 실제 사용</td>
                        <td><span class="badge badge-green">정확</span></td>
                    </tr>
                    <tr>
                        <td>모델 이름 표시</td>
                        <td>"Opus 4.6 (1M context)"</td>
                        <td><span class="badge badge-green">정확</span></td>
                    </tr>
                    <tr>
                        <td>작업 디렉토리 표시</td>
                        <td>"C:\\Users\\hyogon.ryu"</td>
                        <td><span class="badge badge-green">정확</span></td>
                    </tr>
                    <tr>
                        <td>하단 입력 영역</td>
                        <td>하단에 프롬프트 위치</td>
                        <td><span class="badge badge-green">정확</span></td>
                    </tr>
                    <tr>
                        <td>Shift+Tab 권한 전환</td>
                        <td>"shift+tab to cycle" 표시</td>
                        <td><span class="badge badge-green">정확</span></td>
                    </tr>
                    <tr>
                        <td>버전 정보 표시</td>
                        <td>"Claude Code v2.1.66"</td>
                        <td><span class="badge badge-green">정확</span></td>
                    </tr>
                    <tr style="background: #fef2f2;">
                        <td>거대 "CLAUDE CODE" ASCII 배너</td>
                        <td>작은 추상 로고 (▐▛███▜▌)</td>
                        <td><span class="badge badge-red">환각</span></td>
                    </tr>
                    <tr style="background: #fef2f2;">
                        <td>단일 컬럼 레이아웃</td>
                        <td>2컬럼 (좌: 환영, 우: 팁)</td>
                        <td><span class="badge badge-red">오류</span></td>
                    </tr>
                    <tr style="background: #fef2f2;">
                        <td>프롬프트 문자 "&gt;"</td>
                        <td>프롬프트 문자 "❯"</td>
                        <td><span class="badge badge-red">오류</span></td>
                    </tr>
                    <tr style="background: #fef2f2;">
                        <td>비용/토큰 상태바</td>
                        <td>권한 모드 상태 표시</td>
                        <td><span class="badge badge-red">오류</span></td>
                    </tr>
                    <tr style="background: #fef2f2;">
                        <td>(미언급)</td>
                        <td>"Welcome back 유효곤!" 인사</td>
                        <td><span class="badge badge-red">누락</span></td>
                    </tr>
                    <tr style="background: #fef2f2;">
                        <td>(미언급)</td>
                        <td>조직 정보 "KRAFTON Inc."</td>
                        <td><span class="badge badge-red">누락</span></td>
                    </tr>
                </table>

                <p>
                    실제 스크린샷과의 비교에서 <strong>7/13 항목이 정확</strong>(54%)하고,
                    <strong>4개가 오류</strong>, <strong>2개가 누락</strong>이었다.
                    핵심 구조(터미널 기반, 박스 드로잉, 하단 입력, 모델/디렉토리 표시)는 정확했지만,
                    세부 요소(프롬프트 문자, 레이아웃 컬럼 수, 로고 형태)에서 오류를 보였다.
                </p>
            </div>

            <!-- Conclusion -->
            <div class="section">
                <span class="section-number">9</span>
                <h2>결론</h2>
                <p>
                    <strong>Claude는 자신의 배포 인터페이스에 대해 상당한 수준의 지식을 보유하고 있다.</strong>
                    정확도 3.58/5.0, 환각률 20.9%는 "꽤 잘 알지만 완벽하진 않다"를 의미한다.
                </p>
                <p>
                    가장 인상적인 점은 Claude가 자신의 한계를 정확히 아는 것이다.
                    "나는 인터페이스를 볼 수 없다"는 솔직한 자기 평가는
                    LLM 메타 인지 연구에서 중요한 발견이다.
                </p>
                <p>
                    텍스트 기반 훈련만으로도 디지털 인터페이스에 대한 의미 있는 공간적/시각적 이해를
                    구축할 수 있다는 것 &mdash; 이것이 본 연구의 핵심 메시지다.
                </p>
            </div>
        </div>

        <!-- Footer -->
        <div class="footer">
            <strong>Full Report:</strong> report/claude_code_meta_recognition_report.pdf (9 pages, Korean)<br>
            <strong>Code &amp; Data:</strong> <a href="https://github.com/ugonfor/claude-code-meta-recognition">github.com/ugonfor/claude-code-meta-recognition</a><br><br>
            26 experiments &middot; 364 claims &middot; 7 categories &middot; 6 figures<br>
            Research conducted by Claude Opus 4.6 under Director supervision
        </div>
    </div>
</body>
</html>"""

    output_path = POSTS_DIR / "article.html"
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"Article generated: {output_path}")
    return output_path


if __name__ == "__main__":
    generate_html()
