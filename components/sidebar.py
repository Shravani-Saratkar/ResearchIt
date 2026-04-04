"""Sidebar navigation — Academic Black & Gold Theme"""
import streamlit as st


def render_sidebar() -> str:
    with st.sidebar:
        # ── Logo / Branding ──────────────────────────────────────────────
        st.markdown("""
        <div style="text-align:center; padding:28px 0 24px 0;">
            <div style="font-size:40px; margin-bottom:8px; opacity:0.95;">🔬</div>
            <h1 style="font-family:'Playfair Display',Georgia,serif;
                font-size:26px; font-weight:800; margin:0 0 4px 0; letter-spacing:-0.02em;
                background:linear-gradient(135deg,#C9A030,#D4AF37,#F0CC5A);
                -webkit-background-clip:text; -webkit-text-fill-color:transparent;
                background-clip:text;">
                ResearchIt
            </h1>
            <p style="color:#6E6A5E; font-family:'Source Serif 4',Georgia,serif;
                font-size:10px; margin:0; letter-spacing:.14em; text-transform:uppercase;
                font-weight:400;">
                AI Research Intelligence
            </p>
            <div style="margin:14px auto 0 auto; width:40px; height:1px;
                background:linear-gradient(90deg, transparent, #C9A030, transparent);"></div>
        </div>
        """, unsafe_allow_html=True)

        # ── Nav buttons ──────────────────────────────────────────────────
        pages = [
            ("discover",  "🔍  Discover Papers"),
            ("analytics", "📊  Analytics"),
            ("gaps",      "🎯  Gap Detection"),
            ("proposal",  "📄  Research Paper"),
            ("assistant", "💬  AI Assistant"),
        ]

        current = st.session_state.get("current_page", "discover")

        st.markdown("<div style='margin-bottom:8px;'></div>", unsafe_allow_html=True)

        for key, label in pages:
            if st.button(label, key=f"nav_{key}", use_container_width=True):
                st.session_state.current_page = key
                st.rerun()

        # ── Stats ────────────────────────────────────────────────────────
        st.markdown("""
        <hr style="border:none;height:1px;background:#2A2820;margin:18px 0;"/>
        """, unsafe_allow_html=True)

        papers_n = len(st.session_state.get("papers", []))
        gaps_n   = sum(
            len(v) for v in (st.session_state.get("detected_gaps") or {}).values()
        )

        c1, c2 = st.columns(2)
        for col, val, lbl in [(c1, papers_n, "PAPERS"), (c2, gaps_n, "GAPS")]:
            with col:
                st.markdown(f"""
                <div style="background:#161512; border:1px solid #2A2820; border-radius:3px;
                     padding:10px 6px; text-align:center;">
                    <div style="font-family:'Playfair Display',Georgia,serif;
                        font-size:22px; font-weight:700; color:#D4AF37; line-height:1;">
                        {val}
                    </div>
                    <div style="font-family:'Source Serif 4',Georgia,serif;
                        font-size:9px; color:#6E6A5E; text-transform:uppercase;
                        letter-spacing:0.1em; margin-top:4px;">
                        {lbl}
                    </div>
                </div>""", unsafe_allow_html=True)

        # ── Quick actions ────────────────────────────────────────────────
        st.markdown("<div style='margin-top:14px;'></div>", unsafe_allow_html=True)
        if st.button("🔄 Clear All Data", use_container_width=True):
            for k in ["papers","papers_fetched","combined_text","extracted_features",
                      "detected_gaps","interpreted_gaps","impact_matrix",
                      "relationship_graph","prototypes","generated_paper","opportunities"]:
                st.session_state[k] = (
                    [] if k == "papers" else
                    (False if k == "papers_fetched" else
                     ("" if k == "combined_text" else None))
                )
            st.rerun()

        st.markdown("""
        <div style="text-align:center; color:#3A3630;
            font-family:'JetBrains Mono',monospace;
            font-size:10px; margin-top:22px; letter-spacing:0.06em;">
            v3.0.0 · Streamlit + Groq AI
        </div>""", unsafe_allow_html=True)

    return st.session_state.get("current_page", "discover")