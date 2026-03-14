"""
Research Opportunity Discovery Engine
Generates impressive, actionable research insights that users actually want to see.
"""

import os
import re
from typing import Dict, List
from collections import Counter
import google.generativeai as genai


# ═════════════════════════════════════════════════════════════════════════════
# SMART CONCEPT EXTRACTION
# ═════════════════════════════════════════════════════════════════════════════

IGNORE_WORDS = {
    "method", "approach", "dataset", "system", "model", "framework", "technique",
    "paper", "study", "research", "current", "limited", "applying", "using",
    "based", "new", "novel", "effective", "existing", "various", "different"
}


def _smart_extract_domain_and_problem(gap: Dict, papers: List[Dict]) -> tuple:
    """
    Extract REAL domain and problem from gap + paper context.
    Returns: (domain, specific_problem, innovation_type)
    """
    gap_text = gap.get("gap", "")
    category = gap.get("category", "")
    
    # Extract domain from papers (more reliable than gap text)
    domain = _infer_domain_from_papers(papers)
    
    # Extract specific problem from gap text
    problem = _extract_problem_from_gap(gap_text, category)
    
    # Determine innovation type
    innovation = _determine_innovation_type(gap, category)
    
    return domain, problem, innovation


def _infer_domain_from_papers(papers: List[Dict]) -> str:
    """Infer research domain from paper titles/abstracts."""
    if not papers:
        return "AI Research"
    
    # Collect keywords from paper titles
    all_text = " ".join([p.get("title", "") for p in papers[:10]])
    all_text = all_text.lower()
    
    # Domain detection patterns
    domains = {
        "Natural Language Processing": ["language", "nlp", "text", "linguistic", "translation", "bert", "gpt", "llm"],
        "Computer Vision": ["vision", "image", "visual", "object detection", "segmentation", "cnn"],
        "Robotics": ["robot", "robotic", "manipulation", "navigation", "autonomous"],
        "Healthcare AI": ["medical", "clinical", "health", "patient", "diagnosis", "disease"],
        "Reinforcement Learning": ["reinforcement", "policy", "reward", "agent", "rl"],
        "Graph Neural Networks": ["graph", "network", "node", "edge", "gnn"],
        "Time Series": ["time series", "temporal", "forecasting", "prediction"],
        "Federated Learning": ["federated", "privacy", "distributed"],
        "Multi-Agent Systems": ["multi-agent", "cooperative", "coordination"],
        "Finance AI": ["finance", "financial", "trading", "stock", "risk"],
        "Climate Science": ["climate", "weather", "environmental"],
    }
    
    for domain, keywords in domains.items():
        if any(kw in all_text for kw in keywords):
            return domain
    
    return "Machine Learning"


def _extract_problem_from_gap(gap_text: str, category: str) -> str:
    """Extract specific problem statement from gap."""
    
    # Clean gap text
    text = gap_text.lower()
    text = re.sub(r"no papers combine\s*", "", text)
    text = re.sub(r"limited research\s*", "", text)
    
    # Extract quoted concepts
    quoted = re.findall(r"'([^']+)'", text)
    if len(quoted) >= 2:
        return f"integrating {quoted[0]} with {quoted[1]}"
    
    # Extract meaningful phrases
    words = re.findall(r'\b[a-z]{5,}\b', text)
    meaningful = [w for w in words if w not in IGNORE_WORDS][:3]
    
    if len(meaningful) >= 2:
        return f"{meaningful[0]} for {meaningful[1]}"
    
    # Category-based fallback
    problems = {
        "methodological": "developing hybrid approaches",
        "dataset": "creating comprehensive benchmarks",
        "application": "applying AI to new domains",
        "empirical": "validating at scale",
        "theoretical": "building formal frameworks"
    }
    return problems.get(category, "advancing research")


def _determine_innovation_type(gap: Dict, category: str) -> str:
    """Determine what type of innovation this represents."""
    
    innovations = {
        "methodological": "Novel Methodology",
        "dataset": "New Dataset",
        "application": "Domain Transfer",
        "empirical": "Large-Scale Validation",
        "theoretical": "Theoretical Framework",
        "temporal": "Longitudinal Study"
    }
    
    return innovations.get(category, "Research Advance")


# ═════════════════════════════════════════════════════════════════════════════
# AI-POWERED CONTENT GENERATION
# ═════════════════════════════════════════════════════════════════════════════

def _generate_with_ai(gap: Dict, domain: str, problem: str, papers: List[Dict]) -> Dict:
    """Use Gemini to generate high-quality, specific content."""
    
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return _generate_smart_fallback(gap, domain, problem)
    
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-2.5-flash")
        
        # Build context from papers
        paper_context = "\n".join([
            f"- {p.get('title', '')}" for p in papers[:5]
        ])
        
        prompt = f"""You are a research advisor. Generate ONE specific research opportunity.

Domain: {domain}
Gap: {gap.get('gap', '')}
Problem: {problem}
Category: {gap.get('category', '')}

Recent papers in this field:
{paper_context}

Generate in this EXACT format:

TITLE: [Specific 8-12 word research title using real concepts from the domain]

WHY: [2-3 sentences explaining: (1) What current work misses (2) Why this matters NOW (3) What breakthrough this enables]

APPROACH: [4 specific research steps - be concrete, mention actual techniques/datasets/metrics from the domain]

IMPACT: [2 sentences on SPECIFIC real-world applications in {domain} - no generic statements]

STEPS: [3 concrete actions to start THIS WEEK - be specific about papers to read, tools to use, data to get]

Rules:
- Use REAL concepts from {domain}
- Be SPECIFIC - no generic phrases
- Make it sound like a real research project
- Focus on {domain} applications ONLY
"""
        
        response = model.generate_content(prompt)
        return _parse_ai_response(response.text, gap, domain, problem)
        
    except Exception:
        return _generate_smart_fallback(gap, domain, problem)


def _parse_ai_response(text: str, gap: Dict, domain: str, problem: str) -> Dict:
    """Parse AI response into structured content."""
    
    result = {}
    
    # Extract sections
    for key, label in [
        ("title", "TITLE:"),
        ("why", "WHY:"),
        ("approach", "APPROACH:"),
        ("impact", "IMPACT:"),
        ("steps", "STEPS:")
    ]:
        pattern = rf"{label}\s*(.+?)(?=(?:TITLE:|WHY:|APPROACH:|IMPACT:|STEPS:)|$)"
        match = re.search(pattern, text, re.DOTALL | re.I)
        if match:
            result[key] = match.group(1).strip()
    
    # Validate and fallback
    if not result.get("title") or len(result.get("title", "")) < 10:
        return _generate_smart_fallback(gap, domain, problem)
    
    return result


def _generate_smart_fallback(gap: Dict, domain: str, problem: str) -> Dict:
    """Generate smart, context-aware fallback content."""
    
    category = gap.get("category", "")
    
    # Domain-specific titles
    if category == "dataset":
        title = f"Large-Scale Benchmark Dataset for {domain}"
    elif category == "methodological":
        title = f"Hybrid Architecture for {problem.title()} in {domain}"
    elif category == "application":
        title = f"Transfer Learning Approach for {domain} Applications"
    else:
        title = f"Advances in {problem.title()} for {domain}"
    
    # Context-aware why statement
    why = (
        f"Current {domain} research has not adequately addressed {problem}. "
        f"Existing approaches face limitations in scalability and generalization. "
        f"Recent methodological advances make this investigation both timely and impactful."
    )
    
    # Domain-specific approach
    approaches = {
        "Natural Language Processing": "Fine-tune large language models\nCreate domain-specific evaluation benchmarks\nConduct human evaluation studies\nAnalyze error patterns and failure cases",
        "Computer Vision": "Develop multi-scale architecture\nTrain on diverse image datasets\nValidate across different lighting conditions\nBenchmark against state-of-the-art models",
        "Robotics": "Design control algorithm\nTest in simulation environment\nDeploy on physical robot platform\nEvaluate in real-world scenarios",
        "Healthcare AI": "Curate clinical dataset with expert labels\nValidate on multiple hospital systems\nEnsure compliance with medical standards\nConduct prospective clinical study",
        "Reinforcement Learning": "Design reward function\nImplement policy network\nTrain in simulated environments\nTransfer to real-world tasks"
    }
    approach = approaches.get(domain, 
        "Design systematic framework\nImplement prototype system\n"
        "Evaluate on benchmark datasets\nCompare with baseline methods"
    )
    
    # Domain-specific impact
    impacts = {
        "Healthcare AI": f"Could improve clinical decision-making and patient outcomes in {domain} applications.",
        "Robotics": f"Would enable more capable autonomous systems for industrial and service applications.",
        "Natural Language Processing": f"Could enhance human-AI interaction and information access systems.",
        "Computer Vision": f"Would improve visual understanding for autonomous systems and surveillance.",
        "Finance AI": f"Could enhance risk assessment and decision-making in financial systems.",
        "Climate Science": f"Would improve climate modeling and prediction capabilities.",
    }
    impact = impacts.get(domain, 
        f"Could significantly advance capabilities in {domain} systems and applications."
    )
    
    # Domain-specific first steps
    steps_templates = {
        "Natural Language Processing": f"Review recent LLM papers on {problem}\nDownload relevant text corpora\nSet up HuggingFace/PyTorch environment",
        "Computer Vision": f"Survey recent papers on {problem}\nDownload ImageNet/COCO datasets\nSet up PyTorch/TensorFlow pipeline",
        "Robotics": f"Review robotics papers on {problem}\nInstall ROS/Gazebo simulation\nIdentify relevant robot platforms",
        "Healthcare AI": f"Review clinical AI literature\nIdentify publicly available medical datasets\nConsult with domain experts",
    }
    steps = steps_templates.get(domain,
        f"Survey recent {domain} literature\nIdentify benchmark datasets\nSet up development environment"
    )
    
    return {
        "title": title,
        "why": why,
        "approach": approach,
        "impact": impact,
        "steps": steps
    }


# ═════════════════════════════════════════════════════════════════════════════
# SCORING & METADATA
# ═════════════════════════════════════════════════════════════════════════════

def _calculate_opportunity_score(gap: Dict, category: str) -> int:
    """Calculate opportunity score [0-100]."""
    severity_points = {"high": 40, "medium": 25, "low": 15}
    category_weights = {
        "application": 1.3, "methodological": 1.2, "theoretical": 1.1,
        "empirical": 1.0, "dataset": 0.9, "temporal": 0.7
    }
    
    base = severity_points.get(gap.get("severity", "medium"), 25)
    weight = category_weights.get(category, 1.0)
    priority = gap.get("priority", gap.get("score", 50)) * 0.3
    
    return int(min(100, max(0, (base * weight) + priority)))


def _estimate_difficulty(gap: Dict) -> str:
    """Estimate difficulty level."""
    gap_type = gap.get("type", "")
    if gap_type in ["unexplored_domain", "underutilized_method"]:
        return "Beginner-Friendly"
    elif gap_type in ["theoretical_foundation", "dataset_creation", "method_combination"]:
        return "Advanced"
    return "Intermediate"


def _estimate_timeline(difficulty: str) -> str:
    """Estimate timeline."""
    return {
        "Beginner-Friendly": "3-6 months",
        "Intermediate": "6-12 months",
        "Advanced": "12-24 months"
    }.get(difficulty, "6-12 months")


def _extract_keywords(domain: str, problem: str) -> List[str]:
    """Extract keywords from domain and problem."""
    words = re.findall(r'\b[A-Z][a-z]+\b', f"{domain} {problem}")
    return words[:5] if words else [domain.split()[0]]


# ═════════════════════════════════════════════════════════════════════════════
# MAIN DISCOVERY ENGINE
# ═════════════════════════════════════════════════════════════════════════════

def discover_research_opportunities(detected_gaps: Dict, papers: List[Dict]) -> Dict:
    """Transform gaps into impressive, actionable research opportunities."""
    
    all_topics = []
    
    for category, gap_list in detected_gaps.items():
        for gap in gap_list:
            # Smart extraction
            domain, problem, innovation = _smart_extract_domain_and_problem(gap, papers)
            
            # AI-powered content generation
            content = _generate_with_ai(gap, domain, problem, papers)
            
            # Calculate metrics
            score = _calculate_opportunity_score(gap, category)
            difficulty = _estimate_difficulty(gap)
            timeline = _estimate_timeline(difficulty)
            keywords = _extract_keywords(domain, problem)
            
            # Assemble topic
            topic = {
                "opportunity_score": score,
                "difficulty": difficulty,
                "estimated_timeline": timeline,
                "keywords": keywords,
                
                "topic_title": content.get("title", f"Research Advances in {domain}"),
                "research_pitch": content.get("why", "Significant research opportunity identified."),
                "concrete_approach": content.get("approach", "Systematic research approach needed."),
                "why_it_matters": content.get("impact", f"Could advance {domain} research."),
                "first_steps": content.get("steps", "Begin literature review."),
                
                "original_gap": gap.get("gap", ""),
                "category": category,
                "severity": gap.get("severity", "medium"),
            }
            
            all_topics.append(topic)
    
    # Remove duplicates
    all_topics = _deduplicate(all_topics)
    
    # Sort by score
    all_topics.sort(key=lambda t: -t["opportunity_score"])
    
    # Categorize
    hot_topics = all_topics[:8]
    quick_wins = [t for t in all_topics if t["difficulty"] == "Beginner-Friendly"][:5]
    high_impact = [t for t in all_topics if t["difficulty"] == "Advanced" and t["opportunity_score"] >= 70][:5]
    
    # Summary
    total = len(all_topics)
    avg_score = sum(t["opportunity_score"] for t in all_topics) / total if total else 0
    all_keywords = []
    for t in all_topics:
        all_keywords.extend(t["keywords"])
    
    summary = {
        "total_opportunities": total,
        "hot_topic_count": len(hot_topics),
        "quick_win_count": len(quick_wins),
        "high_impact_count": len(high_impact),
        "avg_opportunity_score": round(avg_score, 1),
        "difficulty_distribution": dict(Counter(t["difficulty"] for t in all_topics)),
        "top_keywords": [kw for kw, _ in Counter(all_keywords).most_common(10)],
    }
    
    return {
        "hot_topics": hot_topics,
        "quick_wins": quick_wins,
        "high_impact": high_impact,
        "summary": summary
    }


def _deduplicate(topics: List[Dict]) -> List[Dict]:
    """Remove duplicate topics."""
    seen = set()
    unique = []
    for t in topics:
        key = re.sub(r'\W+', '', t["topic_title"].lower())
        if key not in seen:
            unique.append(t)
            seen.add(key)
    return unique


# ═════════════════════════════════════════════════════════════════════════════
# PUBLIC API
# ═════════════════════════════════════════════════════════════════════════════

def run_gap_intelligence(detected_gaps: Dict, papers: List[Dict] = None) -> Dict:
    """Main entry point."""
    if papers is None:
        papers = []
    
    opportunities = discover_research_opportunities(detected_gaps, papers)
    
    return {
        "opportunities": opportunities,
        "impact_matrix": [],
        "relationship_graph": {"nodes": [], "edges": []},
        "prototypes": []
    }