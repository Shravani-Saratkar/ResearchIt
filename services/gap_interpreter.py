"""
Gap Interpretation & Justification Engine.
Enriches each raw gap with AI reasoning.
FIXED: always returns a proper gap dict — never propagates {"error":...} to session state.
"""

import os
from typing import Dict
import google.generativeai as genai


class GapInterpreter:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        self.model = None
        if api_key:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel("gemini-2.5-flash")

    def interpret_all_gaps(self, validated_gaps: Dict) -> Dict:
        """Return enriched gaps. Falls back gracefully if model unavailable."""
        interpreted = {}
        for gap_type, gaps in validated_gaps.items():
            interpreted[gap_type] = []
            for gap in gaps:
                enriched = gap.copy()
                if self.model:
                    enriched.update(self._interpret_single(gap))
                else:
                    enriched.update(self._fallback(gap))
                interpreted[gap_type].append(enriched)
        return interpreted

    def _interpret_single(self, gap: Dict) -> Dict:
        prompt = f"""You are an expert research reviewer.

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
        try:
            resp = self.model.generate_content(prompt)
            return self._parse(resp.text)
        except Exception:
            return self._fallback(gap)

    @staticmethod
    def _fallback(gap: Dict) -> Dict:
        return {
            "why_existing_work_stops_here": "Methodological and conceptual constraints limit current studies.",
            "implicit_assumption":          "Existing formulations are assumed sufficient.",
            "research_risk":                "Increased complexity or reduced generalizability.",
            "novelty_claim":                "Extends current methods by challenging prevailing assumptions.",
            "proposal_ready_gap":           gap.get("gap", ""),
        }

    @staticmethod
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


def interpret_gaps(validated_gaps: Dict) -> Dict:
    """Public API. Always returns a valid dict of enriched gaps."""
    return GapInterpreter().interpret_all_gaps(validated_gaps)
