"""
Research Opportunity Discovery Page
Shows engaging, actionable research topics - Original Black & Gold Theme

FIX: combined_text is now built on-the-fly from st.session_state.papers
     instead of reading a session key that was never populated.
"""

import streamlit as st
from datetime import datetime


def _build_combined_text(papers: list) -> str:
    """Concatenate title + abstract for every paper into one block of text."""
    chunks = []
    for p in papers:
        title    = p.get("title", "").strip()
        abstract = p.get("abstract", p.get("summary", "")).strip()
        if title or abstract:
            chunks.append(f"{title}\n{abstract}")
    return "\n\n---\n\n".join(chunks)


def render_gaps_page():
    st.markdown("""
    <div class="hero-section">
        <div class="hero-title">🎯 Research Opportunity Discovery</div>
        <div class="hero-subtitle">
            Find your next research topic — we'll show you hot opportunities based on what's missing in the literature
        </div>
    </div>""", unsafe_allow_html=True)

    if not st.session_state.get("papers_fetched") or not st.session_state.get("papers"):
        st.markdown("""
        <div class="glass-card" style="text-align:center; padding:60px;">
            <h2 style="color:#F5F5F0;">No Papers Available</h2>
            <p style="color:#C0C0C0;">Fetch papers from Discover first to find research opportunities.</p>
        </div>""", unsafe_allow_html=True)
        if st.button("🔍 Go to Discover", use_container_width=True, type="primary"):
            st.session_state.current_page = "discover"
            st.rerun()
        return

    # ── Build combined_text from papers (fixes "No text provided" error) ──────
    papers = st.session_state.papers
    combined_text = _build_combined_text(papers)
    # Also persist it so other pages can use it if needed
    st.session_state.combined_text = combined_text

    # ── Quick AI Analysis ─────────────────────────────────────────────────────
    st.markdown("<div class='section-title'>🤖 Quick AI Insights</div>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    action = None
    if c1.button("📊 Research Summary",  use_container_width=True): action = "Research Summary"
    if c2.button("🔍 AI Gap Detection",  use_container_width=True): action = "Gap Detection"
    if c3.button("🚀 Future Topics",     use_container_width=True): action = "Future Topics"

    if action:
        if not combined_text.strip():
            st.warning("⚠️ Papers have no text content. Please re-fetch papers.")
        else:
            from services.simple_rag import generate_summary
            with st.spinner(f"Generating {action}…"):
                result = generate_summary(combined_text, action)
            st.markdown(
                f"<div class='glass-card'><strong>{action}</strong><br><br>{result}</div>",
                unsafe_allow_html=True
            )

    # ── Main Discovery ────────────────────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>🔬 Discover Research Opportunities</div>",
                unsafe_allow_html=True)

    st.markdown("""
    <div class="glass-card" style="padding:20px 24px; margin-bottom:20px;">
        <p style="color:#C0C0C0; margin:0; font-size:14px;">
        We'll analyze your papers and identify <strong style="color:#D4AF37;">specific research topics</strong>
        you can pursue. Each topic includes difficulty rating, timeline estimate, and concrete first steps.
        </p>
    </div>""", unsafe_allow_html=True)

    if st.button("🚀 Find Research Opportunities", use_container_width=True, type="primary"):
        _run_discovery()

    # ── Display Results ───────────────────────────────────────────────────────
    if not st.session_state.get("detected_gaps"):
        return

    opportunities = st.session_state.get("opportunities")
    if not opportunities:
        st.info("Run opportunity discovery first.")
        return

    st.markdown("<br>", unsafe_allow_html=True)

    # Stats overview
    summary = opportunities.get("summary", {})
    c1, c2, c3, c4 = st.columns(4)
    for col, val, lbl in zip(
        [c1, c2, c3, c4],
        [
            summary.get("total_opportunities", 0),
            summary.get("quick_win_count", 0),
            summary.get("high_impact_count", 0),
            f"{summary.get('avg_opportunity_score', 0)}/100"
        ],
        ["Total Topics", "Quick Wins", "High Impact", "Avg Score"]
    ):
        with col:
            st.markdown(f"""
            <div class="glass-card" style="text-align:center; padding:18px 12px;">
                <div style="font-size:28px; font-weight:700; color:#D4AF37;">{val}</div>
                <div style="font-size:11px; color:#808080; text-transform:uppercase;">{lbl}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Topic tabs
    tabs = st.tabs(["🔥 Hot Topics", "⚡ Quick Wins", "💎 High Impact", "📊 All Topics"])

    with tabs[0]:
        _render_topic_list(opportunities.get("hot_topics", []),
                           "🔥 Top Research Opportunities",
                           "These are the hottest research topics based on novelty, impact, and feasibility.")
    with tabs[1]:
        _render_topic_list(opportunities.get("quick_wins", []),
                           "⚡ Beginner-Friendly Topics",
                           "Perfect for getting started — these topics are accessible and have clear pathways.")
    with tabs[2]:
        _render_topic_list(opportunities.get("high_impact", []),
                           "💎 High-Impact Research",
                           "Advanced topics with potential for significant contributions to the field.")
    with tabs[3]:
        _render_all_topics_table(opportunities)

    # Export
    st.markdown("<br>", unsafe_allow_html=True)
    report = _build_report(opportunities)
    st.download_button("📥 Download Research Topics Report", report,
                       "research_opportunities.md", "text/markdown")


# ─────────────────────────────────────────────────────────────────────────────
# Discovery runner
# ─────────────────────────────────────────────────────────────────────────────

def _run_discovery():
    from services.gap_detection import run_systematic_gap_detection
    from services.gap_interpreter import interpret_gaps
    from services.gap_intelligence import run_gap_intelligence

    with st.spinner("🔬 Analyzing papers and discovering opportunities…"):
        result     = run_systematic_gap_detection(st.session_state.papers)
        raw_gaps   = result["gaps"]
        st.session_state.extracted_features = result["features"]
        st.session_state.detected_gaps      = raw_gaps

        interpreted = interpret_gaps(raw_gaps)
        st.session_state.interpreted_gaps   = interpreted

        intel = run_gap_intelligence(interpreted, st.session_state.papers)
        st.session_state.opportunities      = intel.get("opportunities", {})

    total = st.session_state.opportunities.get("summary", {}).get("total_opportunities", 0)
    st.success(f"✅ Discovered {total} research opportunities!")
    st.rerun()


# ─────────────────────────────────────────────────────────────────────────────
# Rendering helpers  (unchanged)
# ─────────────────────────────────────────────────────────────────────────────

_DIFF_COLOR = {"Beginner-Friendly": "#22c55e", "Intermediate": "#f59e0b", "Advanced": "#ef4444"}
_DIFF_ICON  = {"Beginner-Friendly": "🟢",      "Intermediate": "🟡",      "Advanced": "🔴"}


def _render_topic_list(topics: list, title: str, subtitle: str):
    if not topics:
        st.info("No topics in this category.")
        return

    st.markdown(f"### {title}")
    st.markdown(f"<p style='color:#C0C0C0; margin-bottom:20px;'>{subtitle}</p>",
                unsafe_allow_html=True)

    for i, topic in enumerate(topics, 1):
        diff     = topic.get("difficulty", "Intermediate")
        color    = _DIFF_COLOR.get(diff, "#f59e0b")
        icon     = _DIFF_ICON.get(diff, "🟡")
        score    = topic.get("opportunity_score", 0)
        timeline = topic.get("estimated_timeline", "6-12 months")

        with st.expander(
            f"{icon} **{topic.get('topic_title', 'Research Topic')}** — Score: {score}/100",
            expanded=(i == 1)
        ):
            st.markdown(f"""
            <div style="display:flex; gap:8px; flex-wrap:wrap; margin-bottom:16px;">
                <span style="background:{color}22; color:{color}; border:1px solid {color}44;
                             border-radius:20px; padding:4px 12px; font-size:12px; font-weight:700;">
                    {icon} {diff}
                </span>
                <span style="background:rgba(212,175,55,.15); color:#D4AF37;
                             border:1px solid rgba(212,175,55,.3); border-radius:20px;
                             padding:4px 12px; font-size:12px; font-weight:700;">
                    ⏱️ {timeline}
                </span>
                <span style="background:rgba(96,165,250,.15); color:#60a5fa;
                             border:1px solid rgba(96,165,250,.3); border-radius:20px;
                             padding:4px 12px; font-size:12px; font-weight:700;">
                    🎯 Score: {score}/100
                </span>
            </div>""", unsafe_allow_html=True)

            keywords = topic.get("keywords", [])
            if keywords:
                kw_html = " ".join([
                    f"<span style='background:#3A3A3A; color:#D4AF37; padding:3px 8px; "
                    f"border-radius:12px; font-size:11px; margin-right:4px;'>{kw}</span>"
                    for kw in keywords
                ])
                st.markdown(f"<div style='margin-bottom:16px;'>{kw_html}</div>",
                            unsafe_allow_html=True)

            pitch = topic.get("research_pitch", "")
            if pitch:
                st.markdown(f"""
                <div style="background:#2A2A2A; border-left:3px solid #D4AF37;
                            padding:12px 16px; border-radius:6px; margin-bottom:16px;">
                    <strong style="color:#D4AF37; font-size:13px; text-transform:uppercase;">
                        💡 Why This Topic?
                    </strong>
                    <p style="color:#F5F5F0; margin:8px 0 0 0; line-height:1.6;">{pitch}</p>
                </div>""", unsafe_allow_html=True)

            approach = topic.get("concrete_approach", "")
            if approach:
                st.markdown("**🛠️ Research Approach:**")
                for line in approach.split('\n'):
                    if line.strip():
                        st.markdown(f"- {line.strip()}")

            why = topic.get("why_it_matters", "")
            if why:
                st.markdown(f"""
                <div style="background:rgba(34,197,94,.08); border:1px solid rgba(34,197,94,.2);
                            padding:10px 14px; border-radius:6px; margin:12px 0;">
                    <strong style="color:#22c55e;">🌟 Impact:</strong>
                    <span style="color:#F5F5F0;"> {why}</span>
                </div>""", unsafe_allow_html=True)

            steps = topic.get("first_steps", "")
            if steps:
                st.markdown("**🚀 Getting Started (This Week):**")
                for line in steps.split('\n'):
                    if line.strip():
                        st.markdown(f"1. {line.strip()}")

            st.markdown("### 📋 Technical Details")
            st.markdown(f"**Original Gap:** {topic.get('original_gap','')}")
            st.markdown(f"**Category:** {topic.get('category','').title()}")
            st.markdown(f"**Severity:** {topic.get('severity','medium').upper()}")


def _render_all_topics_table(opportunities):
    st.markdown("### 📊 All Research Topics")
    import pandas as pd
    all_topics = opportunities.get("hot_topics", [])
    if not all_topics:
        st.info("No topics available.")
        return
    df = pd.DataFrame([{
        "Topic":      t.get("topic_title", "")[:60] + "…",
        "Difficulty": t.get("difficulty", ""),
        "Score":      t.get("opportunity_score", 0),
        "Timeline":   t.get("estimated_timeline", ""),
        "Keywords":   ", ".join(t.get("keywords", [])[:3]),
    } for t in all_topics])
    st.dataframe(df, use_container_width=True, hide_index=True)


def _build_report(opportunities):
    summary = opportunities.get("summary", {})
    hot     = opportunities.get("hot_topics", [])
    lines   = [
        "# Research Opportunity Report",
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "", "## Summary", "",
        f"- **Total Opportunities:** {summary.get('total_opportunities', 0)}",
        f"- **Quick Wins:** {summary.get('quick_win_count', 0)}",
        f"- **High Impact:** {summary.get('high_impact_count', 0)}",
        f"- **Average Score:** {summary.get('avg_opportunity_score', 0)}/100",
        "", "## 🔥 Hot Topics\n",
    ]
    for i, t in enumerate(hot, 1):
        lines += [
            f"\n### {i}. {t.get('topic_title', '')}",
            "",
            f"**Difficulty:** {t.get('difficulty','')} | "
            f"**Score:** {t.get('opportunity_score',0)}/100 | "
            f"**Timeline:** {t.get('estimated_timeline','')}",
            "", "**Research Pitch:**", t.get("research_pitch", ""), "",
            "**Approach:**",
            *[f"- {l.strip()}" for l in t.get("concrete_approach","").split('\n') if l.strip()],
            "\n---\n"
        ]
    return "\n".join(lines)