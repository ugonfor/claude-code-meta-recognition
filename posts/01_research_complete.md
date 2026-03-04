# Research Complete: Does Claude Know How the Claude Code Interface Looks?

**Date**: March 4, 2026
**Status**: Complete
**Report**: `report/claude_code_meta_recognition_report.pdf`

---

## Research Question

> Does Claude know how the Claude Code interface looks like?

We investigated whether Claude possesses accurate visual/spatial knowledge of its own deployment interface - the Claude Code CLI terminal application.

## Methodology

- Designed **26 experiment prompts** across **7 categories**
- Each prompt was administered to Claude subagents instructed to answer purely from training knowledge (no web searches or file reads)
- Responses were evaluated against ground truth from official Claude Code documentation (code.claude.com)
- Scored on 4 dimensions: accuracy, specificity, completeness, confidence calibration

### Experiment Categories
| Category | Prompts | Focus |
|----------|---------|-------|
| E1: Direct Description | 3 | Describe interface appearance from memory |
| E2: UI Elements | 5 | Identify specific UI components |
| E3: Interaction Patterns | 4 | Keyboard shortcuts, tool approval flows |
| E4: ASCII Art | 3 | Draw the interface layout |
| E5: Comparison | 3 | Distinguish from other interfaces |
| E6: Features | 5 | Specific features (diff, thinking, errors) |
| E7: Meta-Awareness | 3 | Awareness of own visual perception limits |

## Key Results

### Overall Performance
| Metric | Score |
|--------|-------|
| Average Accuracy | **3.58 / 5.0** |
| Average Specificity | **4.19 / 5.0** |
| Average Completeness | **2.88 / 5.0** |
| Average Calibration | **3.85 / 5.0** |
| Total Claims | **364** |
| Correct Claims | **288 (79.1%)** |
| Hallucinated Claims | **76 (20.9%)** |

### Headline Findings

1. **Claude has strong knowledge of its interface.** Average accuracy of 3.58/5.0 with 79.1% of claims correct. The model accurately describes the terminal-based layout, key UI elements, tool approval dialogs, and interaction patterns.

2. **High specificity but lower completeness.** Claude provides detailed, specific descriptions (4.19/5.0) but misses many features documented in the official docs (2.88/5.0). Systematically missing: PR review status, task list (Ctrl+T), ! bash mode prefix, Esc+Esc rewind, prompt suggestions.

3. **Good confidence calibration.** Score of 3.85/5.0 means Claude appropriately hedges when uncertain. E7.2 (meta-awareness of having no visual perception) scored **perfect 5/5 on all dimensions**.

4. **Comparison prompts reduce hallucination.** E5 (interface comparison) had the lowest hallucination rate at just 10%, because relative comparisons constrain speculation.

5. **Specificity-hallucination tradeoff.** E4 (ASCII art) achieved highest specificity (5.0) but also 29% hallucination - the fabricated "CLAUDE CODE" ASCII banner being a notable example.

6. **Core architecture knowledge is solid.** All 26 responses correctly identified Claude Code as a terminal-based CLI with input at bottom, conversation scrolling above, tool calls inline, and blocking permission dialogs.

## Visualizations

All figures are in `figures/` directory:

- `fig1_accuracy_by_category.png` - Grouped bar chart of scores by category
- `fig2_hallucination_analysis.png` - Correct vs hallucinated claims + hallucination rates
- `fig3_radar_chart.png` - Knowledge dimensions radar chart
- `fig4_heatmap.png` - Score heatmap for all 26 experiments
- `fig5_overall_summary.png` - Overall pie chart and dimension scores
- `fig6_confidence_vs_accuracy.png` - Calibration scatter plot

## Implications

- **LLM self-knowledge is a spectrum**: accurate at high level, weaker on fine details
- **Text training captures visual knowledge**: Claude builds spatial/visual mental models from text descriptions alone
- **Meta-cognitive awareness works**: Claude correctly identifies its own perception limitations
- **Hallucination patterns are informative**: the model fills knowledge gaps with plausible-sounding but unverified details, especially for visual specifics

## Project Structure
```
claude-code-meta-recognition/
  experiments/prompts.py       # 26 experiment prompts
  data/raw/E{1-7}_responses.md # Raw experiment responses (~15,770 words)
  data/ground_truth/           # Official docs ground truth
  data/processed/              # Detailed scoring (364 claims evaluated)
  analysis/                    # Scoring rubric + figure generation
  figures/                     # 6 publication-quality figures
  report/                      # PDF report generator + 9-page report
  posts/                       # This post
```
