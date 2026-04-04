"""
Gap Interpretation & Justification Engine.
Enriches each raw gap with AI reasoning.

RATE-LIMIT FIX: Uses shared GroqClient (gemini_client.py) which provides:
  - Prompt caching  (re-runs on same papers cost 0 API calls)
  - Batch merging   (all gaps interpreted in 1-2 API calls instead of N)
  - Exponential backoff + RPM throttle
"""

from typing import Dict
from gemini_client import get_client  # Groq-backed client (drop-in, same API)


# ─────────────────────────────────────────────
# PROMPT BUILDER
# ─────────────────────────────────────────────

def _build_prompt(gap: Dict) -> str:
    return f"""You are an expert research reviewer.

Gap description : {gap.get('gap')}
Gap type        : {gap.get('type')}
Severity        : {gap.get('severity')}
Opportunity     : {gap.get('opportunity')}

Tasks:
1. Explain WHY existing research stops at this point.
2. Identify the implicit assumption causing this gap.
3. State the intellectual risk in addressing it.
4. Frame a clear novelty claim.
5. Rewrite the gap as a proposal-ready problem statement.

Return STRICTLY in this format (use the labels exactly):

WHY_STOP:
<text>

ASSUMPTION:
<text>

RISK:
<text>

NOVELTY:
<text>

PROPOSAL_GAP:
<text>
"""


# ─────────────────────────────────────────────
# RESPONSE PARSER
# ─────────────────────────────────────────────

def _parse(text: str) -> Dict:
    labels = {
        "WHY_STOP":    "why_existing_work_stops_here",
        "ASSUMPTION":  "implicit_assumption",
        "RISK":        "research_risk",
        "NOVELTY":     "novelty_claim",
        "PROPOSAL_GAP":"proposal_ready_gap",
    }
    result, current, buf = {}, None, []
    for line in text.splitlines():
        line = line.strip()
        key  = line.rstrip(":")
        if key in labels:
            if current and buf:
                result[labels[current]] = " ".join(buf).strip()
            current, buf = key, []
        elif current:
            buf.append(line)
    if current and buf:
        result[labels[current]] = " ".join(buf).strip()
    return result


def _fallback(gap: Dict) -> Dict:
    return {
        "why_existing_work_stops_here": "Methodological and conceptual constraints limit current studies.",
        "implicit_assumption":          "Existing formulations are assumed sufficient.",
        "research_risk":                "Increased complexity or reduced generalizability.",
        "novelty_claim":                "Extends current methods by challenging prevailing assumptions.",
        "proposal_ready_gap":           gap.get("gap", ""),
    }


# ─────────────────────────────────────────────
# MAIN INTERPRETER  (batch version)
# ─────────────────────────────────────────────

class GapInterpreter:

    def interpret_all_gaps(self, validated_gaps: Dict) -> Dict:
        """
        Collect ALL gap prompts, fire them as a single batch through
        GroqClient, then reassemble results.
        Zero duplicate API calls thanks to the shared cache.
        """
        # Flatten into ordered list
        order  = []   # (gap_type, index_within_type)
        prompts = []

        for gap_type, gaps in validated_gaps.items():
            for i, gap in enumerate(gaps):
                order.append((gap_type, i))
                prompts.append(_build_prompt(gap))

        if not prompts:
            return validated_gaps

        # ONE batch call (may be split internally into groups of 5)
        try:
            client  = get_client()
            responses = client.generate_batch(prompts, fallback="")
        except EnvironmentError:
            # No API key — use fallback for every gap
            responses = [""] * len(prompts)

        # Rebuild the gap dict with enriched data
        interpreted: Dict = {gt: list(gl) for gt, gl in validated_gaps.items()}

        for (gap_type, i), raw_text in zip(order, responses):
            gap     = validated_gaps[gap_type][i].copy()
            enriched = _parse(raw_text) if raw_text else _fallback(gap)
            # Ensure all keys are present
            for k, v in _fallback(gap).items():
                enriched.setdefault(k, v)
            gap.update(enriched)
            interpreted[gap_type][i] = gap

        return interpreted


def interpret_gaps(validated_gaps: Dict) -> Dict:
    """Public API. Always returns a valid dict of enriched gaps."""
    return GapInterpreter().interpret_all_gaps(validated_gaps)