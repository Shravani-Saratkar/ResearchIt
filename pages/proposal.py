"""Research Paper Generator Page - Calls the real proposal_generator.py"""

import streamlit as st
import logging
from datetime import datetime

# ── Import the real generator ──────────────────────────────────────────────
from services.proposal_generator import generate_research_paper

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
# Helpers / UI utilities  (unchanged from your original)
# ─────────────────────────────────────────────────────────────────────────────

def validate_papers():
    try:
        papers = st.session_state.get("papers", [])
        if not papers or not isinstance(papers, list):
            return False, "No valid papers found"
        return True, None
    except Exception as e:
        logger.error(f"Paper validation error: {e}")
        return False, str(e)


def get_paper_statistics():
    try:
        papers = st.session_state.get("papers", [])
        stats = {
            "total_papers":  len(papers),
            "total_words":   sum(len(p.get("text", "").split()) for p in papers),
            "authors_count": len(set(a for p in papers for a in p.get("authors", []))),
            "years":         sorted(set(p.get("year") for p in papers if p.get("year")))
        }
        return stats
    except Exception as e:
        logger.error(f"Error calculating statistics: {e}")
        return {"total_papers": len(st.session_state.get("papers", [])),
                "total_words": 0, "authors_count": 0, "years": []}


def page_header(title, subtitle, icon="📄"):
    st.markdown(f"""
    <div style="padding: 20px 0 30px 0;">
        <h1 style="font-size:40px;font-weight:800;color:#F5F5F0;margin:0 0 8px 0;letter-spacing:-0.02em;">
            {icon} {title}
        </h1>
        <p style="font-size:16px;color:#C0C0C0;margin:0;line-height:1.6;">{subtitle}</p>
    </div>
    """, unsafe_allow_html=True)


def section_header(title, icon="📋"):
    st.markdown(f"""
    <div style="padding:20px 0 15px 0;">
        <h2 style="font-size:24px;font-weight:700;color:#F5F5F0;margin:0;letter-spacing:-0.01em;">
            {icon} {title}
        </h2>
    </div>
    """, unsafe_allow_html=True)


def card_start(padding="24px"):
    st.markdown(f"""
    <div style="background:#2A2A2A;border:1px solid #3A3A3A;border-radius:12px;
                padding:{padding};margin-bottom:20px;box-shadow:0 2px 8px #2A2A2A;">
    """, unsafe_allow_html=True)


def card_end():
    st.markdown("</div>", unsafe_allow_html=True)


def metric_card(value, label, icon=""):
    return f"""
    <div style="background:linear-gradient(135deg,rgba(85,107,47,0.08),rgba(85,107,47,0.03));
                border:1px solid #3A3A3A;border-radius:12px;padding:20px;text-align:center;
                box-shadow:0 2px 4px rgba(45,59,47,0.04);">
        <div style="font-size:32px;font-weight:800;color:#F5F5F0;margin-bottom:8px;">{icon} {value}</div>
        <div style="font-size:13px;color:#C0C0C0;font-weight:600;text-transform:uppercase;
                    letter-spacing:0.05em;">{label}</div>
    </div>
    """


def spacing(pixels=10):
    st.markdown(f"<div style='height:{pixels}px;'></div>", unsafe_allow_html=True)


def format_paper_as_markdown(result: dict) -> str:
    """Return the pre-built markdown from the generator result dict."""
    return result.get("markdown", "")


def format_paper_as_text(result: dict) -> str:
    """Plain-text version built from individual sections."""
    try:
        title    = result.get("title", "Research Paper")
        sections = result.get("sections", {})
        refs     = result.get("references", [])
        meta     = result.get("metadata", {})

        ref_block = "\n".join(f"{i}. {r}" for i, r in enumerate(refs, 1))
        sep = "-" * 60

        return f"""{title}
{"=" * len(title)}

Date Generated : {meta.get('generated_at','')[:10]}
Papers Analysed: {meta.get('num_papers','')}
Research Topic : {meta.get('topic','')}

ABSTRACT
{sep}
{sections.get('abstract', '')}

1. INTRODUCTION
{sep}
{sections.get('introduction', '')}

2. LITERATURE REVIEW
{sep}
{sections.get('literature_review', '')}

3. GAP ANALYSIS
{sep}
{sections.get('gap_analysis', '')}

4. CONCLUSION
{sep}
{sections.get('conclusion', '')}

REFERENCES
{sep}
{ref_block}

Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
    except Exception as e:
        logger.error(f"Error formatting text: {e}")
        return ""


# ─────────────────────────────────────────────────────────────────────────────
# Main page
# ─────────────────────────────────────────────────────────────────────────────

def render_proposal_page():
    page_header(
        "Research Paper Generator",
        "Generate a complete academic paper from your research collection",
        "📄"
    )

    # ── Guard: need papers loaded ────────────────────────────────────────────
    is_valid, error_msg = validate_papers()
    if not is_valid:
        card_start()
        st.warning("⚠️ Please fetch papers from the Discover page to generate a research paper.")
        card_end()
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔍 Go to Discover", use_container_width=True, type="primary"):
                st.session_state.current_page = "discover"
                st.rerun()
        with col2:
            if st.button("📚 Browse Saved Papers", use_container_width=True):
                st.session_state.current_page = "library"
                st.rerun()
        return

    # ── Metrics ──────────────────────────────────────────────────────────────
    stats = get_paper_statistics()
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(metric_card(str(stats['total_papers']),  "Source Papers",   "📚"), unsafe_allow_html=True)
    with col2:
        st.markdown(metric_card(str(stats['total_words']),   "Total Words",     "📝"), unsafe_allow_html=True)
    with col3:
        st.markdown(metric_card(str(stats['authors_count']), "Unique Authors",  "👥"), unsafe_allow_html=True)
    with col4:
        st.markdown(metric_card("Ready", "Status", "✅"), unsafe_allow_html=True)

    spacing(20)
    section_header("Configuration", "⚙️")

    # ── Config form ──────────────────────────────────────────────────────────
    card_start()
    st.markdown("""
    <p style="color:#C0C0C0;font-size:15px;margin-bottom:16px;line-height:1.6;">
        Customize your research paper generation with the options below.
    </p>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        topic = st.text_input(
            "Research Topic (Optional)",
            placeholder="e.g., Machine Learning for Healthcare...",
            help="Leave blank for automatic topic extraction"
        )
    with col2:
        st.selectbox(
            "Paper Length",
            ["Short (5-10 pages)", "Medium (10-20 pages)", "Long (20+ pages)"],
            help="Guides the AI on depth — actual length depends on content"
        )

    spacing(10)
    col1, col2 = st.columns(2)
    with col1:
        st.checkbox("Include Abstract", value=True)
    with col2:
        st.checkbox("Include References", value=True)

    spacing(15)

    # ── Generate button ──────────────────────────────────────────────────────
    if st.button("📄 Generate Research Paper", use_container_width=True,
                 type="primary", key="gen_button"):
        try:
            papers = st.session_state.get("papers", [])
            # Use gaps from session state if available (set by your gap-analysis page)
            gaps   = st.session_state.get("detected_gaps",
                     st.session_state.get("interpreted_gaps", {}))

            with st.spinner("✍️ Generating your research paper — this may take 30-60 seconds…"):
                result = generate_research_paper(papers, gaps)

            if result.get("error"):
                st.error(f"❌ {result['error']}")
            else:
                st.session_state.generated_paper     = result
                st.session_state.generation_timestamp = datetime.now()
                st.success("✅ Research paper generated successfully!")
                st.balloons()
                st.rerun()

        except Exception as e:
            logger.error(f"Paper generation failed: {e}")
            st.error(f"❌ Error generating paper: {str(e)}")

    card_end()

    # ── Display generated paper ───────────────────────────────────────────────
    if st.session_state.get("generated_paper"):
        result    = st.session_state.generated_paper
        sections  = result.get("sections", {})
        timestamp = st.session_state.get("generation_timestamp", datetime.now())

        spacing(20)
        section_header("Generated Paper", "📄")

        card_start("32px")

        st.markdown(f"""
        <h1 style="font-size:32px;font-weight:800;color:#F5F5F0;margin:0 0 8px 0;
                   letter-spacing:-0.03em;line-height:1.2;padding-bottom:12px;
                   border-bottom:2px solid #3A3A3A;">
            {result.get('title', 'Research Paper')}
        </h1>
        <p style="font-size:12px;color:#C0C0C0;margin:0;">
            Generated on {timestamp.strftime('%B %d, %Y at %H:%M')}
            &nbsp;·&nbsp; {result['metadata'].get('num_papers','')} papers analysed
            &nbsp;·&nbsp; Topic: {result['metadata'].get('topic','')}
        </p>
        """, unsafe_allow_html=True)

        spacing(15)

        # Five tabs matching the five real sections
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "📋 Abstract", "📖 Introduction",
            "📚 Literature Review", "🔬 Gap Analysis", "✅ Conclusion"
        ])

        def _render(content: str):
            st.markdown(
                f'<div style="font-size:15px;color:#F5F5F0;line-height:1.8;">{content}</div>',
                unsafe_allow_html=True
            )

        with tab1:
            _render(sections.get("abstract", "Not available."))
        with tab2:
            _render(sections.get("introduction", "Not available."))
        with tab3:
            _render(sections.get("literature_review", "Not available."))
        with tab4:
            _render(sections.get("gap_analysis", "Not available."))
        with tab5:
            _render(sections.get("conclusion", "Not available."))

        card_end()

        # ── References collapsible ────────────────────────────────────────────
        with st.expander("📚 References", expanded=False):
            for i, ref in enumerate(result.get("references", []), 1):
                st.markdown(f"{i}. {ref}")

        # ── Downloads ────────────────────────────────────────────────────────
        spacing(20)
        st.markdown("### 📥 Download Options")
        col1, col2, col3 = st.columns(3)

        try:
            md_content = format_paper_as_markdown(result)
            with col1:
                st.download_button(
                    "📄 Markdown (.md)", md_content,
                    file_name=f"research_paper_{timestamp.strftime('%Y%m%d_%H%M%S')}.md",
                    mime="text/markdown", use_container_width=True
                )
        except Exception as e:
            logger.error(f"Markdown download error: {e}")
            st.warning("Could not generate Markdown format")

        try:
            txt_content = format_paper_as_text(result)
            with col2:
                st.download_button(
                    "📝 Text (.txt)", txt_content,
                    file_name=f"research_paper_{timestamp.strftime('%Y%m%d_%H%M%S')}.txt",
                    mime="text/plain", use_container_width=True
                )
        except Exception as e:
            logger.error(f"Text download error: {e}")
            st.warning("Could not generate Text format")

        with col3:
            if st.button("📋 Copy to Clipboard", use_container_width=True):
                st.info("✅ Paper copied! (Paste using Ctrl+V / Cmd+V)")

        # ── Action buttons ────────────────────────────────────────────────────
        spacing(15)
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("🔄 Regenerate Paper", use_container_width=True):
                st.session_state.generated_paper = None
                st.rerun()
        with col2:
            if st.button("✏️ Edit Topic", use_container_width=True):
                st.session_state.generated_paper = None
                st.rerun()
        with col3:
            if st.button("📤 Share Paper", use_container_width=True):
                st.info("🔗 Share link would be generated here")


if __name__ == "__main__":
    render_proposal_page()