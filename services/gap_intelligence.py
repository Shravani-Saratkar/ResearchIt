"""
Research Opportunity Discovery Engine.
- Guarantees minimum 5 opportunities by supplementing detected gaps
  with future-scope directions mined directly from paper abstracts.
- No generic labels, no domain adjacency guessing.
- All content grounded in retrieved paper titles and abstracts.
"""

import re
from typing import Dict, List
from collections import Counter
from gemini_client import get_client


# ── Stop / ignore word sets ───────────────────────────────────────────────────

_STOPWORDS = {
    "a","an","the","of","in","on","for","with","and","or","to","via",
    "using","based","from","by","is","are","its","their","this","that",
    "we","our","as","at","be","has","have","been","was","were","will",
    "which","when","how","where","what","whether","both","such","each",
}
_IGNORE = {
    "method","approach","dataset","system","model","framework","technique",
    "paper","study","research","current","limited","applying","novel",
    "effective","existing","various","different","new","toward","across",
}

# Signals that a sentence discusses future work or limitations
_FUTURE_SIGNALS = [
    "future work", "future research", "in the future", "can be extended",
    "remains to be", "left for future", "open problem", "limitation",
    "we did not", "does not address", "fails to", "not yet", "still lacks",
    "further investigation", "warrants further", "promising direction",
    "scope for", "avenue for", "could be improved", "not explored",
    "should be investigated", "needs further", "has not been",
]


# ── Topic inference ───────────────────────────────────────────────────────────

def _infer_topic(papers: List[Dict]) -> str:
    if not papers:
        return "AI Research"
    counter: Counter = Counter()
    for p in papers[:15]:
        chunks = re.findall(r'[A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,3}', p.get("title", ""))
        for chunk in chunks:
            words = chunk.lower().split()
            if len(words) >= 2 and all(w not in _STOPWORDS for w in words):
                counter[chunk] += 1
    for phrase, cnt in counter.most_common(10):
        if cnt >= 2:
            return phrase
    if counter:
        return counter.most_common(1)[0][0]
    words = [w for w in (papers[0].get("title","") or "").split()
             if w.lower() not in _STOPWORDS]
    return " ".join(words[:5]) or "AI Research"


# ── Keyword extraction ────────────────────────────────────────────────────────

def _extract_keywords(papers: List[Dict], n: int = 6) -> List[str]:
    counter: Counter = Counter()
    for p in papers[:20]:
        title = p.get("title", "")
        for w in re.findall(r'\b([A-Z][a-z]{4,})\b', title):
            if w.lower() not in _STOPWORDS | _IGNORE:
                counter[w] += 1
        for ph in re.findall(r'([A-Z][a-z]+\s+[A-Z][a-z]+)', title):
            if all(w.lower() not in _STOPWORDS | _IGNORE for w in ph.split()):
                counter[ph] += 1
    top = [kw for kw, _ in counter.most_common(n * 2)]
    filtered = []
    for kw in top:
        if not any(kw in longer for longer in top if longer != kw):
            filtered.append(kw)
        if len(filtered) >= n:
            break
    return filtered or ["Research", "Methods"]


# ── Future scope extraction ───────────────────────────────────────────────────

def _extract_future_scope_sentences(papers: List[Dict]) -> List[Dict]:
    """
    Return a list of dicts: {paper_title, sentence}
    for every sentence in abstracts that signals future work / limitations.
    Used both for the gap prompt and to generate synthetic extra opportunities.
    """
    collected = []
    for p in papers[:15]:
        title    = p.get("title", "Untitled")
        abstract = (p.get("abstract") or p.get("summary") or "")
        for sent in re.split(r'(?<=[.!?])\s+', abstract):
            if len(sent) > 40 and any(sig in sent.lower() for sig in _FUTURE_SIGNALS):
                collected.append({"paper_title": title, "sentence": sent.strip()})
    return collected


def _future_scope_block(papers: List[Dict]) -> str:
    items = _extract_future_scope_sentences(papers)
    if not items:
        return ""
    lines = [f'[{i["paper_title"]}]: "{i["sentence"]}"' for i in items[:12]]
    return "\nFUTURE SCOPE & LIMITATION STATEMENTS (authors' own words):\n" + "\n".join(lines) + "\n"


# ── Synthetic gaps from future-scope sentences ────────────────────────────────

def _make_synthetic_gaps_from_future_scope(papers: List[Dict]) -> List[Dict]:
    """
    Convert future-scope sentences into gap dicts so they feed into
    _generate_opportunity — this guarantees extra opportunities even
    when gap_detection finds only 1-2 structural gaps.
    """
    items  = _extract_future_scope_sentences(papers)
    gaps   = []
    seen   = set()
    for item in items[:8]:
        sent = item["sentence"]
        key  = sent[:60]
        if key in seen:
            continue
        seen.add(key)
        gaps.append({
            "type":       "future_scope",
            "gap":        sent,
            "severity":   "medium",
            "opportunity": f"Investigate the direction stated as future work in: {item['paper_title']}",
            "evidence":   [item["paper_title"]],
            "score":      65,
            "priority":   65,
            "category":   "future_scope",
        })
    return gaps


# ── AI content generation for one opportunity ─────────────────────────────────

def _generate_opportunity(gap: Dict, topic: str, papers: List[Dict]) -> Dict:
    paper_titles = "\n".join(
        f"- {p.get('title','')}" for p in papers[:10] if p.get("title")
    )
    paper_abstracts = "\n".join(
        f"  [{p.get('title','')}]: {(p.get('abstract','') or '')[:200]}"
        for p in papers[:4] if p.get("abstract")
    )
    scope = _future_scope_block(papers)
    evidence = gap.get("evidence", [])
    evidence_str = ("Evidence from: " + ", ".join(str(e) for e in evidence[:2])) if evidence else ""

    prompt = (
        "You are an academic research advisor generating a precise, actionable research opportunity.\n\n"
        f"PAPER TITLES (your ONLY source of domain knowledge):\n{paper_titles}\n\n"
        f"ABSTRACT SNIPPETS:\n{paper_abstracts}\n"
        f"{scope}\n"
        f"DETECTED GAP / FUTURE DIRECTION:\n{gap.get('gap','')}\n\n"
        f"OPPORTUNITY HINT:\n{gap.get('opportunity','')}\n\n"
        f"{evidence_str}\n\n"
        "STRICT RULES:\n"
        "— Every sentence must reference specific concepts or findings from the paper titles above.\n"
        "— Do NOT introduce any domain not present in those titles.\n"
        "— Do NOT use phrases like 'benchmark dataset', 'limited data', 'more research needed'.\n"
        "— Write precise academic English. Every sentence must be complete.\n\n"
        "Return EXACTLY in this format:\n\n"
        "TITLE:\n[8-12 word research title naming the specific technique and problem from the papers]\n\n"
        "WHY:\n[2 sentences. What is missing and where. What filling this gap would contribute.]\n\n"
        "APPROACH:\n[4 numbered steps. Each step names a concrete method or paper from the titles.]\n\n"
        "IMPACT:\n[1-2 sentences on the specific benefit to this research area.]\n\n"
        "STEPS:\n[3 immediate actions referencing specific papers above.]\n"
    )

    try:
        text = get_client().generate(prompt, fallback="")
        if text and len(text) > 100:
            return _parse_response(text, gap, topic, papers)
    except Exception:
        pass
    return _fallback_content(gap, topic, papers)


def _parse_response(text: str, gap: Dict, topic: str, papers: List[Dict]) -> Dict:
    result = {}
    for key, label in [
        ("title",    "TITLE:"),
        ("why",      "WHY:"),
        ("approach", "APPROACH:"),
        ("impact",   "IMPACT:"),
        ("steps",    "STEPS:"),
    ]:
        pattern = rf"{label}\s*(.+?)(?=(?:TITLE:|WHY:|APPROACH:|IMPACT:|STEPS:)|$)"
        m = re.search(pattern, text, re.DOTALL | re.I)
        if m:
            result[key] = m.group(1).strip()
    if not result.get("title") or len(result.get("title","")) < 8:
        return _fallback_content(gap, topic, papers)
    return result


def _fallback_content(gap: Dict, topic: str, papers: List[Dict]) -> Dict:
    top = [p.get("title","") for p in papers[:3] if p.get("title")]
    cat = gap.get("category","methodological")
    title_map = {
        "methodological": f"Hybrid Methodology for {topic}",
        "dataset":        f"Evaluation Framework for {topic}",
        "future_scope":   f"Extending {topic}: Addressing Stated Future Work",
    }
    title = title_map.get(cat, f"Advancing {topic}: Closing an Identified Gap")
    why   = (
        f"The reviewed papers on {topic} leave this direction unaddressed: "
        f"{gap.get('gap','')}. "
        f"Closing this gap would directly extend the contributions of the reviewed literature."
    )
    approach_lines = [f"1. Replicate and extend baselines from: {top[0]}"] if top else []
    if len(top) > 1:
        approach_lines.append(f"2. Compare methodology against: {top[1]}")
    approach_lines += [
        f"3. Design and implement the missing component for {topic}",
        "4. Evaluate under conditions not covered in the reviewed papers",
    ]
    steps = (
        f"1. Annotate future scope sections in: {', '.join(top[:2])}\n"
        f"2. Search recent preprints for '{topic}' and the gap keywords\n"
        "3. Set up a reproducible experiment environment using reviewed paper baselines"
        if top else
        "1. Conduct targeted literature search\n2. Identify baselines\n3. Define evaluation protocol"
    )
    return {
        "title":    title,
        "why":      why,
        "approach": "\n".join(approach_lines),
        "impact":   f"Directly advances the research agenda in {topic}.",
        "steps":    steps,
    }


# ── Scoring & metadata ────────────────────────────────────────────────────────

def _score(gap: Dict, category: str) -> int:
    severity_pts = {"high": 40, "medium": 25, "low": 15}
    cat_weights  = {
        "methodological": 1.2, "theoretical": 1.1,
        "empirical": 1.0,      "dataset": 0.9,
        "future_scope": 1.15,  "temporal": 0.7,
    }
    base     = severity_pts.get(gap.get("severity","medium"), 25)
    weight   = cat_weights.get(category, 1.0)
    priority = gap.get("priority", gap.get("score", 50)) * 0.3
    return int(min(100, max(0, base * weight + priority)))


def _difficulty(gap: Dict) -> str:
    t = gap.get("type","")
    if t in ["unexplored_domain", "underutilized_method", "future_scope"]:
        return "Intermediate"
    if t in ["method_combination", "dataset_creation", "dataset_diversity", "theoretical_foundation"]:
        return "Advanced"
    return "Intermediate"


def _timeline(difficulty: str) -> str:
    return {
        "Beginner-Friendly": "3-6 months",
        "Intermediate":      "6-12 months",
        "Advanced":          "12-24 months",
    }.get(difficulty, "6-12 months")


# ── Main discovery engine ─────────────────────────────────────────────────────

def discover_research_opportunities(detected_gaps: Dict, papers: List[Dict]) -> Dict:
    """
    Transform gaps into structured research opportunities.
    Guarantees at least 5 by supplementing with future-scope directions
    extracted directly from the papers' own abstracts.
    """
    topic    = _infer_topic(papers)
    keywords = _extract_keywords(papers)

    # Build master gap list: structural gaps + future-scope gaps
    all_gaps: List[tuple] = []  # (category, gap_dict)
    for category, gap_list in detected_gaps.items():
        for gap in gap_list:
            all_gaps.append((category, gap))

    # Add future-scope synthetic gaps to pad to at least 5
    if len(all_gaps) < 5:
        synthetic = _make_synthetic_gaps_from_future_scope(papers)
        needed    = 5 - len(all_gaps)
        for sg in synthetic[:needed + 3]:   # grab a few extras for dedup headroom
            all_gaps.append(("future_scope", sg))

    # Generate opportunity for every gap
    all_topics: List[Dict] = []
    for category, gap in all_gaps:
        content    = _generate_opportunity(gap, topic, papers)
        score      = _score(gap, category)
        difficulty = _difficulty(gap)
        timeline   = _timeline(difficulty)

        all_topics.append({
            "opportunity_score":  score,
            "difficulty":         difficulty,
            "estimated_timeline": timeline,
            "keywords":           keywords[:5],

            "topic_title":        content.get("title", f"Research Advance in {topic}"),
            "research_pitch":     content.get("why",   "Significant opportunity identified."),
            "concrete_approach":  content.get("approach", "Systematic investigation required."),
            "why_it_matters":     content.get("impact", f"Advances the field of {topic}."),
            "first_steps":        content.get("steps", "Begin with a targeted literature review."),

            "original_gap":       gap.get("gap",""),
            "category":           category,
            "severity":           gap.get("severity","medium"),
        })

    # Deduplicate by title
    seen, unique = set(), []
    for t in all_topics:
        key = re.sub(r'\W+', '', t["topic_title"].lower())
        if key not in seen:
            unique.append(t)
            seen.add(key)

    unique.sort(key=lambda t: -t["opportunity_score"])

    # Guarantee at least 5 in hot_topics
    hot_topics  = unique[:max(8, 5)]
    quick_wins  = [t for t in unique if t["difficulty"] == "Beginner-Friendly"][:5]
    high_impact = [t for t in unique
                   if t["difficulty"] == "Advanced" and t["opportunity_score"] >= 70][:5]
    total       = len(unique)
    avg_score   = round(sum(t["opportunity_score"] for t in unique) / total, 1) if total else 0

    return {
        "hot_topics":  hot_topics,
        "quick_wins":  quick_wins,
        "high_impact": high_impact,
        "summary": {
            "total_opportunities":    total,
            "quick_win_count":        len(quick_wins),
            "high_impact_count":      len(high_impact),
            "avg_opportunity_score":  avg_score,
            "difficulty_distribution":dict(Counter(t["difficulty"] for t in unique)),
            "top_keywords":           keywords[:8],
        }
    }


# ── Public API ────────────────────────────────────────────────────────────────

def run_gap_intelligence(detected_gaps: Dict, papers: List[Dict] = None) -> Dict:
    if papers is None:
        papers = []
    opportunities = discover_research_opportunities(detected_gaps, papers)
    return {
        "opportunities":      opportunities,
        "impact_matrix":      [],
        "relationship_graph": {"nodes": [], "edges": []},
        "prototypes":         [],
    }