"""
Systematic Gap Detection Framework — Improved Version

Fixes:
• Filters generic tokens like 'method', 'approach'
• Avoids meaningless combinations
• Extracts only meaningful research methods
• Produces cleaner gaps for gap_intelligence module
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

            r'\b([A-Z][A-Za-z0-9]+)\s+dataset',

            r'\bdataset[s]?:\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
        ]


    def extract_all_features(self, papers: List[Dict]) -> Dict:

        return {

            'methods': self.extract_methods(papers),

            'datasets': self.extract_datasets(papers),

            'applications': self.extract_applications(papers),

            'limitations': self.extract_limitations(papers),

            'temporal_distribution': self.analyze_temporal_distribution(papers),
        }


    # ─────────────────────────────────────────────
    # METHOD EXTRACTION
    # ─────────────────────────────────────────────

    def extract_methods(self, papers):

        methods = defaultdict(lambda: {'count': 0, 'papers': []})

        for paper in papers:

            text = f"{paper.get('title','')} {paper.get('abstract','')}"

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

    def extract_datasets(self, papers):

        datasets = defaultdict(lambda: {'count': 0, 'papers': []})

        for paper in papers:

            text = f"{paper.get('title','')} {paper.get('abstract','')}"

            for pattern in self.dataset_patterns:

                for match in re.finditer(pattern, text):

                    d = match.group(1).strip()

                    if len(d) > 2:

                        datasets[d]['count'] += 1

                        if paper['title'] not in datasets[d]['papers']:

                            datasets[d]['papers'].append(paper['title'])

        return {k: v for k, v in datasets.items() if v['count'] > 0}


    # ─────────────────────────────────────────────
    # APPLICATION EXTRACTION
    # ─────────────────────────────────────────────

    def extract_applications(self, papers):

        apps = Counter()

        domain_kw = {

            'Healthcare': ['medical','clinical','patient','disease'],

            'Finance': ['financial','trading','stock'],

            'Education': ['learning','student','educational'],

            'Computer Vision': ['image','vision','segmentation'],

            'NLP': ['text','language','translation'],

            'Robotics': ['robot','autonomous','manipulation'],
        }

        for paper in papers:

            text = f"{paper.get('title','')} {paper.get('abstract','')}".lower()

            for domain, kws in domain_kw.items():

                if any(k in text for k in kws):

                    apps[domain] += 1

        return dict(apps)


    # ─────────────────────────────────────────────
    # LIMITATION EXTRACTION
    # ─────────────────────────────────────────────

    def extract_limitations(self, papers):

        lims = []

        kws = ['limitation','drawback','however','challenge','cannot']

        for paper in papers:

            for sent in paper.get('abstract','').split('.'):

                if any(k in sent.lower() for k in kws):

                    lims.append({

                        'paper': paper['title'],

                        'limitation': sent.strip()

                    })

        return lims


    # ─────────────────────────────────────────────
    # TEMPORAL ANALYSIS
    # ─────────────────────────────────────────────

    def analyze_temporal_distribution(self, papers):

        years = []

        for p in papers:

            pub = p.get('published','')

            if pub:

                try:

                    years.append(datetime.fromisoformat(pub.replace('Z','+00:00')).year)

                except Exception:

                    pass

        if not years:

            return {}

        yc = Counter(years)

        return {

            'earliest': min(years),

            'latest': max(years),

            'span': max(years) - min(years),

            'distribution': dict(yc)
        }


# ─────────────────────────────────────────────
# GAP DETECTION ENGINE
# ─────────────────────────────────────────────

class GapDetectionEngine:

    def __init__(self, features):

        self.features = features


    def detect_all_gaps(self):

        return {

        'methodological': self._methodological(),

        'application': self._application(),

        'dataset': self._dataset()
    }


    # ─────────────────────────────────────────────
    # METHOD GAPS
    # ─────────────────────────────────────────────

    def _methodological(self):

        gaps = []

        methods = self.features.get('methods', {})

        if not methods:

            return gaps

        method_list = [m for m in methods.keys() if len(m.split()) >= 2]

        for i, m1 in enumerate(method_list[:5]):

            for m2 in method_list[i+1:6]:

                if not (set(methods[m1]['papers']) & set(methods[m2]['papers'])):

                    gaps.append({

                        'type':'method_combination',

                        'gap':f"No studies combine '{m1}' with '{m2}'",

                        'severity':'high',

                        'opportunity':f"Investigate hybrid system combining {m1} and {m2}",

                        'score':75
                    })

        return gaps[:5]


    # ─────────────────────────────────────────────
    # EMPIRICAL GAPS
    # ─────────────────────────────────────────────

    def _empirical(self):

        gaps = []

        datasets = self.features.get('datasets', {})

        if len(datasets) < 3:

            gaps.append({

                'type':'limited_datasets',

                'gap':"Insufficient benchmark datasets for reliable evaluation",

                'severity':'medium',

                'opportunity':'Introduce additional evaluation datasets',

                'score':70
            })

        return gaps


    # ─────────────────────────────────────────────
    # APPLICATION GAPS
    # ─────────────────────────────────────────────

    def _application(self):

        gaps = []

        apps = self.features.get('applications', {})

        all_domains = [

            'Healthcare','Finance','Education',

            'Computer Vision','NLP','Robotics',

            'Agriculture','Climate'
        ]

        for domain in list(set(all_domains) - set(apps.keys()))[:3]:

            gaps.append({

                'type':'unexplored_domain',

                'gap':f"Limited research applying current methods to {domain}",

                'severity':'medium',

                'opportunity':f"Apply existing techniques to {domain}",

                'score':65
            })

        return gaps


    # ─────────────────────────────────────────────
    # DATASET GAPS
    # ─────────────────────────────────────────────

    def _dataset(self):

        gaps = []

        datasets = self.features.get('datasets', {})

        if len(datasets) < 3:

            gaps.append({

                'type':'dataset_creation',

                'gap':"Need for new benchmark datasets",

                'severity':'high',

                'opportunity':'Create new datasets addressing current limitations',

                'score':75
            })

        return gaps


    # ─────────────────────────────────────────────
    # TEMPORAL GAPS
    # ─────────────────────────────────────────────

    def _temporal(self):

        gaps = []

        temporal = self.features.get('temporal_distribution', {})

        if not temporal or 'distribution' not in temporal:

            return gaps

        dist = temporal['distribution']

        years = sorted(dist.keys())

        for i in range(len(years)-1):

            if years[i+1] - years[i] > 2:

                gaps.append({

                    'type':'temporal_gap',

                    'gap':f"Research gap between {years[i]} and {years[i+1]}",

                    'severity':'medium',

                    'opportunity':f"Investigate research developments between {years[i]}–{years[i+1]}",

                    'score':60
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

                g = gap.copy()

                g['priority'] = g.get('score', 50)

                g['confidence'] = min(100, g['priority'] * 1.1)

                g['category'] = gap_type

                validated[gap_type].append(g)

        return validated


# ─────────────────────────────────────────────
# PUBLIC API
# ─────────────────────────────────────────────

def run_systematic_gap_detection(papers: List[Dict]) -> Dict:

    features = FeatureExtractor().extract_all_features(papers)

    raw_gaps = GapDetectionEngine(features).detect_all_gaps()

    validated = GapValidator().validate_gaps(raw_gaps)

    return {

        'features': features,

        'gaps': validated
    }