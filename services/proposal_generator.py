"""
Research Paper Generator — Academic Draft Quality Output.
All Groq calls routed through shared GroqClient for caching and rate-limit safety.
Generates a properly structured academic paper draft suitable as a starting point
for real submission.
"""

import os
from typing import List, Dict
from datetime import datetime
from gemini_client import get_client


# ── Context builders ──────────────────────────────────────────────────────────

def _paper_ctx(papers: List[Dict], n: int = 25) -> str:
    lines = []
    for i, p in enumerate(papers[:n], 1):
        title    = p.get("title", "Untitled").strip()
        authors  = p.get("authors", [])
        auth_str = ", ".join(authors[:3]) + (" et al." if len(authors) > 3 else "")
        year     = p.get("year") or p.get("published", "")[:4] or "n.d."
        abstract = (p.get("abstract", "") or "").strip()[:400].replace("\n", " ")
        lines.append(
            f"[Paper {i}]\n"
            f"Title: {title}\n"
            f"Authors: {auth_str}\n"
            f"Year: {year}\n"
            f"Abstract: {abstract}...\n"
        )
    return "\n".join(lines)


def _gap_ctx(gaps: Dict) -> str:
    lines = []
    for gtype, glist in gaps.items():
        for i, g in enumerate(glist, 1):
            text     = g.get("proposal_ready_gap") or g.get("gap", "")
            opp      = g.get("opportunity", "")
            sev      = g.get("severity", "medium")
            evid     = g.get("evidence", [])
            evid_str = (", ".join(evid[:2]) if isinstance(evid, list) else str(evid))[:150]
            lines.append(
                f"[{gtype.upper()} GAP #{i}]\n"
                f"  Description : {text}\n"
                f"  Severity    : {sev}\n"
                f"  Opportunity : {opp}\n"
                f"  Evidence    : {evid_str}\n"
            )
    return "\n".join(lines) if lines else "Several methodological and empirical gaps identified."


def _safe_call(prompt: str, fallback: str, max_retries: int = 3,
               min_length: int = 400) -> str:
    """
    Call Groq via shared client.
    Retries up to max_retries times if response is too short.
    """
    client = get_client()
    for attempt in range(max_retries):
        text = client.generate(
            prompt,
            fallback="",
            use_cache=(attempt == 0),
        )
        if text and len(text) >= min_length:
            return text
        if text and attempt < max_retries - 1:
            prompt = (
                prompt
                + f"\n\nCRITICAL: Your previous answer was too short ({len(text)} chars). "
                f"Write the full section — minimum {min_length} characters. Do not truncate."
            )
    return fallback


# ── Paper generator class ─────────────────────────────────────────────────────

class PaperGenerator:

    def __init__(self, papers: List[Dict], gaps: Dict):
        self.papers    = papers
        self.gaps      = gaps
        self.paper_ctx = _paper_ctx(papers)
        self.gap_ctx   = _gap_ctx(gaps)
        self.topic     = self._infer_topic()

    def _infer_topic(self) -> str:
        titles = "; ".join(p.get("title", "") for p in self.papers[:12])
        result = _safe_call(
            f"Given these paper titles:\n{titles}\n\n"
            "State the single common research topic in 3–5 words.\n"
            "Rules: use only key nouns from the titles, no conjunctions, no 'and/or'.\n"
            "Return ONLY the short topic phrase — nothing else. Max 5 words.",
            "Research Topic",
            min_length=3
        )
        # Hard cap: take first 5 words only to prevent run-on topics
        words = result.strip().split()
        return " ".join(words[:5]) if words else "Research Topic" 

    def title(self) -> str:
        return _safe_call(
            f"Research topic: {self.topic}\n"
            f"Key gaps identified:\n{self.gap_ctx[:600]}\n\n"
            "Write ONE concise academic paper title (6–10 words maximum).\n"
            "Requirements:\n"
            "• Name the specific research domain\n"
            "• Indicate it is a review or gap analysis\n"
            "• Formal academic language\n"
            "• NO subtitle after a colon. NO punctuation at end.\n"
            "• Return ONLY the title — nothing else.",
            f"Systematic Gap Analysis in {self.topic}"
        )

    def abstract(self) -> str:
        return _safe_call(
            f"Write the Abstract for an academic research paper on: {self.topic}\n\n"
            f"Based on {len(self.papers)} reviewed papers.\n"
            f"Identified gaps:\n{self.gap_ctx[:900]}\n\n"
            "Structure (single flowing paragraph, 250–300 words):\n"
            "Background → Research problem → Objectives → Methodology → "
            "Key findings → Significance and contribution\n\n"
            "Requirements:\n"
            "• Formal academic tone — write as if submitting to a peer-reviewed journal\n"
            "• Mention the number of papers reviewed\n"
            "• Name 2–3 specific gap types found\n"
            "• State a concrete contribution\n"
            "• No bullet points. No section headings. One paragraph only.\n\n"
            "Begin writing immediately.",
            f"This paper presents a systematic review of {len(self.papers)} research works "
            f"in {self.topic}. Through comprehensive analysis, we identify critical gaps "
            "across methodological, empirical, and application dimensions.",
            min_length=900,
        )

    def introduction(self) -> str:
        return _safe_call(
            f"Write the Introduction section for a research paper on: {self.topic}\n\n"
            f"Papers reviewed:\n{self.paper_ctx[:2000]}\n\n"
            f"Identified gaps:\n{self.gap_ctx[:600]}\n\n"
            "Structure (650–750 words total):\n\n"
            "**Background** (2–3 paragraphs)\n"
            "  — Context and importance of {self.topic}\n"
            "  — Key developments in the reviewed literature\n"
            "  — Why this area is relevant now\n\n"
            "**Problem Statement** (1 paragraph)\n"
            "  — Clearly state what is missing or unresolved\n"
            "  — Reference specific gaps from the reviewed papers\n\n"
            "**Research Objectives** (1 paragraph)\n"
            "  — List 3–4 specific objectives this paper addresses\n"
            "  — Each objective must be measurable and grounded in the gaps above\n\n"
            "**Paper Organisation** (1 short paragraph)\n"
            "  — Briefly state what each section covers\n\n"
            "Requirements:\n"
            "• Formal academic prose — no bullet lists\n"
            "• Bold the sub-heading labels as shown above\n"
            "• Do not restate the abstract verbatim\n"
            "• Begin directly with '**Background**'",
            f"**Background**\n\nThe field of {self.topic} has seen substantial development "
            "over recent years.\n\n**Problem Statement**\n\nDespite this progress, "
            "critical gaps remain that limit the field's advancement.\n\n"
            "**Research Objectives**\n\nThis paper systematically identifies and analyses "
            "these gaps.\n\n**Paper Organisation**\n\nSection 2 reviews the literature. "
            "Section 3 presents the gap analysis. Section 4 concludes.",
            min_length=2500,
        )

    def literature_review(self) -> str:
        prompt = f"""Write the Literature Review section for an academic research paper.

TOPIC: {self.topic}

PAPERS TO REVIEW (cite these — do NOT invent authors or findings):
{self.paper_ctx}

Write 950–1150 words using EXACTLY these sub-sections (bold headings):

**Overview** (~120 words)
  — Scope of the reviewed literature: number of papers, year range, thematic coverage
  — 2–3 overarching themes or research directions
  — What this review contributes beyond existing surveys

**Foundational Work** (~250 words)
  — 4–5 seminal papers from the list; for each: author(s), year, method, key finding
  — Why each is considered foundational to the topic
  — Cite as (Author et al., Year) using actual names above

**Methodological Diversity** (~250 words)
  — 4–5 papers with distinct methodologies from the list
  — Compare and contrast their approaches, strengths, and limitations
  — Note where methods are complementary or in tension

**Recent Advances** (~250 words)
  — 4–5 of the most recent papers from the list
  — What new ground they break relative to earlier work
  — How they build on or challenge prior findings

**Synthesis and Transition** (~180 words)
  — Converging insights across all reviewed papers
  — Contradictions, underexplored directions, and emerging questions
  — Natural transition: "These observations motivate the gap analysis in Section 3."

FORMATTING RULES:
— Bold headings exactly as shown. Flowing academic prose — NO bullet points.
— Cite as (FirstAuthor et al., Year). Use actual author names from the paper list.
— Begin directly with "**Overview**". Return only the section body."""

        fallback = f"""**Overview**

The literature on {self.topic} spans {len(self.papers)} papers reviewed here, covering
work from foundational contributions through recent advances. Three primary themes emerge:
methodological innovation, empirical validation, and application breadth.

**Foundational Work**

Early research established the theoretical and methodological foundations that continue
to shape the field today, introducing core concepts and evaluation protocols.

**Methodological Diversity**

Researchers have adopted diverse approaches, ranging from theoretical frameworks to
large-scale empirical studies, each contributing distinct perspectives and insights.

**Recent Advances**

Recent publications have introduced novel techniques, expanded evaluation scope, and
begun to address limitations identified in earlier work.

**Synthesis and Transition**

Across all reviewed papers, a consistent finding emerges: while individual contributions
are robust, collective coverage leaves significant areas unexplored. These observations
motivate the gap analysis in Section 3."""

        return _safe_call(prompt, fallback, max_retries=3, min_length=4000)

    def gap_analysis(self) -> str:
        prompt = f"""Write the Gap Analysis section for a research paper on: {self.topic}

PAPERS REVIEWED:
{self.paper_ctx[:1800]}

DETECTED GAPS (base your analysis ONLY on these):
{self.gap_ctx}

Write 500–650 words structured as follows:

Opening paragraph (4–5 lines):
  — Introduce the gap analysis, how it was conducted, and what the {len(self.papers)} papers reveal
  — Reference the specific gap categories below

Gap bullets (for each gap below, write one bullet in this format):
  • **[Concise gap name]** — Explanation tying the gap to specific papers or methods above.
    Why this gap exists. Why closing it matters. (2–3 sentences per bullet)

Closing paragraph (3–4 lines):
  — Synthesise the gaps into a coherent research agenda
  — Transition to the Conclusion: "Addressing these gaps constitutes the primary
    contribution of the research agenda outlined in Section 4."

REQUIREMENTS:
— Do NOT use generic section labels (not "Methodological Gap" as a header — embed it in text)
— Do NOT invent gaps not present in the DETECTED GAPS section above
— Every bullet must name a specific technique, dataset, or paper from the context
— Formal academic prose
— Begin directly with the opening paragraph"""

        fallback = (
            f"Analysis of the {len(self.papers)} reviewed papers on {self.topic} "
            "reveals several important research gaps that collectively define a clear agenda "
            "for future investigation.\n\n"
            "• **Limited methodological integration** — Current papers apply individual "
            "techniques in isolation despite evidence that combined approaches may yield "
            "stronger results across the reviewed settings.\n\n"
            "• **Insufficient evaluation diversity** — Studies rely on a narrow range of "
            "experimental conditions, which constrains the generalisability of reported findings.\n\n"
            "• **Absence of real-world validation** — Most reviewed papers conduct laboratory "
            "evaluations only; deployment in practical settings remains unexplored.\n\n"
            "Addressing these gaps constitutes the primary contribution of the research agenda "
            "outlined in Section 4."
        )
        return _safe_call(prompt, fallback, max_retries=3, min_length=2000)

    def conclusion(self) -> str:
        prompt = f"""Write the Conclusion section for a research paper on: {self.topic}

Papers reviewed: {len(self.papers)}

Identified gaps:
{self.gap_ctx[:1000]}

Write 420–500 words using EXACTLY these sub-sections (bold headings):

**Summary of Findings** (~120 words)
  — Key insights from the literature review
  — Total gaps identified and their categories
  — Most significant patterns across the reviewed papers

**Significance of Identified Gaps** (~100 words)
  — Why these specific gaps matter for researchers and practitioners
  — Implications for the direction of the field

**Recommendations for Future Research** (~180 words)
  — 4–5 concrete, specific research directions that directly address the identified gaps
  — For each: state the direction, which gap it addresses, a concrete approach, expected impact
  — Prioritise by feasibility and significance

**Closing Statement** (~60 words)
  — Forward-looking, motivating paragraph
  — Emphasise the research opportunities the gaps represent

REQUIREMENTS:
— Bold headings exactly as shown. Formal academic prose — NO bullet points.
— Begin directly with "**Summary of Findings**"
— Do not repeat the abstract verbatim"""

        fallback = f"""**Summary of Findings**

This systematic review analysed {len(self.papers)} papers on {self.topic}, identifying
critical gaps across methodological, empirical, and application dimensions. The analysis
reveals that while the field has progressed substantially, key areas remain underexplored
and underspecified, limiting both theoretical coherence and practical adoption.

**Significance of Identified Gaps**

The gaps identified carry direct implications for researchers seeking to make meaningful
contributions and for practitioners seeking to apply current methods reliably. Addressing
them is a prerequisite for the field reaching its next phase of maturity.

**Recommendations for Future Research**

Researchers should prioritise the integration of complementary methodologies identified
across reviewed papers, the expansion of empirical evaluation to underrepresented settings,
and the development of replicable protocols that bridge the laboratory-to-practice divide.
Each direction is tractable and builds directly on existing literature.

**Closing Statement**

The gaps documented here are not obstacles but invitations. The reviewed literature
provides a strong foundation; the research community is well-positioned to close these
gaps and substantially advance {self.topic} in the years ahead."""

        return _safe_call(prompt, fallback, max_retries=3, min_length=1500)

    def references(self) -> List[str]:
        refs = []
        for p in self.papers[:30]:
            title   = p.get("title", "Untitled").strip()
            authors = p.get("authors", [])
            year    = p.get("year") or p.get("published", "")[:4] or "n.d."
            url     = p.get("url") or p.get("arxiv_url", "")

            if authors:
                fmt = []
                for a in authors[:6]:
                    parts = a.strip().split()
                    if len(parts) >= 2:
                        last = parts[-1]
                        ini  = ". ".join(pt[0].upper() for pt in parts[:-1] if pt) + "."
                        fmt.append(f"{last}, {ini}")
                    elif parts:
                        fmt.append(parts[0])
                if len(authors) > 6:
                    fmt.append("et al.")
                auth_str = (
                    ", & ".join(fmt) if len(fmt) > 1 else (fmt[0] if fmt else "Unknown Author(s)")
                )
                ref = f"{auth_str} ({year}). {title}. *arXiv preprint*."
            else:
                ref = f"Unknown Author(s). ({year}). {title}. *arXiv preprint*."

            if url:
                ref += f" Retrieved from {url}"
            refs.append(ref)
        return refs

    def _get_year_range(self) -> str:
        years = []
        for p in self.papers:
            try:
                years.append(int(p.get("year") or p.get("published", "")[:4]))
            except Exception:
                pass
        return f"{min(years)}–{max(years)}" if years else "recent years"


# ── Markdown assembler ────────────────────────────────────────────────────────

def _build_markdown(title: str, sections: Dict, refs: List[str], meta: Dict) -> str:
    ref_block = "\n\n".join(f"{i}. {r}" for i, r in enumerate(refs, 1))

    return f"""# {title}

---

| Field | Value |
|---|---|
| **Date Generated** | {meta['generated_at'][:10]} |
| **Papers Analysed** | {meta['num_papers']} |
| **Research Topic** | {meta['topic']} |

> *This document is an AI-generated draft to be used as a starting point.*
> *Review, expand, and verify all content before any submission.*

---

## Abstract

{sections['abstract']}

---

## 1. Introduction

{sections['introduction']}

---

## 2. Literature Review

{sections['literature_review']}

---

## 3. Gap Analysis

{sections['gap_analysis']}

---

## 4. Conclusion

{sections['conclusion']}

---

## References

{ref_block}

---

*Auto-generated by ResearchIt v3.0 · {meta['generated_at'][:16]}*
"""


# ── Public entry point ────────────────────────────────────────────────────────

def generate_research_paper(papers: List[Dict], gaps: Dict) -> Dict:
    """
    Generate a complete academic paper draft.
    All Groq calls go through shared GroqClient — rate-limit safe.
    """
    if not os.getenv("GROQ_API_KEY"):
        return {
            "error": (
                "GROQ_API_KEY not set. Add it to your .env file. "
                "Get your free key at https://console.groq.com/"
            )
        }
    if not papers:
        return {"error": "No papers available. Please fetch papers first."}

    try:
        gen = PaperGenerator(papers, gaps or {})
    except Exception as e:
        return {"error": f"Failed to initialise generator: {e}"}

    sections = {
        "abstract":          gen.abstract(),
        "introduction":      gen.introduction(),
        "literature_review": gen.literature_review(),
        "gap_analysis":      gen.gap_analysis(),
        "conclusion":        gen.conclusion(),
    }

    title = gen.title()
    refs  = gen.references()
    meta  = {
        "generated_at": datetime.now().isoformat(),
        "num_papers":   len(papers),
        "topic":        gen.topic,
        "year_range":   gen._get_year_range(),
    }

    return {
        "title":      title,
        "sections":   sections,
        "references": refs,
        "markdown":   _build_markdown(title, sections, refs, meta),
        "metadata":   meta,
        "error":      None,
    }