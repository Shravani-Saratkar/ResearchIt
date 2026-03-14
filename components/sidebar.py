"""Sidebar navigation - Original Black & Gold Theme"""
import streamlit as st


def render_sidebar() -> str:
    with st.sidebar:
        # ── Logo ────────────────────────────────────────────────────────
        st.markdown("""
        <div style="text-align:center; padding:20px 0 28px 0;">
            <div style="font-size:44px;">🔬</div>
            <h1 style="font-size:26px; font-weight:800; margin:6px 0 0 0;
                background:linear-gradient(135deg,#D4AF37,#FFD700);
                -webkit-background-clip:text; -webkit-text-fill-color:transparent;">
                ResearchIt
            </h1>
            <p style="color:#808080; font-size:11px; margin:4px 0 0 0; letter-spacing:.1em;">
                AI RESEARCH INTELLIGENCE
            </p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<hr style='margin:0 0 20px 0;'>", unsafe_allow_html=True)

        # ── Nav buttons ─────────────────────────────────────────────────
        pages = [
            ("discover",  "🔍  Discover Papers"),
            ("analytics", "📊  Analytics"),
            ("gaps",      "🎯  Gap Detection"),
            ("proposal",  "📄  Research Paper"),
            ("assistant", "💬  AI Assistant"),
        ]

        current = st.session_state.get("current_page", "discover")

        for key, label in pages:
            active_style = (
                "background:linear-gradient(135deg,#D4AF37,#C9A636)!important;"
                "color:#1A1A1A!important; font-weight:700!important;"
            ) if key == current else ""
            if st.button(label, key=f"nav_{key}", use_container_width=True):
                st.session_state.current_page = key
                st.rerun()

        # ── Stats ───────────────────────────────────────────────────────
        st.markdown("<hr>", unsafe_allow_html=True)
        papers_n = len(st.session_state.get("papers", []))
        gaps_n   = sum(
            len(v) for v in (st.session_state.get("detected_gaps") or {}).values()
        )

        c1, c2 = st.columns(2)
        for col, val, lbl in [(c1, papers_n, "PAPERS"), (c2, gaps_n, "GAPS")]:
            with col:
                st.markdown(f"""
                <div style="background:#2A2A2A; border:1px solid #3A3A3A; border-radius:10px;
                     padding:12px; text-align:center;">
                    <div style="font-size:22px; font-weight:700; color:#D4AF37;">{val}</div>
                    <div style="font-size:10px; color:#808080; text-transform:uppercase;">{lbl}</div>
                </div>""", unsafe_allow_html=True)

        # ── Quick actions ────────────────────────────────────────────────
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🔄 Clear All Data", use_container_width=True):
            for k in ["papers","papers_fetched","combined_text","extracted_features",
                      "detected_gaps","interpreted_gaps","impact_matrix",
                      "relationship_graph","prototypes","generated_paper","opportunities"]:
                st.session_state[k] = [] if k == "papers" else (False if k == "papers_fetched" else ("" if k == "combined_text" else None))
            st.rerun()

        st.markdown("""
        <div style="text-align:center; color:#4A4A4A; font-size:11px; margin-top:20px;">
            v3.0.0 · Streamlit + Gemini AI
        </div>""", unsafe_allow_html=True)

    return st.session_state.get("current_page", "discover")