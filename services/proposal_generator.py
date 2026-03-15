"""
Research Paper Generator — Enhanced with detailed, structured prompts.
IMPROVEMENTS:
  - Literature Review: Forces proper thematic organization with real paper citations
  - Gap Analysis: Demands structured sub-sections with evidence and reasoning
  - Conclusion: Enforces concrete, actionable recommendations
All sections now have multi-stage prompts with explicit structure requirements.
"""

import os
from typing import List, Dict
from datetime import datetime
import google.generativeai as genai


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def _paper_ctx(papers: List[Dict], n: int = 25) -> str:
    """Build detailed context with ALL paper metadata for better citations."""
    lines = []
    for i, p in enumerate(papers[:n], 1):
        title    = p.get("title","Untitled").strip()
        authors  = p.get("authors",[])
        auth_str = ", ".join(authors[:3]) + (" et al." if len(authors) > 3 else "")
        year     = p.get("year") or p.get("published","")[:4] or "n.d."
        abstract = (p.get("abstract","") or "")[:400].replace("\n"," ")
        lines.append(
            f"[Paper {i}]\n"
            f"Title: {title}\n"
            f"Authors: {auth_str}\n"
            f"Year: {year}\n"
            f"Abstract: {abstract}...\n"
        )
    return "\n".join(lines)


def _gap_ctx(gaps: Dict) -> str:
    """Detailed gap context with all metadata."""
    lines = []
    for gtype, glist in gaps.items():
        for i, g in enumerate(glist, 1):
            text = g.get("proposal_ready_gap") or g.get("gap","")
            opp  = g.get("opportunity","")
            sev  = g.get("severity","medium")
            evid = g.get("evidence", [])
            evid_str = (", ".join(evid[:2]) if isinstance(evid, list) else str(evid))[:150]
            lines.append(
                f"[{gtype.upper()} GAP #{i}]\n"
                f"  Description: {text}\n"
                f"  Severity: {sev}\n"
                f"  Opportunity: {opp}\n"
                f"  Evidence: {evid_str}\n"
            )
    return "\n".join(lines) if lines else "Several methodological and empirical gaps identified."


def _safe_call(model, prompt: str, fallback: str, max_retries: int = 2) -> str:
    """Call Gemini with retries; never return None."""
    for attempt in range(max_retries):
        try:
            resp = model.generate_content(prompt)
            text = (resp.text or "").strip()
            if text and len(text) > 100:  # Ensure substantial response
                return text
        except Exception:
            if attempt == max_retries - 1:
                return fallback
    return fallback


# ─────────────────────────────────────────────────────────────────────────────
# Section generators — ENHANCED
# ─────────────────────────────────────────────────────────────────────────────

class PaperGenerator:
    def __init__(self, model, papers: List[Dict], gaps: Dict):
        self.model     = model
        self.papers    = papers
        self.gaps      = gaps
        self.paper_ctx = _paper_ctx(papers)
        self.gap_ctx   = _gap_ctx(gaps)
        self.topic     = self._infer_topic()

    def _infer_topic(self) -> str:
        titles = "; ".join(p.get("title","") for p in self.papers[:12])
        return _safe_call(
            self.model,
            f"""
        Given these paper titles:

        {titles}

        Return the COMMON research topic.
        Use only words from titles.
        Do not invent new domain.
        Return 3-6 words only.
        """,
            "Research Topic"    
        )
        

    def title(self) -> str:
        return _safe_call(
            self.model,
            f"Research topic: {self.topic}\n"
            f"Key gaps identified:\n{self.gap_ctx[:800]}\n\n"
            "Write a single compelling academic research paper title (12-16 words). "
            "Requirements:\n"
            "- Clearly state the research domain\n"
            "- Mention the approach (systematic review / gap analysis)\n"
            "- Indicate the contribution\n"
            "- Use formal academic language\n"
            "- NO quotes, NO punctuation at end\n\n"
            "Return ONLY the title.",
            f"A Systematic Review and Gap Analysis in {self.topic}: Identifying Research Opportunities"
        )

    def abstract(self) -> str:
        return _safe_call(
            self.model,
            f"Write the Abstract section of a research paper on: {self.topic}\n\n"
            f"Based on analysis of {len(self.papers)} papers.\n"
            f"Key gaps identified:\n{self.gap_ctx[:1000]}\n\n"
            "Requirements:\n"
            "Write as if this will be submitted as a real research paper."
            "Use formal academic tone."
            "Use concrete methods."
            "Avoid generic statements."
            "- EXACTLY 250-300 words\n"
            "- Structure with these elements:\n"
            "  1. Background (why this topic matters)\n"
            "  2. Problem statement (what gaps exist)\n"
            "  3. Objectives (what this paper does)\n"
            "  4. Methodology (systematic review approach)\n"
            "  5. Key findings (main gaps discovered)\n"
            "  6. Significance (why these gaps matter)\n"
            "- Use formal academic English\n"
            "- Write as a single flowing paragraph OR clear logical flow\n"
            "- NO section headings, NO bullet points\n\n"
            "Return ONLY the abstract text.",
            f"This paper presents a systematic review of {len(self.papers)} research works "
            f"in {self.topic}. Through comprehensive analysis, we identify critical gaps "
            "across methodological, empirical, and theoretical dimensions. Our findings reveal "
            "opportunities for future research that could significantly advance the field."
        )

    def introduction(self) -> str:
        return _safe_call(
            self.model,
            f"Write the Introduction section of a research paper on: {self.topic}\n\n"
            f"Sample papers reviewed:\n{self.paper_ctx[:2000]}\n\n"
            f"Identified gaps:\n{self.gap_ctx[:700]}\n\n"
            "Requirements:\n"
            "- 650-750 words total\n"
            "Write as if this will be submitted as a real research paper."
            "Use formal academic tone."
            "Use concrete methods."
            "Avoid generic statements."
            "- Structure with bold inline sub-headings:\n"
            "  **Background** (2-3 paragraphs):\n"
            "    - Why this research area is important\n"
            "    - Recent growth and developments\n"
            "    - Real-world applications and impact\n"
            "  **Problem Statement** (1 paragraph):\n"
            "    - What critical gaps exist in current research\n"
            "    - Why these gaps need to be addressed\n"
            "  **Research Objectives** (1 paragraph):\n"
            "    - State 3-4 specific objectives of this review\n"
            "  **Paper Organisation** (1 short paragraph):\n"
            "    - Briefly describe what each subsequent section covers\n"
            "- Use flowing academic prose, NO bullet lists\n"
            "- Cite papers naturally where relevant\n\n"
            "Return ONLY the section body (no 'Introduction' heading).",
            f"**Background**\n\nThe rapid evolution of {self.topic} has created significant "
            "opportunities and challenges for researchers and practitioners worldwide. "
            "This paper systematically reviews existing literature to identify gaps and "
            "propose future directions.\n\n**Problem Statement**\n\nDespite extensive research, "
            "critical gaps remain in our understanding.\n\n**Research Objectives**\n\n"
            "This paper aims to identify and analyse these gaps systematically."
        )

    def literature_review(self) -> str:
        """COMPLETELY REWRITTEN with detailed requirements."""
        prompt = f"""You are writing the Literature Review section of an academic research paper.

TOPIC: {self.topic}

PAPERS TO REVIEW (cite these by author and year):
{self.paper_ctx}
IMPORTANT:
    Use ONLY the papers provided.
    Do not invent authors.
    Do not invent datasets.
    Do not invent methods.
    Every paragraph must refer to the given papers.

CRITICAL INSTRUCTIONS:
You MUST write 950-1150 words organized into these EXACT sub-sections with bold headings:
"Write as if this will be submitted as a real research paper."
            "Use formal academic tone."
            "Use concrete methods."
            "Avoid generic statements."
**Overview** (1 paragraph, ~120 words):
  - Summarize the breadth of literature: number of papers, year range, major publication venues
  - Identify 2-3 overarching themes or trends across the corpus
  - State what this review contributes

**Foundational Work** (~250 words):
  - Identify and discuss 4-5 seminal/early papers from the list above
  - For EACH paper: state author(s), year, what they established, methods used, key findings
  - Explain why these works are foundational
  - Cite as (Author, Year) — use the actual authors and years from the papers above

**Methodological Approaches** (~250 words):
  - Discuss 4-5 papers that use different methodologies
  - Compare and contrast their approaches
  - Analyze strengths and weaknesses of each method
  - Cite specific papers from the list above

**Recent Advances** (~250 words):
  - Focus on 4-5 recent papers (newest years from the list)
  - What new ground do they break?
  - What novel results do they achieve?
  - How do they build on earlier work?
  - Cite specific papers from the list above

**Synthesis** (~180 words):
  - What converging insights emerge across all themes?
  - Where do papers contradict each other?
  - What remains underexplored or poorly understood?
  - Transition naturally to the gap analysis that follows

FORMATTING RULES:
- Use bold headings exactly as shown above
- Write in flowing academic prose — NO bullet points
- Cite papers inline as (FirstAuthor et al., Year) or (FirstAuthor, Year)
- Use actual author names and years from the papers provided
- Vary your sentence structure
- Maintain formal academic tone throughout

Return ONLY the section body. Do NOT include a "Literature Review" heading.
Begin directly with "**Overview**"."""

        fallback = f"""**Overview**

The literature on {self.topic} spans {len(self.papers)} papers published between {self._get_year_range()}. 
Research has progressed through distinct phases, from foundational theoretical work to recent 
empirical advances. This review synthesizes current knowledge and identifies critical gaps.

**Foundational Work**

Early research established core principles and methodologies that continue to shape the field. 
Seminal contributions introduced key concepts and frameworks that subsequent studies build upon. 
These foundational papers demonstrated the feasibility and importance of systematic investigation in this domain.

**Methodological Approaches**

Researchers have employed diverse methodologies, ranging from theoretical modeling to empirical 
validation. Some studies favor experimental approaches, while others rely on observational data 
or simulation. Each methodology offers distinct advantages for addressing specific research questions.

**Recent Advances**

Recent work has pushed the boundaries of {self.topic} through novel techniques and datasets. 
Contemporary studies achieve improved performance and broader applicability compared to earlier 
approaches. Integration with related fields has opened new research directions.

**Synthesis**

Across all themes, the literature demonstrates steady progress in both theoretical understanding 
and practical applications. However, significant disagreements persist regarding optimal approaches 
and evaluation criteria. Several promising research directions remain largely unexplored, motivating 
the gap analysis that follows."""

        return _safe_call(self.model, prompt, fallback, max_retries=2)

    def gap_analysis(self) -> str:
        """COMPLETELY REWRITTEN with structured gap reporting."""
        n = len(self.papers)
        prompt = f"""
        You are writing the GAP ANALYSIS section of a research paper.

        TOPIC: {self.topic}

        PAPERS ANALYSED:
        {self.paper_ctx}

        DETECTED GAPS:
        {self.gap_ctx}

        Instructions:

        Write the gap section as a realistic research paper section.

        Rules:

        - DO NOT use headings like Methodological / Empirical / Theoretical
        - DO NOT write generic statements
        - DO NOT invent gaps
        - Use only the detected gaps and papers above
        - Write in academic style
        - Use bullet points for each gap
        - Each gap must be specific and based on papers

        Format:

        Write an introduction paragraph (4–5 lines)

        Then list gaps as bullet points like:

        • Gap 1 — explanation based on papers  
        • Gap 2 — explanation based on papers  
        • Gap 3 — explanation based on papers  
        • Gap 4 — explanation based on papers  

        Each bullet must:
        - mention technique / dataset / topic
        - relate to papers
        - explain why gap exists
        - explain why important

        End with 1 short concluding paragraph.
        """

        fallback = f"""
        The analysis of the reviewed papers reveals several important research gaps.

        • Limited combination of existing methods across the reviewed papers.
        • Few studies evaluate results on diverse datasets.
        • Several approaches lack real-world validation.
        • Some topics mentioned in the papers remain under-explored.

        These gaps indicate clear opportunities for future research.
        """

        return _safe_call(self.model, prompt, fallback, max_retries=2)

    def conclusion(self) -> str:
        """COMPLETELY REWRITTEN with concrete recommendations."""
        prompt = f"""You are writing the Conclusion section of an academic research paper.

TOPIC: {self.topic}
PAPERS REVIEWED: {len(self.papers)}

IDENTIFIED GAPS:
{self.gap_ctx[:1200]}

CRITICAL INSTRUCTIONS:
You MUST write 420-500 words organized into these EXACT sub-sections with bold headings:
"Write as if this will be submitted as a real research paper."
            "Use formal academic tone."
            "Use concrete methods."
            "Avoid generic statements."
**Summary of Findings** (~120 words):
  - Recap the main insights from the literature review
  - State the total number and types of gaps identified
  - Highlight the most significant patterns observed

**Significance of Gaps** (~100 words):
  - Explain why these gaps matter for the field
  - Discuss implications for researchers and practitioners
  - Connect to broader challenges in {self.topic}

**Recommendations for Future Research** (~180 words):
  - Provide 4-5 CONCRETE, SPECIFIC research directions
  - For EACH recommendation:
    * State it clearly and specifically
    * Explain which gap(s) it addresses
    * Suggest a concrete approach or methodology
    * Estimate the potential impact
  - Prioritize recommendations by feasibility and impact
  - Make recommendations actionable (researchers should know exactly what to do)

**Closing Statement** (~60 words):
  - End with a forward-looking, motivating paragraph
  - Emphasize the opportunities ahead
  - Leave readers inspired to address these gaps

FORMATTING RULES:
- Use bold headings exactly as shown above
- Write in formal academic prose — NO bullet points or numbered lists
- Be specific and concrete — avoid generic statements like "more research is needed"
- Good: "Future work should develop hybrid architectures combining X and Y, validated on diverse datasets including Z"
- Bad: "More research is needed in this area"

Return ONLY the section body. Do NOT include a "Conclusion" heading.
Begin directly with "**Summary of Findings**"."""

        fallback = f"""**Summary of Findings**

This systematic review analyzed {len(self.papers)} papers in {self.topic}, identifying critical gaps 
across methodological, empirical, theoretical, and application dimensions. The literature demonstrates 
substantial progress but reveals significant opportunities for future research.

**Significance of Gaps**

Addressing these gaps is essential for advancing both theoretical understanding and practical applications 
in {self.topic}. The identified gaps limit generalizability, restrict adoption in real-world contexts, 
and constrain the field's potential impact. Closing these gaps would substantially strengthen the 
research foundation.

**Recommendations for Future Research**

First, researchers should develop and validate hybrid methodological approaches that combine strengths 
of existing techniques while mitigating their weaknesses. Second, empirical work must expand beyond 
standard datasets to include diverse, real-world contexts that better represent practical deployment 
scenarios. Third, theoretical frameworks require development to explain observed phenomena and guide 
future investigations. Fourth, cross-domain applications should be explored systematically to identify 
transferable insights and broaden the field's impact. Finally, longitudinal studies tracking developments 
over time would provide valuable perspective on trends and trajectories.

**Closing Statement**

The gaps identified in this review represent not limitations but opportunities for impactful contributions. 
As {self.topic} continues to evolve, addressing these gaps will unlock new possibilities and strengthen 
the field's foundations for future growth."""

        return _safe_call(self.model, prompt, fallback, max_retries=2)

    def references(self) -> List[str]:
        """Enhanced reference formatting with better error handling."""
        refs = []
        for p in self.papers[:30]:
            title   = p.get("title","Untitled").strip()
            authors = p.get("authors",[])
            year    = p.get("year") or p.get("published","")[:4] or "n.d."
            url     = p.get("url") or p.get("arxiv_url","")
            
            if authors and len(authors) > 0:
                fmt = []
                for a in authors[:6]:
                    parts = a.strip().split()
                    if len(parts) >= 2:
                        last = parts[-1]
                        ini  = ". ".join(pt[0].upper() for pt in parts[:-1] if pt) + "."
                        fmt.append(f"{last}, {ini}")
                    elif len(parts) == 1:
                        fmt.append(parts[0])
                if len(authors) > 6:
                    fmt.append("et al.")
                auth_str = ", & ".join(fmt) if len(fmt) > 1 else (fmt[0] if fmt else "Unknown")
                ref = f"{auth_str} ({year}). {title}. *arXiv preprint*."
            else:
                ref = f"Unknown Author(s). ({year}). {title}. *arXiv preprint*."
            
            if url:
                ref += f" {url}"
            refs.append(ref)
        return refs

    def _get_year_range(self) -> str:
        """Helper to get year range for fallbacks."""
        years = []
        for p in self.papers:
            try:
                y = int(p.get("year") or p.get("published","")[:4])
                years.append(y)
            except:
                pass
        if years:
            return f"{min(years)}-{max(years)}"
        return "recent years"


# ─────────────────────────────────────────────────────────────────────────────
# Markdown assembler
# ─────────────────────────────────────────────────────────────────────────────

def _build_markdown(title, sections, refs, meta) -> str:
    ref_block = "\n\n".join(f"{i}. {r}" for i, r in enumerate(refs, 1))
    return f"""# {title}

---

**Date Generated:** {meta['generated_at'][:10]}  
**Papers Analysed:** {meta['num_papers']}  
**Research Topic:** {meta['topic']}

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

*Auto-generated by ResearchIt v3.0 as a starting draft. Review, expand, and verify all content before submission.*
"""


# ─────────────────────────────────────────────────────────────────────────────
# Public entry point
# ─────────────────────────────────────────────────────────────────────────────

def generate_research_paper(papers: List[Dict], gaps: Dict) -> Dict:
    """
    Generate a complete research paper with enhanced quality.

    Parameters
    ----------
    papers : list of paper dicts from ArXiv
    gaps   : detected_gaps or interpreted_gaps dict (both formats accepted)
             Pass {} if no gaps detected yet — paper still generates.

    Returns
    -------
    dict with keys: title, sections, references, markdown, metadata
    All sections guaranteed non-empty with quality fallbacks.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return {"error": "GEMINI_API_KEY not set. Add it to your .env file."}

    if not papers:
        return {"error": "No papers available. Please fetch papers first."}

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-2.5-flash")
    except Exception as e:
        return {"error": f"Failed to initialise Gemini: {e}"}

    gen = PaperGenerator(model, papers, gaps or {})

    # Generate each section with enhanced prompts
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
    }

    return {
        "title":      title,
        "sections":   sections,
        "references": refs,
        "markdown":   _build_markdown(title, sections, refs, meta),
        "metadata":   meta,
        "error":      None,
    }