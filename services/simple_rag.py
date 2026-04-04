"""
simple_rag.py — AI-powered gap detection, research summary, and future topics.
- Research Summary: overall synthesis in bullet points (themes, NOT one-per-paper)
- Gap Detection: grounded in future scope sections of retrieved papers
- Future Topics: specific, well-written, varied directions
Uses shared GroqClient (gemini_client.py) for caching and rate-limit safety.
"""

import os
import streamlit as st
from gemini_client import get_client

_topic_model = None
_embedding_model = None


# ── Lazy BERTopic loader ──────────────────────────────────────────────────────

def load_models():
    global _topic_model, _embedding_model
    try:
        from sentence_transformers import SentenceTransformer
        from bertopic import BERTopic
    except Exception:
        return None
    if _embedding_model is None:
        _embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
    if _topic_model is None:
        _topic_model = BERTopic(
            embedding_model=_embedding_model,
            min_topic_size=2,
            nr_topics="auto"
        )
    return _topic_model


# ── Groq helper ───────────────────────────────────────────────────────────────

def _call_groq(prompt: str, fallback: str = "Could not generate a response.") -> str:
    try:
        result = get_client().generate(prompt, fallback=fallback)
        return result if result else fallback
    except Exception:
        return fallback


def _fix_spacing(text: str) -> str:
    """Ensure bullet points and section headers each start on a fresh line."""
    import re
    text = text.replace('\r\n', '\n').replace('\r', '\n')
    text = re.sub(r'\n(•|-)', r'\n\n\1', text)
    text = re.sub(r'\n(#{1,3} )', r'\n\n\1', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()


# ── Paper formatter ───────────────────────────────────────────────────────────

def _format_papers(papers_or_text) -> tuple:
    """
    Returns (paper_block: str, titles: List[str]).
    Uses abstract + summary. Extracts future-scope / limitation sentences explicitly.
    """
    if isinstance(papers_or_text, list) and papers_or_text:
        lines, titles = [], []
        for i, p in enumerate(papers_or_text[:15], 1):
            title    = p.get("title", "").strip()
            abstract = (p.get("abstract", "") or p.get("summary", "") or "").strip()[:500]
            if not title and not abstract:
                continue
            titles.append(title)
            lines.append(f"Paper {i}: {title}\nAbstract: {abstract}")
        return "\n\n".join(lines), titles
    text = papers_or_text if isinstance(papers_or_text, str) else ""
    return text[:5000], []


def _extract_future_scope(papers_or_text) -> str:
    """
    Pull out sentences that contain future-scope / limitation signals.
    These are the most reliable source of real research gaps.
    """
    import re
    future_keywords = [
        "future work", "future research", "future study", "in the future",
        "can be extended", "could be extended", "remains to be", "left for future",
        "open problem", "open question", "limitation", "we did not", "we could not",
        "does not address", "fails to", "cannot handle", "not yet", "still lacks",
        "further investigation", "warrants further", "needs to be explored",
        "scope for", "avenue for", "promising direction"
    ]

    papers = papers_or_text if isinstance(papers_or_text, list) else []
    collected = []

    for p in papers[:15]:
        title    = p.get("title", "Untitled")
        abstract = (p.get("abstract", "") or p.get("summary", "") or "")
        # Split into sentences
        sentences = re.split(r'(?<=[.!?])\s+', abstract)
        for sent in sentences:
            sent_lower = sent.lower()
            if any(kw in sent_lower for kw in future_keywords) and len(sent) > 40:
                collected.append(f'[{title}]: "{sent.strip()}"')

    return "\n".join(collected) if collected else ""


# ── Research Summary ──────────────────────────────────────────────────────────

def summarize_with_groq(text: str, papers=None) -> str:
    """
    Overall thematic synthesis of the paper collection as structured bullet points.
    NOT one-per-paper — this gives a high-level view across the corpus.
    """
    paper_block = text[:6000]

    prompt = f"""You are an academic research analyst. You have read a collection of research papers.
Write an overall thematic synthesis — NOT a list of individual paper summaries.

PAPERS:
{paper_block}

Write in this exact format using bullet points:

## 🔑 Core Research Theme
• One sentence stating the unifying topic across all these papers.

## 📌 Key Findings Across the Collection
• **[Finding 1]**: A key result or conclusion that appears in multiple papers. (1–2 sentences)
• **[Finding 2]**: Another cross-cutting finding, stated precisely. (1–2 sentences)
• **[Finding 3]**: A third insight, referencing specific methods or results. (1–2 sentences)
• **[Finding 4]**: One more notable pattern across the papers. (1–2 sentences)

## ⚙️ Methods Commonly Used
• **[Method]**: What it is and which type of papers use it. (1 sentence)
• **[Method]**: Same format.
• **[Method]**: Same format.

## 📉 Shared Limitations
• **[Limitation]**: A weakness that appears across multiple papers. (1 sentence)
• **[Limitation]**: Another recurring limitation. (1 sentence)
• **[Limitation]**: One more. (1 sentence)

## 🧭 Where This Field Is Heading
• One sentence on the direction the collected papers collectively point toward.

RULES:
— Use bullet points (•) only inside sections.
— Bold the label inside each bullet.
— Every point must be grounded in the actual paper content above.
— Write in clear academic English. No filler phrases.
— Do NOT list papers individually. Synthesise across them.
"""
    result = _call_groq(prompt, fallback="Summary not available.")
    return _fix_spacing(result)


# ── Gap Detection ─────────────────────────────────────────────────────────────

def detect_gaps(papers_or_text) -> str:
    """
    Identify research gaps by mining:
    1. Future scope and limitation sentences explicitly stated in the papers
    2. Topics the papers mention but do not investigate
    3. Contradictions between papers
    Output: structured, specific bullet points — no generic phrases.
    """
    paper_block, titles = _format_papers(papers_or_text)
    if not paper_block.strip():
        return "⚠️ No research content provided for gap analysis."

    future_scope_block = _extract_future_scope(papers_or_text)

    titles_preview = (
        "\n".join(f"• {t}" for t in titles[:12])
        if titles else "(plain text input)"
    )

    future_scope_section = ""
    if future_scope_block:
        future_scope_section = f"""
FUTURE SCOPE & LIMITATION STATEMENTS (extracted directly from the papers):
{future_scope_block}

These are the authors' own words about what their work does not cover.
Use these as your PRIMARY source for identifying gaps.
"""

    prompt = f"""You are a senior academic reviewer. Your task is to identify specific, well-grounded research gaps from the papers below.

PRIMARY RULE: Base your gaps on (1) what the authors themselves say is missing or future work, (2) methods/topics mentioned but not investigated, and (3) contradictions between papers. Do NOT invent gaps.

PAPERS ANALYSED ({len(titles)} papers):
{titles_preview}

FULL PAPER CONTENT:
{paper_block}
{future_scope_section}

Write EXACTLY in this format. Each bullet: bold gap title + em dash + 2 clear sentences explaining the gap and why it matters. No padding. No generic phrases.

## 🔍 Unexplored Research Directions
(Gaps the authors themselves acknowledge but do not address)
• **[Specific gap title]** — First sentence: what is not studied. Second sentence: why investigating it would advance the field.
• **[Specific gap title]** — Same format.
• **[Specific gap title]** — Same format.

## ⚙️ Methodological Limitations
(Techniques used in these papers that have known weaknesses left unaddressed)
• **[Specific gap title]** — First sentence: which method and what its limitation is. Second sentence: what a better approach would do.
• **[Specific gap title]** — Same format.
• **[Specific gap title]** — Same format.

## 📊 Evaluation & Scope Constraints
(What was NOT tested, measured, or included in these studies)
• **[Specific gap title]** — First sentence: what evaluation or context is missing. Second sentence: what broader testing would reveal.
• **[Specific gap title]** — Same format.

## ⚠️ Conflicting Findings
(Where two or more papers disagree or produce inconsistent results)
• **[Specific gap title]** — First sentence: describe the conflict between papers. Second sentence: why resolving it matters.
• **[Specific gap title]** — Same format.

STRICT RULES:
— Bullet points (•) only. Bold the gap title. Follow with em dash (—) and explanation.
— Every gap must be traceable to specific content above.
— No two bullets may use the same noun to label their gap.
— No generic phrases: never write "benchmark dataset", "limited data", "more research needed".
— Write in precise academic English. Every sentence must be complete and meaningful.
— Minimum 2 bullets per section.
"""

    result = _call_groq(prompt)
    if result and len(result) > 150:
        return _fix_spacing(
            f"### Research Gap Analysis — {len(titles)} Papers\n\n{result}"
        )
    return _fallback_keyword_analysis(paper_block)


def _fallback_keyword_analysis(text: str) -> str:
    import re
    sents = re.split(r'(?<=[.!?])\s+', text.replace("\n", " "))
    keywords = ["however", "limitation", "future", "cannot", "lacks",
                "challenge", "fail", "difficult", "not addressed", "open problem"]
    gaps = [s.strip() for s in sents
            if len(s) > 50 and any(k in s.lower() for k in keywords)][:8]
    if not gaps:
        gaps = [s.strip() for s in sents if len(s) > 60][:6]
    result = "### Research Gap Analysis\n\n"
    for g in gaps:
        result += f"• {g}.\n\n"
    return result


# ── Future Topics ─────────────────────────────────────────────────────────────

def predict_future_topics(papers_or_text) -> str:
    """
    Predict specific, well-written future research directions directly grounded
    in the gaps and future-scope statements from the retrieved papers.
    """
    paper_block, titles = _format_papers(papers_or_text)
    if not paper_block.strip():
        return "⚠️ No research content provided for future topics prediction."

    future_scope_block = _extract_future_scope(papers_or_text)

    titles_preview = (
        "\n".join(f"• {t}" for t in titles[:12])
        if titles else "(plain text input)"
    )

    future_scope_section = ""
    if future_scope_block:
        future_scope_section = f"""
FUTURE SCOPE STATEMENTS FROM THE PAPERS (authors' own words):
{future_scope_block}

Build your predictions around these stated directions.
"""

    # BERTopic enrichment
    bert_keywords = ""
    documents = [c.strip() for c in paper_block.split("\n\n") if len(c.strip()) > 50]
    if len(documents) >= 2:
        topic_model = load_models()
        if topic_model is not None:
            try:
                topic_model.fit_transform(documents)
                info = topic_model.get_topic_info()
                info = info[info["Topic"] != -1]
                kws = []
                for _, row in info.head(4).iterrows():
                    try:
                        words = [w for w, _ in topic_model.get_topic(row["Topic"])[:4]]
                        kws.append(", ".join(words))
                    except Exception:
                        pass
                if kws:
                    bert_keywords = "\nTopic clusters found in papers: " + " | ".join(kws) + "\n"
            except Exception:
                pass

    prompt = f"""You are an experienced research advisor helping a new researcher identify promising directions to pursue next.

You have read the following {len(titles)} papers:
{titles_preview}
{bert_keywords}
FULL PAPER CONTENT:
{paper_block}
{future_scope_section}

Your task: Predict specific, actionable future research directions that directly emerge from what these papers studied, found, and left unfinished.

Write EXACTLY in this format. Each bullet: bold direction title + em dash + 2 well-formed sentences. First sentence: what to do. Second sentence: why it matters or what it would contribute.

## 🚀 High-Priority Research Directions
(The most important next steps, directly following from these papers' findings)
• **[Direction title]** — What the research should investigate and how it connects to a specific finding above. Why this direction would meaningfully advance the field.
• **[Direction title]** — Same format.
• **[Direction title]** — Same format.
• **[Direction title]** — Same format.
• **[Direction title]** — Same format.

## 🛠 Methodological Improvements
(Better techniques that could address the limitations identified in these papers)
• **[Direction title]** — Which limitation from the papers this would address and what the improved approach would involve. What gain in performance or understanding it would bring.
• **[Direction title]** — Same format.
• **[Direction title]** — Same format.

## 🌐 Under-Explored Applications
(Contexts or populations absent from these papers that deserve investigation)
• **[Direction title]** — What context or setting is missing from the current papers. What a study in that setting would specifically contribute.
• **[Direction title]** — Same format.
• **[Direction title]** — Same format.

## 🤝 Cross-Disciplinary Extensions
(How insights from adjacent fields could strengthen this research)
• **[Direction title]** — Which field's tools or knowledge would address a concrete gap in these papers. What a joint study would look like.
• **[Direction title]** — Same format.

STRICT RULES:
— Bullet points (•) only. Bold the direction title. Follow with em dash (—) and explanation.
— Every bullet must reference a specific paper, finding, method, or limitation above.
— No two bullets may suggest the same kind of work.
— Do NOT write vague phrases like "more research is needed" or "this area is promising".
— Write complete, grammatically correct academic sentences. Be specific and concrete.
— Do NOT use the word "benchmark" or "dataset diversity" as gap labels.
"""

    fallback = "• Could not generate future topics — check GROQ_API_KEY and try again."
    result = _call_groq(prompt, fallback)
    header = f"### Future Research Directions — {len(titles)} Papers\n\n"
    return _fix_spacing(header + result)


# ── Public entry point ────────────────────────────────────────────────────────

def generate_summary(text_or_papers, mode: str) -> str:
    if not text_or_papers:
        return "⚠️ No text provided."
    if isinstance(text_or_papers, str) and not text_or_papers.strip():
        return "⚠️ No text provided."

    m = mode.lower()

    if m == "future topics":
        return predict_future_topics(text_or_papers)

    if m == "gap detection":
        return detect_gaps(text_or_papers)

    # Research Summary — pass both structured list and plain text
    if isinstance(text_or_papers, list):
        text = "\n\n".join(
            f"{p.get('title', '')}\n{p.get('abstract', '') or p.get('summary', '')}"
            for p in text_or_papers
        )
        return summarize_with_groq(text, papers=text_or_papers)
    else:
        return summarize_with_groq(text_or_papers)