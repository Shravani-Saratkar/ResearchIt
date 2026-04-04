"""
Research Opportunity Discovery Page — Academic Theme
- Research Summary and Gap Detection shown side-by-side
- Future Topics removed (logic merged into Discover Research Opportunities)
- Discover Research Opportunities structure unchanged
- Minimum 5 opportunities guaranteed via gap_intelligence
"""

import streamlit as st
from datetime import datetime
import re as _re


# ── Controlled markdown renderer ──────────────────────────────────────────────
# Prevents Streamlit's giant default heading sizes from breaking typography.

def _render_ai_output(text: str):
    html_lines = []
    for line in text.split("\n"):
        s = line.strip()

        if s.startswith("## "):
            h = s[3:].strip()
            html_lines.append(
                '<div style="'
                "font-family:'Playfair Display',Georgia,serif;"
                "font-size:13px;font-weight:700;color:#D4AF37;"
                "text-transform:uppercase;letter-spacing:0.08em;"
                "margin:20px 0 7px 0;padding-bottom:5px;"
                'border-bottom:1px solid #2A2820;">'
                + h + "</div>"
            )
        elif s.startswith("### "):
            h = s[4:].strip()
            html_lines.append(
                '<div style="'
                "font-family:'Playfair Display',Georgia,serif;"
                "font-size:13px;font-weight:600;color:#E8E4DC;"
                'margin:14px 0 5px 0;">'
                + h + "</div>"
            )
        elif _re.match(r"^\*\*.+\*\*$", s) or _re.match(r"^\*\*.+\*\*:", s):
            h = _re.sub(r"\*\*(.+?)\*\*:?", r"\1", s).strip()
            html_lines.append(
                '<div style="'
                "font-family:'Playfair Display',Georgia,serif;"
                "font-size:13px;font-weight:700;color:#D4AF37;"
                "text-transform:uppercase;letter-spacing:0.07em;"
                "margin:20px 0 7px 0;padding-bottom:5px;"
                'border-bottom:1px solid #2A2820;">'
                + h + "</div>"
            )
        elif s.startswith(("• ", "- ")):
            body = _re.sub(
                r"\*\*(.+?)\*\*",
                r'<strong style="color:#E8E4DC;font-weight:600;">\1</strong>',
                s[2:].strip()
            )
            html_lines.append(
                '<div style="display:flex;gap:9px;margin:5px 0;align-items:flex-start;">'
                '<span style="color:#C9A030;font-size:13px;flex-shrink:0;margin-top:3px;">•</span>'
                '<span style="'
                "font-family:'Source Serif 4',Georgia,serif;"
                "font-size:13px;color:#C8C4BC;line-height:1.75;font-weight:300;"
                '">' + body + "</span></div>"
            )
        elif _re.match(r"^\d+\.\s", s):
            body = _re.sub(
                r"\*\*(.+?)\*\*",
                r'<strong style="color:#E8E4DC;font-weight:600;">\1</strong>',
                s
            )
            html_lines.append(
                '<div style="'
                "font-family:'Source Serif 4',Georgia,serif;"
                "font-size:13px;color:#C8C4BC;line-height:1.75;font-weight:300;"
                'margin:4px 0 4px 14px;">'
                + body + "</div>"
            )
        elif s == "":
            html_lines.append('<div style="height:4px;"></div>')
        else:
            body = _re.sub(
                r"\*\*(.+?)\*\*",
                r'<strong style="color:#E8E4DC;font-weight:600;">\1</strong>',
                s
            )
            html_lines.append(
                '<div style="'
                "font-family:'Source Serif 4',Georgia,serif;"
                "font-size:13px;color:#C8C4BC;line-height:1.75;font-weight:300;"
                'margin:2px 0;">'
                + body + "</div>"
            )

    st.markdown(
        '<div style="padding:2px 0;">' + "\n".join(html_lines) + "</div>",
        unsafe_allow_html=True,
    )


# ── Helpers ───────────────────────────────────────────────────────────────────

def _build_combined_text(papers: list) -> str:
    chunks = []
    for p in papers:
        title    = p.get("title", "").strip()
        abstract = p.get("abstract", p.get("summary", "")).strip()
        if title or abstract:
            chunks.append(f"{title}\n{abstract}")
    return "\n\n---\n\n".join(chunks)


def _section_title(text: str):
    st.markdown(f"""
    <div style="font-family:'Playfair Display',Georgia,serif;
        font-size:17px; font-weight:700; color:#E8E4DC;
        margin:26px 0 12px 0; padding-bottom:7px;
        border-bottom:1px solid #2A2820; letter-spacing:-0.01em;">
        {text}
    </div>
    """, unsafe_allow_html=True)


def _insight_card(label: str, content_fn):
    """Render a labelled insight card — label + rendered AI output."""
    st.markdown(f"""
    <div style="background:#161512; border:1px solid #2A2820; border-radius:4px;
        padding:16px 18px 14px 18px; height:100%;">
        <div style="font-family:'Playfair Display',Georgia,serif;
            font-size:12px; font-weight:700; color:#D4AF37;
            text-transform:uppercase; letter-spacing:0.09em;
            margin-bottom:10px; padding-bottom:6px;
            border-bottom:1px solid #2A2820;">
            {label}
        </div>
    """, unsafe_allow_html=True)
    content_fn()
    st.markdown("</div>", unsafe_allow_html=True)


def _stat_card(value, label):
    return f"""
    <div style="background:#161512; border:1px solid #2A2820; border-radius:4px;
        padding:14px 8px; text-align:center;">
        <div style="font-family:'Playfair Display',Georgia,serif;
            font-size:24px; font-weight:700; color:#D4AF37; line-height:1;">
            {value}
        </div>
        <div style="font-family:'Source Serif 4',Georgia,serif;
            font-size:10px; color:#6E6A5E; text-transform:uppercase;
            letter-spacing:0.1em; margin-top:5px; font-weight:400;">
            {label}
        </div>
    </div>
    """


# ── Main page ─────────────────────────────────────────────────────────────────

def render_gaps_page():
    st.markdown("""
    <div style="background:linear-gradient(135deg,#1A1915 0%,#161512 50%,#1E1B16 100%);
        border:1px solid #2E2B22; border-radius:4px; padding:44px 36px;
        text-align:center; margin-bottom:24px; position:relative; overflow:hidden;">
        <div style="position:absolute;top:0;left:0;right:0;bottom:0;
            background:radial-gradient(ellipse at 50% 0%,rgba(212,175,55,0.06) 0%,transparent 65%);
            pointer-events:none;"></div>
        <div style="font-family:'Playfair Display',Georgia,serif;
            font-size:32px; font-weight:800; letter-spacing:-0.02em; color:#D4AF37;
            margin-bottom:10px;">
            🎯 Research Opportunity Discovery
        </div>
        <div style="font-family:'Source Serif 4',Georgia,serif; color:#9E9A8E;
            font-size:14px; font-weight:300; line-height:1.65; max-width:520px;
            margin:0 auto;">
            Uncover specific, actionable research topics derived from gaps in your literature
        </div>
    </div>
    """, unsafe_allow_html=True)

    if not st.session_state.get("papers_fetched") or not st.session_state.get("papers"):
        st.markdown("""
        <div style="background:#161512; border:1px solid #2A2820; border-radius:4px;
            text-align:center; padding:56px 40px;">
            <div style="font-size:44px; margin-bottom:14px; opacity:0.2;">🎯</div>
            <div style="font-family:'Playfair Display',Georgia,serif;
                color:#E8E4DC; font-size:18px; font-weight:700; margin-bottom:10px;">
                No Papers Available
            </div>
            <div style="font-family:'Source Serif 4',Georgia,serif;
                color:#9E9A8E; font-size:14px; font-weight:300;">
                Fetch papers from Discover first, then return here to analyse them.
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("<div style='height:14px;'></div>", unsafe_allow_html=True)
        if st.button("🔍 Go to Discover", use_container_width=True, type="primary"):
            st.session_state.current_page = "discover"
            st.rerun()
        return

    papers        = st.session_state.papers
    combined_text = _build_combined_text(papers)
    st.session_state.combined_text = combined_text

    # ── Quick AI Insights — Research Summary | Gap Detection side by side ──────
    _section_title("🤖 Quick AI Insights")

    col_btn1, col_btn2 = st.columns(2)
    run_summary = col_btn1.button("📊 Research Summary",  use_container_width=True)
    run_gaps    = col_btn2.button("🔍 AI Gap Detection",  use_container_width=True)

    # Store results in session state so both columns persist after rerun
    if run_summary:
        if not combined_text.strip():
            st.warning("Papers have no text content. Please re-fetch.")
        else:
            from services.simple_rag import generate_summary
            with st.spinner("Generating Research Summary…"):
                st.session_state["_insight_summary"] = generate_summary(
                    combined_text, "Research Summary"
                )

    if run_gaps:
        if not combined_text.strip():
            st.warning("Papers have no text content. Please re-fetch.")
        else:
            from services.simple_rag import generate_summary
            with st.spinner("Generating Gap Detection…"):
                st.session_state["_insight_gaps"] = generate_summary(
                    st.session_state.papers, "Gap Detection"
                )

    # Render both side by side if either result exists
    summary_result = st.session_state.get("_insight_summary")
    gaps_result    = st.session_state.get("_insight_gaps")

    if summary_result or gaps_result:
        col_l, col_r = st.columns(2)

        with col_l:
            st.markdown("""
            <div style="background:#161512; border:1px solid #2A2820; border-radius:4px;
                padding:16px 18px 14px 18px; min-height:160px;">
                <div style="font-family:'Playfair Display',Georgia,serif;
                    font-size:11px; font-weight:700; color:#D4AF37;
                    text-transform:uppercase; letter-spacing:0.1em;
                    margin-bottom:10px; padding-bottom:6px;
                    border-bottom:1px solid #2A2820;">
                    📊 Research Summary
                </div>
            """, unsafe_allow_html=True)
            if summary_result:
                _render_ai_output(summary_result)
            else:
                st.markdown(
                    '<div style="font-family:\'Source Serif 4\',Georgia,serif;'
                    'font-size:13px;color:#6E6A5E;font-weight:300;padding:8px 0;">'
                    'Click Research Summary above to generate.</div>',
                    unsafe_allow_html=True
                )
            st.markdown("</div>", unsafe_allow_html=True)

        with col_r:
            st.markdown("""
            <div style="background:#161512; border:1px solid #2A2820; border-radius:4px;
                padding:16px 18px 14px 18px; min-height:160px;">
                <div style="font-family:'Playfair Display',Georgia,serif;
                    font-size:11px; font-weight:700; color:#D4AF37;
                    text-transform:uppercase; letter-spacing:0.1em;
                    margin-bottom:10px; padding-bottom:6px;
                    border-bottom:1px solid #2A2820;">
                    🔍 Gap Detection
                </div>
            """, unsafe_allow_html=True)
            if gaps_result:
                _render_ai_output(gaps_result)
            else:
                st.markdown(
                    '<div style="font-family:\'Source Serif 4\',Georgia,serif;'
                    'font-size:13px;color:#6E6A5E;font-weight:300;padding:8px 0;">'
                    'Click AI Gap Detection above to generate.</div>',
                    unsafe_allow_html=True
                )
            st.markdown("</div>", unsafe_allow_html=True)

    # ── Discover Research Opportunities (structure unchanged) ─────────────────
    st.markdown("<div style='height:10px;'></div>", unsafe_allow_html=True)
    _section_title("🔬 Discover Research Opportunities")

    st.markdown("""
    <div style="background:#161512; border:1px solid #2A2820; border-radius:4px;
        padding:16px 20px; margin-bottom:18px;">
        <p style="font-family:'Source Serif 4',Georgia,serif; color:#9E9A8E;
            font-size:13px; margin:0; line-height:1.7; font-weight:300;">
            Analyse your papers to surface <strong style="color:#D4AF37;">specific research topics</strong>
            you can pursue — grounded in detected gaps and future-scope directions stated by the authors.
            Each opportunity includes a difficulty rating, timeline, and concrete first steps.
        </p>
    </div>
    """, unsafe_allow_html=True)

    if st.button("🚀 Find Research Opportunities", use_container_width=True, type="primary"):
        _run_discovery()

    if not st.session_state.get("detected_gaps"):
        return

    opportunities = st.session_state.get("opportunities")
    if not opportunities:
        st.info("Run opportunity discovery to see results.")
        return

    st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)

    # Stats row
    summary = opportunities.get("summary", {})
    c1, c2, c3, c4 = st.columns(4)
    for col, val, lbl in zip(
        [c1, c2, c3, c4],
        [
            summary.get("total_opportunities", 0),
            summary.get("quick_win_count", 0),
            summary.get("high_impact_count", 0),
            f"{summary.get('avg_opportunity_score', 0):.0f}/100",
        ],
        ["Opportunities", "Quick Wins", "High Impact", "Avg Score"]
    ):
        with col:
            st.markdown(_stat_card(val, lbl), unsafe_allow_html=True)

    st.markdown("<div style='height:14px;'></div>", unsafe_allow_html=True)

    tabs = st.tabs(["🔥 Hot Topics", "⚡ Quick Wins", "💎 High Impact", "📊 All Topics"])
    with tabs[0]:
        _render_topic_list(
            opportunities.get("hot_topics", []),
            "🔥 Top Research Opportunities",
            "Highest-ranking topics by novelty, impact, and feasibility — grounded in your papers."
        )
    with tabs[1]:
        _render_topic_list(
            opportunities.get("quick_wins", []),
            "⚡ Accessible Entry Points",
            "Research directions with clear pathways drawn from your literature."
        )
    with tabs[2]:
        _render_topic_list(
            opportunities.get("high_impact", []),
            "💎 High-Impact Research",
            "Advanced topics with potential for significant contributions."
        )
    with tabs[3]:
        _render_all_topics_table(opportunities)

    st.markdown("<div style='height:10px;'></div>", unsafe_allow_html=True)
    report = _build_report(opportunities)
    st.download_button(
        "📥 Download Research Opportunities Report",
        report, "research_opportunities.md", "text/markdown",
        use_container_width=True
    )


# ── Discovery runner ──────────────────────────────────────────────────────────

def _run_discovery():
    from services.gap_detection   import run_systematic_gap_detection
    from services.gap_interpreter import interpret_gaps
    from services.gap_intelligence import run_gap_intelligence

    with st.spinner("Analysing papers and discovering research opportunities…"):
        result   = run_systematic_gap_detection(st.session_state.papers)
        raw_gaps = result["gaps"]
        st.session_state.extracted_features = result["features"]
        st.session_state.detected_gaps      = raw_gaps

        interpreted = interpret_gaps(raw_gaps)
        st.session_state.interpreted_gaps   = interpreted

        intel = run_gap_intelligence(interpreted, st.session_state.papers)
        st.session_state.opportunities = intel.get("opportunities", {})

    total = st.session_state.opportunities.get("summary", {}).get("total_opportunities", 0)
    st.success(f"✅ Discovered {total} research opportunities.")
    st.rerun()


# ── Topic card rendering (structure unchanged) ────────────────────────────────

_DIFF_COLOR = {
    "Beginner-Friendly": "#22c55e",
    "Intermediate":      "#f59e0b",
    "Advanced":          "#ef4444",
}
_DIFF_ICON = {
    "Beginner-Friendly": "🟢",
    "Intermediate":      "🟡",
    "Advanced":          "🔴",
}


def _render_topic_list(topics: list, title: str, subtitle: str):
    if not topics:
        st.info("No topics in this category.")
        return

    st.markdown(f"""
    <div style="font-family:'Playfair Display',Georgia,serif;
        font-size:17px; font-weight:700; color:#E8E4DC; margin:8px 0 5px 0;">
        {title}
    </div>
    <div style="font-family:'Source Serif 4',Georgia,serif; color:#9E9A8E;
        font-size:13px; margin-bottom:16px; font-weight:300;">{subtitle}</div>
    """, unsafe_allow_html=True)

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
            # Badge row
            st.markdown(f"""
            <div style="display:flex; gap:7px; flex-wrap:wrap; margin-bottom:12px;">
                <span style="background:{color}18; color:{color}; border:1px solid {color}40;
                    border-radius:2px; padding:2px 9px; font-size:11px; font-weight:600;
                    font-family:'Source Serif 4',Georgia,serif; letter-spacing:0.04em;">
                    {icon} {diff}
                </span>
                <span style="background:rgba(212,175,55,.1); color:#D4AF37;
                    border:1px solid rgba(212,175,55,.25); border-radius:2px;
                    padding:2px 9px; font-size:11px; font-weight:600;
                    font-family:'Source Serif 4',Georgia,serif; letter-spacing:0.04em;">
                    ⏱ {timeline}
                </span>
                <span style="background:rgba(96,165,250,.1); color:#93C5FD;
                    border:1px solid rgba(96,165,250,.25); border-radius:2px;
                    padding:2px 9px; font-size:11px; font-weight:600;
                    font-family:'Source Serif 4',Georgia,serif; letter-spacing:0.04em;">
                    🎯 {score}/100
                </span>
            </div>
            """, unsafe_allow_html=True)

            # Keywords
            keywords = topic.get("keywords", [])
            if keywords:
                kw_html = " ".join(
                    f"<span style='background:#2A2820;color:#D4AF37;padding:2px 7px;"
                    f"border-radius:2px;font-size:11px;margin-right:3px;"
                    f"font-family:\"JetBrains Mono\",monospace;'>{kw}</span>"
                    for kw in keywords
                )
                st.markdown(f"<div style='margin-bottom:12px;'>{kw_html}</div>",
                            unsafe_allow_html=True)

            # Why this topic
            pitch = topic.get("research_pitch", "")
            if pitch:
                st.markdown(f"""
                <div style="background:#1A1915; border-left:3px solid #C9A030;
                    padding:10px 14px; border-radius:3px; margin-bottom:12px;">
                    <div style="font-family:'Source Serif 4',Georgia,serif;
                        font-size:10px; font-weight:700; color:#D4AF37;
                        text-transform:uppercase; letter-spacing:0.09em; margin-bottom:5px;">
                        💡 Why This Topic?
                    </div>
                    <div style="font-family:'Source Serif 4',Georgia,serif;
                        color:#C8C4BC; line-height:1.75; font-size:13px;
                        font-weight:300;">{pitch}</div>
                </div>
                """, unsafe_allow_html=True)

            # Research approach
            approach = topic.get("concrete_approach", "")
            if approach:
                st.markdown("""
                <div style="font-family:'Source Serif 4',Georgia,serif;
                    font-size:12px; font-weight:600; color:#E8E4DC; margin-bottom:5px;">
                    🛠 Research Approach
                </div>
                """, unsafe_allow_html=True)
                for line in approach.split("\n"):
                    if line.strip():
                        st.markdown(
                            f'<div style="font-family:\'Source Serif 4\',Georgia,serif;'
                            f'font-size:13px;color:#C8C4BC;line-height:1.7;'
                            f'font-weight:300;margin:3px 0 3px 8px;">— {line.strip()}</div>',
                            unsafe_allow_html=True
                        )

            # Impact
            why = topic.get("why_it_matters", "")
            if why:
                st.markdown(f"""
                <div style="background:rgba(34,197,94,.05); border:1px solid rgba(34,197,94,.15);
                    padding:9px 13px; border-radius:3px; margin:10px 0;">
                    <span style="font-family:'Source Serif 4',Georgia,serif;
                        color:#4ADE80; font-weight:600; font-size:12px;">🌟 Impact: </span>
                    <span style="font-family:'Source Serif 4',Georgia,serif;
                        color:#C8C4BC; font-size:13px; font-weight:300;">{why}</span>
                </div>
                """, unsafe_allow_html=True)

            # First steps
            steps = topic.get("first_steps", "")
            if steps:
                st.markdown("""
                <div style="font-family:'Source Serif 4',Georgia,serif;
                    font-size:12px; font-weight:600; color:#E8E4DC; margin-bottom:5px;">
                    🚀 Getting Started This Week
                </div>
                """, unsafe_allow_html=True)
                for line in steps.split("\n"):
                    if line.strip():
                        st.markdown(
                            f'<div style="font-family:\'Source Serif 4\',Georgia,serif;'
                            f'font-size:13px;color:#C8C4BC;line-height:1.7;'
                            f'font-weight:300;margin:3px 0 3px 8px;">{line.strip()}</div>',
                            unsafe_allow_html=True
                        )

            # Technical details
            st.markdown("""
            <div style="font-family:'Source Serif 4',Georgia,serif;
                font-size:12px; font-weight:600; color:#9E9A8E;
                margin:12px 0 5px 0; text-transform:uppercase;
                letter-spacing:0.06em;">
                📋 Technical Details
            </div>
            """, unsafe_allow_html=True)
            st.markdown(
                f'<div style="font-family:\'JetBrains Mono\',monospace;'
                f'font-size:11px;color:#6E6A5E;line-height:1.8;">'
                f"Gap: {topic.get('original_gap','')}<br>"
                f"Category: {topic.get('category','').replace('_',' ').title()} &nbsp;|&nbsp; "
                f"Severity: {topic.get('severity','medium').upper()}"
                f"</div>",
                unsafe_allow_html=True
            )


def _render_all_topics_table(opportunities):
    st.markdown("""
    <div style="font-family:'Playfair Display',Georgia,serif;
        font-size:17px; font-weight:700; color:#E8E4DC; margin:8px 0 14px 0;">
        📊 All Research Topics
    </div>
    """, unsafe_allow_html=True)
    import pandas as pd
    all_topics = opportunities.get("hot_topics", [])
    if not all_topics:
        st.info("No topics available.")
        return
    df = pd.DataFrame([{
        "Topic":      t.get("topic_title","")[:65] + "…" if len(t.get("topic_title","")) > 65 else t.get("topic_title",""),
        "Difficulty": t.get("difficulty",""),
        "Score":      t.get("opportunity_score", 0),
        "Timeline":   t.get("estimated_timeline",""),
        "Keywords":   ", ".join(t.get("keywords",[])[:3]),
    } for t in all_topics])
    st.dataframe(df, use_container_width=True, hide_index=True)


def _build_report(opportunities) -> str:
    summary = opportunities.get("summary", {})
    hot     = opportunities.get("hot_topics", [])
    lines   = [
        "# Research Opportunity Report",
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "", "## Summary", "",
        f"- **Total Opportunities:** {summary.get('total_opportunities', 0)}",
        f"- **Quick Wins:** {summary.get('quick_win_count', 0)}",
        f"- **High Impact:** {summary.get('high_impact_count', 0)}",
        f"- **Average Score:** {summary.get('avg_opportunity_score', 0):.0f}/100",
        "", "---", "", "## Hot Topics", "",
    ]
    for i, t in enumerate(hot, 1):
        lines += [
            f"### {i}. {t.get('topic_title','')}",
            "",
            f"**Difficulty:** {t.get('difficulty','')} | "
            f"**Score:** {t.get('opportunity_score',0)}/100 | "
            f"**Timeline:** {t.get('estimated_timeline','')}",
            "",
            "**Why This Topic:**", t.get("research_pitch",""), "",
            "**Research Approach:**",
            *[f"- {l.strip()}" for l in t.get("concrete_approach","").split("\n") if l.strip()],
            "", "**First Steps:**",
            *[f"1. {l.strip()}" for l in t.get("first_steps","").split("\n") if l.strip()],
            "", "---", "",
        ]
    return "\n".join(lines)