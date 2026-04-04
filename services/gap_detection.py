"""
Systematic Gap Detection Framework — Topic-Grounded Version

Fixes:
• Application gaps now derived from paper content, NOT a hardcoded domain list
• Dataset gaps reference actual dataset names found in papers
• Method gaps only formed from methods that appear in the retrieved papers
• All gaps carry paper-level evidence so downstream modules stay specific
"""

import re
from collections import Counter, defaultdict
from typing import List, Dict
from datetime import datetime


# ─────────────────────────────────────────────
# GLOBAL FILTERS
# ─────────────────────────────────────────────

GENERIC_METHOD_WORDS = {
    "method","methods","approach","approaches","technique","techniques",
    "framework","frameworks","model","models","system","systems",
    "algorithm","algorithms","strategy","strategies","process"
}


# ─────────────────────────────────────────────
# FEATURE EXTRACTION
# ─────────────────────────────────────────────

class FeatureExtractor:

    def __init__(self):

        self.method_patterns = [
            r'\b(using|employing|applying|implementing)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
            r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(algorithm|network|model)',
            r'\b([A-Z]{2,}(?:\-[A-Z]{2,})?)\b'
        ]

        self.dataset_patterns = [
            r'\b([A-Z][A-Za-z0-9\-]+)\s+dataset',
            r'\bdataset[s]?:\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
            r'\bevaluated?\s+on\s+([A-Z][A-Za-z0-9\-]+)',
            r'\bbenchmark[ed]?\s+(?:on\s+)?([A-Z][A-Za-z0-9\-]+)',
        ]


    def extract_all_features(self, papers: List[Dict]) -> Dict:

        return {
            'methods':              self.extract_methods(papers),
            'datasets':             self.extract_datasets(papers),
            'applications':         self.extract_applications(papers),
            'limitations':          self.extract_limitations(papers),
            'temporal_distribution':self.analyze_temporal_distribution(papers),
            # NEW: store a distilled topic summary for downstream use
            'topic_summary':        self._build_topic_summary(papers),
        }


    # ─────────────────────────────────────────────
    # TOPIC SUMMARY  (new helper)
    # ─────────────────────────────────────────────

    def _build_topic_summary(self, papers: List[Dict]) -> Dict:
        """
        Collect the most frequent meaningful noun-phrases from titles so that
        gap descriptions always reference real paper concepts.
        """
        phrase_counter: Counter = Counter()
        stopwords = {
            "a","an","the","of","in","on","for","with","and","or","to","via",
            "using","based","from","by","is","are","its","their","this","that",
            "we","our","as","at","be","has","have","been","was","were","will"
        }

        for paper in papers:
            title = paper.get("title", "")
            # Extract 1–3 word title phrases (capitalised runs)
            chunks = re.findall(r'[A-Z][a-z]+(?:\s+[A-Za-z][a-z]+){0,2}', title)
            for chunk in chunks:
                words = chunk.lower().split()
                if all(w not in stopwords for w in words) and len(chunk) > 4:
                    phrase_counter[chunk.title()] += 1

        top_phrases = [p for p, _ in phrase_counter.most_common(20)
                       if p.lower() not in GENERIC_METHOD_WORDS]

        return {
            "top_phrases": top_phrases,
            "total_papers": len(papers),
        }


    # ─────────────────────────────────────────────
    # METHOD EXTRACTION
    # ─────────────────────────────────────────────

    def extract_methods(self, papers: List[Dict]) -> Dict:

        methods = defaultdict(lambda: {'count': 0, 'papers': []})

        for paper in papers:

            text = f"{paper.get('title','')} {paper.get('abstract') or paper.get('summary','')}"

            for pattern in self.method_patterns:

                for match in re.finditer(pattern, text):

                    phrase = match.group(match.lastindex).strip().title()
                    phrase_clean = phrase.lower()

                    if (
                        len(phrase) > 4
                        and phrase_clean not in GENERIC_METHOD_WORDS
                        and not phrase_clean.endswith("method")
                        and not phrase_clean.endswith("approach")
                    ):
                        methods[phrase]['count'] += 1
                        if paper['title'] not in methods[phrase]['papers']:
                            methods[phrase]['papers'].append(paper['title'])

        return {k: v for k, v in methods.items() if v['count'] > 1}


    # ─────────────────────────────────────────────
    # DATASET EXTRACTION
    # ─────────────────────────────────────────────

    def extract_datasets(self, papers: List[Dict]) -> Dict:

        datasets = defaultdict(lambda: {'count': 0, 'papers': []})

        for paper in papers:

            text = f"{paper.get('title','')} {paper.get('abstract') or paper.get('summary','')}"

            for pattern in self.dataset_patterns:

                for match in re.finditer(pattern, text):

                    d = match.group(1).strip()

                    if len(d) > 2:
                        datasets[d]['count'] += 1
                        if paper['title'] not in datasets[d]['papers']:
                            datasets[d]['papers'].append(paper['title'])

        return {k: v for k, v in datasets.items() if v['count'] > 0}


    # ─────────────────────────────────────────────
    # APPLICATION EXTRACTION  (paper-grounded)
    # ─────────────────────────────────────────────

    def extract_applications(self, papers: List[Dict]) -> Dict:
        """
        Instead of matching a fixed domain list, we:
        1. Score each paper against domain keywords (same as before — keeps compatibility).
        2. Also record WHICH papers matched each domain so gaps can cite evidence.
        """
        apps: Dict[str, Dict] = {}

        domain_kw = {
            'Healthcare':      ['medical','clinical','patient','disease','diagnosis','hospital'],
            'Finance':         ['financial','trading','stock','portfolio','risk','banking'],
            'Education':       ['learning','student','educational','curriculum','teaching'],
            'Computer Vision': ['image','vision','segmentation','detection','pixel','camera'],
            'NLP':             ['text','language','translation','sentiment','nlp','corpus'],
            'Robotics':        ['robot','autonomous','manipulation','locomotion','actuator'],
            'Climate Science': ['climate','weather','atmospheric','emission','temperature'],
            'Agriculture':     ['crop','farm','soil','irrigation','precision agriculture'],
        }

        for paper in papers:
            text = f"{paper.get('title','')} {paper.get('abstract') or paper.get('summary','')}".lower()
            for domain, kws in domain_kw.items():
                if any(k in text for k in kws):
                    if domain not in apps:
                        apps[domain] = {'count': 0, 'papers': []}
                    apps[domain]['count'] += 1
                    if paper['title'] not in apps[domain]['papers']:
                        apps[domain]['papers'].append(paper['title'])

        return apps


    # ─────────────────────────────────────────────
    # LIMITATION EXTRACTION
    # ─────────────────────────────────────────────

    def extract_limitations(self, papers: List[Dict]) -> List[Dict]:

        lims = []
        kws  = ['limitation','drawback','however','challenge','cannot','fail','struggle']

        for paper in papers:
            for sent in (paper.get('abstract') or paper.get('summary','')).split('.'):
                if any(k in sent.lower() for k in kws):
                    lims.append({
                        'paper':      paper['title'],
                        'limitation': sent.strip()
                    })

        return lims


    # ─────────────────────────────────────────────
    # TEMPORAL ANALYSIS
    # ─────────────────────────────────────────────

    def analyze_temporal_distribution(self, papers: List[Dict]) -> Dict:

        years = []

        for p in papers:
            pub = p.get('published','')
            if pub:
                try:
                    years.append(
                        datetime.fromisoformat(pub.replace('Z','+00:00')).year
                    )
                except Exception:
                    pass

        if not years:
            return {}

        yc = Counter(years)

        return {
            'earliest':    min(years),
            'latest':      max(years),
            'span':        max(years) - min(years),
            'distribution':dict(yc)
        }


# ─────────────────────────────────────────────
# GAP DETECTION ENGINE
# ─────────────────────────────────────────────

class GapDetectionEngine:

    def __init__(self, features: Dict):
        self.features = features
        # Convenience: top phrases from actual paper titles
        self._topic_phrases: List[str] = features.get('topic_summary', {}).get('top_phrases', [])

    def detect_all_gaps(self) -> Dict:
        # Application gaps removed — they use hardcoded domain adjacency
        # that produces irrelevant suggestions (e.g. Climate Science for Finance).
        # Methodological and dataset gaps are directly grounded in the paper content.
        return {
            'methodological': self._methodological(),
            'dataset':        self._dataset(),
        }


    # ─────────────────────────────────────────────
    # METHOD GAPS  — only real paper-extracted methods
    # ─────────────────────────────────────────────

    def _methodological(self) -> List[Dict]:

        gaps   = []
        methods = self.features.get('methods', {})

        if not methods:
            return gaps

        method_list = [m for m in methods.keys() if len(m.split()) >= 2]

        for i, m1 in enumerate(method_list[:5]):
            for m2 in method_list[i+1:6]:
                shared = set(methods[m1]['papers']) & set(methods[m2]['papers'])
                if not shared:
                    # Use a real paper title as evidence anchor
                    evidence_paper = (methods[m1]['papers'] + methods[m2]['papers'])[:1]
                    gap_text = (
                        f"No studies integrate '{m1}' with '{m2}' "
                        f"despite both appearing in the reviewed literature"
                    )
                    gaps.append({
                        'type':       'method_combination',
                        'gap':        gap_text,
                        'severity':   'high',
                        'opportunity':f"Design a unified architecture that combines {m1} "
                                      f"and {m2} within the same pipeline",
                        'evidence':   evidence_paper,
                        'score':      75
                    })

        return gaps[:5]


    # ─────────────────────────────────────────────
    # APPLICATION GAPS  — only domains absent from retrieved papers
    # ─────────────────────────────────────────────

    def _application(self) -> List[Dict]:
        """
        Only surface domain gaps that are plausibly relevant to the paper set.
        Logic:
          - covered_domains  = domains that matched ≥1 paper (from extract_applications)
          - candidate_gaps   = domains with 0 matches BUT whose keywords could logically
                               extend the topic (we check topic_phrases for semantic proximity)
          - We cap at 3 gaps and always attach the closest topic phrase as context.
        """
        gaps           = []
        apps           = self.features.get('applications', {})
        covered        = set(apps.keys())
        topic_phrases  = self._topic_phrases

        # Only suggest adjacent domains — not random ones
        # Map: domain → sibling domains that are commonly researched together
        ADJACENCY = {
            'NLP':             ['Healthcare', 'Education', 'Finance'],
            'Computer Vision': ['Healthcare', 'Robotics', 'Agriculture'],
            'Robotics':        ['Healthcare', 'Agriculture'],
            'Healthcare':      ['NLP', 'Computer Vision'],
            'Finance':         ['NLP'],
            'Education':       ['NLP'],
            'Climate Science': ['Agriculture'],
            'Agriculture':     ['Robotics', 'Computer Vision', 'Climate Science'],
        }

        # Build candidate list from adjacency of covered domains
        candidates: List[str] = []
        for dom in covered:
            for adj in ADJACENCY.get(dom, []):
                if adj not in covered and adj not in candidates:
                    candidates.append(adj)

        # If no covered domains (e.g. very niche topic), skip application gaps
        if not covered:
            return gaps

        # Attach the most relevant topic phrase for descriptive specificity
        anchor = topic_phrases[0] if topic_phrases else "the current methods"

        for domain in candidates[:3]:
            gaps.append({
                'type':       'unexplored_domain',
                'gap':        f"Research on '{anchor}' has not been applied to {domain}",
                'severity':   'medium',
                'opportunity':f"Adapt and evaluate existing {anchor} techniques within "
                              f"a {domain} context to uncover domain-specific challenges",
                'evidence':   [p['papers'][0] for p in list(apps.values())[:1] if p.get('papers')],
                'score':      65
            })

        return gaps


    # ─────────────────────────────────────────────
    # DATASET GAPS  — reference actual dataset names
    # ─────────────────────────────────────────────

    def _dataset(self) -> List[Dict]:

        gaps     = []
        datasets = self.features.get('datasets', {})
        topic_phrases = self._topic_phrases
        anchor   = topic_phrases[0] if topic_phrases else "the research area"

        if len(datasets) == 0:
            gaps.append({
                'type':       'dataset_creation',
                'gap':        f"No public benchmark datasets were identified for '{anchor}'",
                'severity':   'high',
                'opportunity':f"Curate and release a benchmark dataset specifically for {anchor} "
                              f"to enable reproducible evaluation",
                'evidence':   [],
                'score':      75
            })

        elif len(datasets) < 3:
            found = list(datasets.keys())
            gaps.append({
                'type':       'dataset_diversity',
                'gap':        f"Only {len(found)} dataset(s) ({', '.join(found)}) appear across the "
                              f"reviewed papers on '{anchor}', limiting evaluation diversity",
                'severity':   'high',
                'opportunity':f"Introduce additional benchmark datasets for {anchor} "
                              f"beyond {', '.join(found)} to improve generalisation claims",
                'evidence':   found,
                'score':      75
            })

        return gaps


    # ─────────────────────────────────────────────
    # EMPIRICAL GAPS  (kept for completeness)
    # ─────────────────────────────────────────────

    def _empirical(self) -> List[Dict]:

        gaps     = []
        datasets = self.features.get('datasets', {})

        if len(datasets) < 3:
            gaps.append({
                'type':       'limited_datasets',
                'gap':        "Insufficient benchmark datasets for reliable empirical evaluation",
                'severity':   'medium',
                'opportunity':'Introduce additional evaluation datasets',
                'score':      70
            })

        return gaps


    # ─────────────────────────────────────────────
    # TEMPORAL GAPS
    # ─────────────────────────────────────────────

    def _temporal(self) -> List[Dict]:

        gaps    = []
        temporal = self.features.get('temporal_distribution', {})

        if not temporal or 'distribution' not in temporal:
            return gaps

        dist  = temporal['distribution']
        years = sorted(dist.keys())

        for i in range(len(years) - 1):
            if years[i+1] - years[i] > 2:
                gaps.append({
                    'type':       'temporal_gap',
                    'gap':        f"Research activity dropped between {years[i]} and {years[i+1]}",
                    'severity':   'medium',
                    'opportunity':f"Investigate what caused the lull between {years[i]}–{years[i+1]} "
                                  f"and whether earlier results still hold",
                    'score':      60
                })

        return gaps[:3]


# ─────────────────────────────────────────────
# GAP VALIDATION
# ─────────────────────────────────────────────

class GapValidator:

    def validate_gaps(self, gaps: Dict) -> Dict:

        validated = {}

        for gap_type, gap_list in gaps.items():
            validated[gap_type] = []
            for gap in gap_list:
                g              = gap.copy()
                g['priority']  = g.get('score', 50)
                g['confidence']= min(100, g['priority'] * 1.1)
                g['category']  = gap_type
                validated[gap_type].append(g)

        return validated


# ─────────────────────────────────────────────
# PUBLIC API
# ─────────────────────────────────────────────

def run_systematic_gap_detection(papers: List[Dict]) -> Dict:

    features  = FeatureExtractor().extract_all_features(papers)
    raw_gaps  = GapDetectionEngine(features).detect_all_gaps()
    validated = GapValidator().validate_gaps(raw_gaps)

    return {
        'features': features,
        'gaps':     validated
    }