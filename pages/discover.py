"""Discover Papers Page — Academic Theme with ResearchIt branding"""

import streamlit as st
from arxiv_helper import fetch_papers
import logging

logger = logging.getLogger(__name__)


# ── UI helpers ────────────────────────────────────────────────────────────────

def _hero():
    """Full-page hero with ResearchIt logo — solid gold color, always visible."""
    st.markdown("""
    <div style="text-align:center; padding:44px 0 36px 0;">
        <div style="font-size:54px; line-height:1; margin-bottom:14px;">🔬</div>
        <div style="font-family:'Playfair Display',Georgia,serif;
            font-size:46px; font-weight:800; letter-spacing:-0.03em;
            color:#D4AF37; line-height:1.05; margin-bottom:8px;">
            ResearchIt
        </div>
        <div style="font-family:'Source Serif 4',Georgia,serif;
            color:#6E6A5E; font-size:10px; letter-spacing:.2em;
            text-transform:uppercase; margin-bottom:20px; font-weight:400;">
            AI Research Intelligence Platform
        </div>
        <div style="width:56px; height:1px;
            background:linear-gradient(90deg,transparent,#C9A030,transparent);
            margin:0 auto 22px auto;"></div>
        <div style="font-family:'Playfair Display',Georgia,serif;
            font-size:22px; font-weight:600; color:#E8E4DC;
            margin-bottom:10px; letter-spacing:-0.01em;">
            🔍 Discover Research Papers
        </div>
        <div style="font-family:'Source Serif 4',Georgia,serif;
            color:#9E9A8E; font-size:15px; font-weight:300; line-height:1.65;">
            Search, retrieve, and analyse papers from ArXiv to fuel your research
        </div>
    </div>
    """, unsafe_allow_html=True)


def section_header(title, icon="📋"):
    st.markdown(f"""
    <div style="padding:18px 0 12px 0;">
        <h2 style="font-family:'Playfair Display',Georgia,serif;
            font-size:20px; font-weight:700; color:#E8E4DC; margin:0;
            letter-spacing:-0.01em;">
            {icon} {title}
        </h2>
    </div>
    """, unsafe_allow_html=True)


def card_start(padding="22px"):
    st.markdown(f"""
    <div style="background:#161512; border:1px solid #2A2820; border-radius:4px;
        padding:{padding}; margin-bottom:18px;">
    """, unsafe_allow_html=True)


def card_end():
    st.markdown("</div>", unsafe_allow_html=True)


def spacing(px=10):
    st.markdown(f"<div style='height:{px}px;'></div>", unsafe_allow_html=True)


def metric_card(value, label, icon=""):
    return f"""
    <div style="background:#161512; border:1px solid #2A2820; border-radius:4px;
        padding:18px; text-align:center;">
        <div style="font-family:'Playfair Display',Georgia,serif;
            font-size:28px; font-weight:700; color:#D4AF37; margin-bottom:6px;">
            {icon} {value}
        </div>
        <div style="font-family:'Source Serif 4',Georgia,serif;
            font-size:11px; color:#6E6A5E; font-weight:400;
            text-transform:uppercase; letter-spacing:0.08em;">
            {label}
        </div>
    </div>
    """


# ── Main page ─────────────────────────────────────────────────────────────────

def render_discover_page():
    _hero()

    # Session state init
    for key, default in [
        ("papers", []),
        ("papers_fetched", False),
        ("collection", []),
        ("saved_papers", []),
    ]:
        if key not in st.session_state:
            st.session_state[key] = default

    # ── Search section ────────────────────────────────────────────────────
    section_header("Search Papers", "🔎")
    card_start()

    st.markdown("""
    <p style="font-family:'Source Serif 4',Georgia,serif;
        color:#9E9A8E; font-size:14px; margin-bottom:16px; line-height:1.7;
        font-weight:300;">
        Enter keywords to search ArXiv for research papers.
        Separate multiple keywords with spaces or commas.
    </p>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([3, 1])
    with col1:
        query = st.text_input(
            "Search Query",
            placeholder="e.g., transformer attention mechanism, BERT language model...",
            label_visibility="collapsed",
            key="search_query"
        )
    with col2:
        spacing(8)
        search_button = st.button("🔍 Search", use_container_width=True, type="primary")

    spacing(8)
    col1, col2 = st.columns(2)
    with col1:
        max_results = st.slider(
            "Number of Papers", min_value=5, max_value=50, value=10, step=5,
            help="How many papers to fetch from ArXiv"
        )
    with col2:
        use_sample = st.checkbox(
            "Use Sample Papers", value=False,
            help="Use demo papers instead of fetching from ArXiv"
        )

    card_end()

    # ── Handle search ─────────────────────────────────────────────────────
    if search_button and query:
        spacing(10)
        with st.spinner("Retrieving papers from ArXiv…"):
            try:
                papers, success, message = fetch_papers(
                    query, max_results=max_results, use_sample=use_sample
                )
                if success:
                    st.session_state.papers = papers
                    st.session_state.papers_fetched = True
                    if "sample" in message.lower():
                        st.warning(f"⚠️ {message}")
                    else:
                        st.success(f"✅ {message}")
                else:
                    st.session_state.papers = papers
                    st.session_state.papers_fetched = True
                    st.warning(f"⚠️ {message}")
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
                logger.error(f"Search error: {e}")

    # ── Display results ───────────────────────────────────────────────────
    if st.session_state.papers_fetched and st.session_state.papers:
        papers = st.session_state.papers
        spacing(20)

        section_header(f"Papers Found ({len(papers)})", "📚")

        # Summary metrics
        col1, col2, col3 = st.columns(3)
        years = set(p.get("year", "Unknown") for p in papers)
        all_authors = set()
        for p in papers:
            all_authors.update(p.get("authors", []))

        with col1:
            st.markdown(metric_card(str(len(papers)), "Total Papers", "📄"),
                        unsafe_allow_html=True)
        with col2:
            st.markdown(metric_card(str(len(years)), "Years Covered", "📅"),
                        unsafe_allow_html=True)
        with col3:
            st.markdown(metric_card(str(len(all_authors)), "Unique Authors", "👥"),
                        unsafe_allow_html=True)

        spacing(18)

        # Individual paper cards
        for idx, paper in enumerate(papers, 1):
            card_start()

            st.markdown(f"""
            <h3 style="font-family:'Playfair Display',Georgia,serif;
                font-size:17px; font-weight:700; color:#E8E4DC;
                margin:0 0 10px 0; line-height:1.4;">
                {idx}. {paper.get('title', 'Untitled')}
            </h3>
            """, unsafe_allow_html=True)

            authors = paper.get("authors", [])
            if authors:
                auth_str = ", ".join(authors[:3])
                if len(authors) > 3:
                    auth_str += f" +{len(authors)-3} more"
                st.markdown(f"""
                <p style="font-family:'Source Serif 4',Georgia,serif;
                    font-size:13px; color:#9E9A8E; margin:0 0 6px 0;">
                    <span style="color:#6E6A5E;font-size:11px;text-transform:uppercase;
                        letter-spacing:0.06em;">Authors</span>&nbsp;&nbsp;{auth_str}
                </p>
                """, unsafe_allow_html=True)

            year = paper.get("year", "Unknown")
            arxiv_id = paper.get("arxiv_id", "")
            st.markdown(f"""
            <p style="font-family:'JetBrains Mono',monospace;
                font-size:11px; color:#6E6A5E; margin:0 0 12px 0;">
                {year} &nbsp;·&nbsp; arXiv:{arxiv_id}
            </p>
            """, unsafe_allow_html=True)

            summary = paper.get("summary", "No summary available")[:500]
            if len(paper.get("summary", "")) > 500:
                summary += "…"
            st.markdown(f"""
            <p style="font-family:'Source Serif 4',Georgia,serif;
                font-size:14px; color:#C8C4BC; margin:0; line-height:1.7;
                font-weight:300;">
                {summary}
            </p>
            """, unsafe_allow_html=True)

            spacing(12)
            c1, c2, c3 = st.columns(3)
            with c1:
                if st.button("🔗 View on ArXiv", key=f"view_{idx}", use_container_width=True):
                    st.markdown(f"[Open on ArXiv ↗]({paper.get('url', '#')})")
            with c2:
                if st.button(f"💾 Save Paper", key=f"save_{idx}", use_container_width=True):
                    if paper not in st.session_state.saved_papers:
                        st.session_state.saved_papers.append(paper)
                        st.success("Saved")
                    else:
                        st.info("Already saved")
            with c3:
                if st.button(f"📋 Add to Collection", key=f"add_{idx}",
                             use_container_width=True):
                    if paper not in st.session_state.collection:
                        st.session_state.collection.append(paper)
                        st.success("Added to collection")
                    else:
                        st.info("Already in collection")

            card_end()
            spacing(4)

        # Actions
        spacing(16)
        c1, c2, c3 = st.columns(3)
        with c1:
            if st.button("✅ Confirm Selection", use_container_width=True, type="primary"):
                st.success("✅ Papers added to your collection!")
                st.balloons()
        with c2:
            if st.button("🔄 New Search", use_container_width=True):
                st.session_state.papers = []
                st.session_state.papers_fetched = False
                st.rerun()
        with c3:
            if st.button("📥 Export Papers", use_container_width=True):
                st.info("📥 Export functionality coming soon")

    elif st.session_state.papers_fetched and not st.session_state.papers:
        spacing(20)
        st.warning("No papers found. Please try different keywords.")

    else:
        spacing(20)
        st.markdown("""
        <div style="background:#161512; border:1px solid #2A2820; border-radius:4px;
            padding:32px 28px;">
            <h3 style="font-family:'Playfair Display',Georgia,serif;
                font-size:17px; font-weight:600; color:#E8E4DC; margin:0 0 14px 0;">
                📖 How to Get Started
            </h3>
            <ol style="font-family:'Source Serif 4',Georgia,serif;
                color:#9E9A8E; font-size:14px; line-height:2; margin:0; padding-left:20px;
                font-weight:300;">
                <li>Enter your research keywords in the search box above</li>
                <li>Set how many papers you want to retrieve (5–50)</li>
                <li>Click <strong style="color:#D4AF37;">Search</strong> to fetch papers from ArXiv</li>
                <li>Review the papers and their abstracts</li>
                <li>Click <strong style="color:#D4AF37;">Confirm Selection</strong> to add them to your collection</li>
                <li>Navigate to <strong style="color:#D4AF37;">Gap Detection</strong> or <strong style="color:#D4AF37;">Research Paper</strong> to analyse</li>
            </ol>
        </div>
        """, unsafe_allow_html=True)


if __name__ == "__main__":
    render_discover_page()