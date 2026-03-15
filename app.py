"""
ResearchIt v2.0 — AI-Powered Research Intelligence Platform
Main entry point.
"""

import streamlit as st
import sys
from pathlib import Path
import os

_root = Path(__file__).parent

try:
    from dotenv import load_dotenv
    load_dotenv()
except:
    pass

sys.path.insert(0, str(_root))
sys.path.insert(0, str(_root / "services"))

# ✅ import theme FIRST
from components.theme import apply_theme

# page config must come before UI
st.set_page_config(
    page_title="ResearchIt — AI Research Intelligence",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ✅ apply theme BEFORE sidebar / pages
apply_theme()


from components.sidebar import render_sidebar


# ─── Session state bootstrap ─────────────────────────

DEFAULTS = {
    "papers": [],
    "papers_fetched": False,
    # combined_text is intentionally NOT pre-set here.
    # gaps.py builds it fresh from st.session_state.papers every time
    # the page loads, so it always reflects the current paper list.
    "current_page": "discover",

    "extracted_features": None,
    "detected_gaps": None,
    "interpreted_gaps": None,

    "impact_matrix": None,
    "relationship_graph": None,
    "prototypes": None,

    "generated_paper": None,
}

for k, v in DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v


# ─── Sidebar navigation ─────────────────────────

page = render_sidebar()


# ─── Routing ─────────────────────────

if page == "discover":

    from pages.discover import render_discover_page

    render_discover_page()


elif page == "analytics":

    from pages.analytics import render_analytics_page

    render_analytics_page()


elif page == "gaps":

    from pages.gaps import render_gaps_page

    render_gaps_page()


elif page == "proposal":

    from pages.proposal import render_proposal_page

    render_proposal_page()


elif page == "assistant":

    from pages.assistant import render_assistant_page

    render_assistant_page()


# ─── Footer ─────────────────────────

st.markdown(
    """
<div style="text-align:center;
padding:24px 0;
color:#6B7766;
font-size:13px;
border-top:1px solid #E3E7DD;
margin-top:40px;">

ResearchIt v2.0 — AI Research Platform

</div>
""",
    unsafe_allow_html=True,
)