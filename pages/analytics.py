"""Analytics Page — Academic Theme"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from collections import Counter
from datetime import datetime
import pandas as pd

# Shared plotly theme
_PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Source Serif 4, Georgia, serif", color="#C8C4BC", size=13),
    xaxis=dict(
        showgrid=False, color="#6E6A5E",
        linecolor="#2A2820", tickfont=dict(size=11)
    ),
    yaxis=dict(
        showgrid=True, gridcolor="rgba(42,40,32,0.8)",
        color="#6E6A5E", linecolor="#2A2820", tickfont=dict(size=11)
    ),
    margin=dict(t=40, b=40, l=40, r=20),
)


def _section_title(text: str):
    st.markdown(f"""
    <div style="font-family:'Playfair Display',Georgia,serif;
        font-size:20px; font-weight:700; color:#E8E4DC;
        margin:24px 0 16px 0; padding-bottom:8px;
        border-bottom:1px solid #2A2820; letter-spacing:-0.01em;">
        {text}
    </div>
    """, unsafe_allow_html=True)


def _stat_box(value, label, colour="#D4AF37"):
    return f"""
    <div style="background:#161512; border:1px solid #2A2820; border-radius:4px;
        padding:18px; text-align:center;">
        <div style="font-family:'Playfair Display',Georgia,serif;
            font-size:28px; font-weight:700; color:{colour}; margin-bottom:4px;">
            {value}
        </div>
        <div style="font-family:'Source Serif 4',Georgia,serif; font-size:11px;
            color:#6E6A5E; text-transform:uppercase; letter-spacing:0.08em;
            font-weight:400;">
            {label}
        </div>
    </div>
    """


def render_analytics_page():
    st.markdown("""
    <div style="background:linear-gradient(135deg,#1A1915 0%,#161512 50%,#1E1B16 100%);
        border:1px solid #2E2B22; border-radius:4px; padding:48px 40px;
        text-align:center; margin-bottom:28px; position:relative; overflow:hidden;">
        <div style="position:absolute;top:0;left:0;right:0;bottom:0;
            background:radial-gradient(ellipse at 50% 0%,rgba(212,175,55,0.06) 0%,transparent 65%);
            pointer-events:none;"></div>
        <div style="font-family:'Playfair Display',Georgia,serif;
            font-size:36px; font-weight:800; letter-spacing:-0.025em;
            background:linear-gradient(135deg,#C9A030,#D4AF37,#F0CC5A);
            -webkit-background-clip:text; -webkit-text-fill-color:transparent;
            background-clip:text; margin-bottom:12px;">
            📊 Research Analytics
        </div>
        <p style="font-family:'Source Serif 4',Georgia,serif; color:#9E9A8E;
            font-size:15px; margin:0; font-weight:300; line-height:1.7;">
            Deep visualisations and statistical insights from your paper corpus
        </p>
    </div>
    """, unsafe_allow_html=True)

    if not st.session_state.papers_fetched or not st.session_state.papers:
        st.markdown("""
        <div style="background:#161512; border:1px solid #2A2820; border-radius:4px;
            text-align:center; padding:60px 40px;">
            <div style="font-size:48px; margin-bottom:16px; opacity:0.2;">📊</div>
            <h2 style="font-family:'Playfair Display',Georgia,serif;
                color:#E8E4DC; margin-bottom:12px; font-size:20px;">
                No Data Available
            </h2>
            <p style="font-family:'Source Serif 4',Georgia,serif;
                color:#9E9A8E; font-size:14px; font-weight:300;">
                Search for papers in the Discover section first.
            </p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("🔍 Go to Discover", use_container_width=True, type="primary"):
            st.session_state.current_page = "discover"
            st.rerun()
        return

    papers = st.session_state.papers

    tab1, tab2, tab3, tab4 = st.tabs(
        ["📈 Trends", "👥 Authors", "🔤 Keywords", "📊 Statistics"]
    )

    # ── Trends ────────────────────────────────────────────────────────────
    with tab1:
        _section_title("Publication Trends Over Time")

        years = []
        for paper in papers:
            if paper.get("published"):
                try:
                    year = datetime.fromisoformat(
                        paper["published"].replace("Z", "+00:00")
                    ).year
                    years.append(year)
                except Exception:
                    pass

        if years:
            year_counts  = Counter(years)
            sorted_years = sorted(year_counts.items())

            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=[y[0] for y in sorted_years],
                y=[y[1] for y in sorted_years],
                mode="lines+markers",
                line=dict(color="#D4AF37", width=2.5),
                marker=dict(size=8, color="#D4AF37",
                            line=dict(color="#0F0F0E", width=2)),
                fill="tozeroy",
                fillcolor="rgba(201,160,48,0.08)"
            ))
            layout = dict(**_PLOTLY_LAYOUT)
            layout["title"] = dict(
                text="Publications per Year",
                font=dict(family="Playfair Display, Georgia, serif",
                          size=16, color="#E8E4DC"),
                x=0
            )
            fig.update_layout(**layout)
            st.plotly_chart(fig, use_container_width=True)

            c1, c2 = st.columns(2)
            peak_year = max(year_counts.items(), key=lambda x: x[1])
            growth    = (
                (sorted_years[-1][1] - sorted_years[0][1]) / sorted_years[0][1] * 100
                if len(sorted_years) > 1 else 0
            )
            with c1:
                st.markdown(_stat_box(str(peak_year[0]),
                                      f"Peak Year ({peak_year[1]} papers)"),
                            unsafe_allow_html=True)
            with c2:
                colour = "#22c55e" if growth >= 0 else "#ef4444"
                st.markdown(_stat_box(f"{growth:+.1f}%",
                                      f"Growth {sorted_years[0][0]}→{sorted_years[-1][0]}",
                                      colour),
                            unsafe_allow_html=True)
        else:
            st.info("No publication date information available.")

    # ── Authors ───────────────────────────────────────────────────────────
    with tab2:
        _section_title("Author Analysis")

        all_authors  = [a for p in papers for a in p["authors"]]
        author_counts = Counter(all_authors)
        top_authors  = author_counts.most_common(15)

        fig = go.Figure(data=[
            go.Bar(
                x=[count for _, count in top_authors],
                y=[author for author, _ in top_authors],
                orientation="h",
                marker=dict(
                    color=[count for _, count in top_authors],
                    colorscale=[[0, "#2A2820"], [0.5, "#C9A030"], [1, "#F0CC5A"]],
                    showscale=False,
                    line=dict(color="#0F0F0E", width=0.5)
                )
            )
        ])
        layout = dict(**_PLOTLY_LAYOUT)
        layout["title"] = dict(
            text="Top 15 Most Prolific Authors",
            font=dict(family="Playfair Display, Georgia, serif",
                      size=16, color="#E8E4DC"),
            x=0
        )
        layout["height"] = 480
        fig.update_layout(**layout)
        st.plotly_chart(fig, use_container_width=True)

        c1, c2, c3 = st.columns(3)
        avg_authors = sum(len(p["authors"]) for p in papers) / len(papers)
        unique_auth = len(set(all_authors))
        max_authors = max(len(p["authors"]) for p in papers)
        with c1:
            st.markdown(_stat_box(f"{avg_authors:.1f}", "Avg Authors / Paper"),
                        unsafe_allow_html=True)
        with c2:
            st.markdown(_stat_box(str(unique_auth), "Unique Authors"),
                        unsafe_allow_html=True)
        with c3:
            st.markdown(_stat_box(str(max_authors), "Max Authors (1 Paper)"),
                        unsafe_allow_html=True)

    # ── Keywords ──────────────────────────────────────────────────────────
    with tab3:
        _section_title("Keyword Frequency in Titles")

        import re
        stopwords = {
            "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for",
            "of", "with", "by", "from", "as", "is", "are", "was", "were", "be",
            "using", "based", "via", "its", "their", "this", "that", "we", "our"
        }
        word_freq = Counter()
        for paper in papers:
            title = paper["title"].lower()
            for word in re.findall(r"\b[a-z]{4,}\b", title):
                if word not in stopwords:
                    word_freq[word] += 1

        top_kw = word_freq.most_common(20)

        fig = go.Figure(data=[
            go.Bar(
                x=[word for word, _ in top_kw],
                y=[count for _, count in top_kw],
                marker=dict(
                    color=[count for _, count in top_kw],
                    colorscale=[[0, "#2A2820"], [0.5, "#C9A030"], [1, "#F0CC5A"]],
                    showscale=False,
                    line=dict(color="#0F0F0E", width=0.5)
                )
            )
        ])
        layout = dict(**_PLOTLY_LAYOUT)
        layout["title"] = dict(
            text="Top 20 Keywords in Paper Titles",
            font=dict(family="Playfair Display, Georgia, serif",
                      size=16, color="#E8E4DC"),
            x=0
        )
        layout["xaxis"]["tickangle"] = -40
        fig.update_layout(**layout)
        st.plotly_chart(fig, use_container_width=True)

    # ── Statistics ────────────────────────────────────────────────────────
    with tab4:
        _section_title("Statistical Summary")

        data = []
        for paper in papers:
            year = ""
            if paper.get("published"):
                try:
                    year = datetime.fromisoformat(
                        paper["published"].replace("Z", "+00:00")
                    ).year
                except Exception:
                    pass
            data.append({
                "Title":        paper["title"][:55] + "…"
                                if len(paper["title"]) > 55 else paper["title"],
                "Authors":      len(paper["authors"]),
                "Year":         year,
                "First Author": paper["authors"][0] if paper["authors"] else "Unknown",
            })

        df = pd.DataFrame(data)
        st.dataframe(df, use_container_width=True, height=420)

        csv = df.to_csv(index=False)
        st.download_button(
            "📥 Download Dataset (CSV)",
            csv,
            "research_papers.csv",
            "text/csv",
            key="download-analytics-csv",
            use_container_width=True
        )