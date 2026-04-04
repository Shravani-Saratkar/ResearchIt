"""Research Paper Generator Page — Academic Theme"""

import streamlit as st
import logging
from datetime import datetime

from services.proposal_generator import generate_research_paper

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ── Helpers ───────────────────────────────────────────────────────────────────

def validate_papers():
    papers = st.session_state.get("papers", [])
    if not papers or not isinstance(papers, list):
        return False, "No valid papers found"
    return True, None


def get_paper_statistics():
    papers = st.session_state.get("papers", [])
    stats = {
        "total_papers":  len(papers),
        "total_words":   sum(len(p.get("text", "").split()) for p in papers),
        "authors_count": len(set(a for p in papers for a in p.get("authors", []))),
        "years":         sorted(set(p.get("year") for p in papers if p.get("year")))
    }
    return stats


def _page_header():
    st.markdown("""
    <div style="padding:24px 0 28px 0;">
        <h1 style="font-family:'Playfair Display',Georgia,serif;
            font-size:36px; font-weight:800; color:#E8E4DC;
            margin:0 0 8px 0; letter-spacing:-0.025em;">
            📄 Research Paper Generator
        </h1>
        <p style="font-family:'Source Serif 4',Georgia,serif;
            font-size:15px; color:#9E9A8E; margin:0; line-height:1.6; font-weight:300;">
            Generate a structured academic paper draft from your research collection
        </p>
    </div>
    """, unsafe_allow_html=True)


def _section_header(title, icon="📋"):
    st.markdown(f"""
    <div style="padding:18px 0 12px 0;">
        <h2 style="font-family:'Playfair Display',Georgia,serif;
            font-size:20px; font-weight:700; color:#E8E4DC;
            margin:0; letter-spacing:-0.01em;">
            {icon} {title}
        </h2>
    </div>
    """, unsafe_allow_html=True)


def _card_start(padding="22px"):
    st.markdown(f"""
    <div style="background:#161512; border:1px solid #2A2820; border-radius:4px;
        padding:{padding}; margin-bottom:18px;">
    """, unsafe_allow_html=True)


def _card_end():
    st.markdown("</div>", unsafe_allow_html=True)


def _metric_card(value, label, icon=""):
    return f"""
    <div style="background:#161512; border:1px solid #2A2820; border-radius:4px;
        padding:18px; text-align:center;">
        <div style="font-family:'Playfair Display',Georgia,serif;
            font-size:26px; font-weight:700; color:#D4AF37; margin-bottom:6px;">
            {icon} {value}
        </div>
        <div style="font-family:'Source Serif 4',Georgia,serif;
            font-size:11px; color:#6E6A5E; font-weight:400;
            text-transform:uppercase; letter-spacing:0.08em;">
            {label}
        </div>
    </div>
    """


def spacing(px=10):
    st.markdown(f"<div style='height:{px}px;'></div>", unsafe_allow_html=True)


def format_paper_as_markdown(result: dict) -> str:
    return result.get("markdown", "")


def format_paper_as_text(result: dict) -> str:
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


# ── Main page ─────────────────────────────────────────────────────────────────





import re as _re

def _render_ai_output(text: str):
    """
    Render AI-generated markdown with controlled typography.
    Converts ## headers and bullet points into proportional HTML
    so Streamlit's default giant heading sizes do not apply.
    """
    html_lines = []
    for line in text.split("\n"):
        s = line.strip()

        # ## Section headers  →  small gold label
        if s.startswith("## "):
            h = s[3:].strip()
            html_lines.append(
                '<div style="'
                "font-family:'Playfair Display',Georgia,serif;"
                "font-size:15px;font-weight:700;color:#D4AF37;"
                "text-transform:uppercase;letter-spacing:0.07em;"
                "margin:22px 0 8px 0;padding-bottom:5px;"
                'border-bottom:1px solid #2A2820;">'
                + h + "</div>"
            )

        # ### Sub-headers  →  slightly larger body label
        elif s.startswith("### "):
            h = s[4:].strip()
            html_lines.append(
                '<div style="'
                "font-family:'Playfair Display',Georgia,serif;"
                "font-size:14px;font-weight:600;color:#E8E4DC;"
                'margin:16px 0 5px 0;">'
                + h + "</div>"
            )

        # **Bold heading** lines (no #)
        elif _re.match(r"^\*\*.+\*\*$", s) or _re.match(r"^\*\*.+\*\*:", s):
            h = _re.sub(r"\*\*(.+?)\*\*:?", r"\1", s).strip()
            html_lines.append(
                '<div style="'
                "font-family:'Playfair Display',Georgia,serif;"
                "font-size:15px;font-weight:700;color:#D4AF37;"
                "text-transform:uppercase;letter-spacing:0.07em;"
                "margin:22px 0 8px 0;padding-bottom:5px;"
                'border-bottom:1px solid #2A2820;">'
                + h + "</div>"
            )

        # Bullet points
        elif s.startswith(("• ", "- ")):
            body = _re.sub(
                r"\*\*(.+?)\*\*",
                r'<strong style="color:#E8E4DC;font-weight:600;">\1</strong>',
                s[2:].strip()
            )
            html_lines.append(
                '<div style="display:flex;gap:10px;margin:5px 0;align-items:flex-start;">'
                '<span style="color:#C9A030;font-size:14px;flex-shrink:0;margin-top:3px;">•</span>'
                '<span style="'
                "font-family:'Source Serif 4',Georgia,serif;"
                "font-size:14px;color:#C8C4BC;line-height:1.8;font-weight:300;"
                '">' + body + "</span></div>"
            )

        # Numbered list items
        elif _re.match(r"^\d+\.\s", s):
            body = _re.sub(
                r"\*\*(.+?)\*\*",
                r'<strong style="color:#E8E4DC;font-weight:600;">\1</strong>',
                s
            )
            html_lines.append(
                '<div style="'
                "font-family:'Source Serif 4',Georgia,serif;"
                "font-size:14px;color:#C8C4BC;line-height:1.8;font-weight:300;"
                'margin:4px 0 4px 16px;">'
                + body + "</div>"
            )

        # Empty line
        elif s == "":
            html_lines.append('<div style="height:5px;"></div>')

        # Normal paragraph
        else:
            body = _re.sub(
                r"\*\*(.+?)\*\*",
                r'<strong style="color:#E8E4DC;font-weight:600;">\1</strong>',
                s
            )
            html_lines.append(
                '<div style="'
                "font-family:'Source Serif 4',Georgia,serif;"
                "font-size:14px;color:#C8C4BC;line-height:1.85;font-weight:300;"
                'margin:3px 0;">'
                + body + "</div>"
            )

    import streamlit as st
    st.markdown(
        '<div style="padding:4px 2px;">' + "\n".join(html_lines) + "</div>",
        unsafe_allow_html=True,
    )

def render_proposal_page():
    _page_header()

    is_valid, error_msg = validate_papers()
    if not is_valid:
        _card_start()
        st.warning("⚠️ Please fetch papers from the Discover page to generate a research paper.")
        _card_end()
        c1, c2 = st.columns(2)
        with c1:
            if st.button("🔍 Go to Discover", use_container_width=True, type="primary"):
                st.session_state.current_page = "discover"
                st.rerun()
        with c2:
            if st.button("📚 Browse Saved Papers", use_container_width=True):
                st.session_state.current_page = "library"
                st.rerun()
        return

    # Stats
    stats = get_paper_statistics()
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(_metric_card(str(stats['total_papers']),  "Source Papers",  "📚"),
                    unsafe_allow_html=True)
    with c2:
        st.markdown(_metric_card(str(stats['total_words']),   "Total Words",    "📝"),
                    unsafe_allow_html=True)
    with c3:
        st.markdown(_metric_card(str(stats['authors_count']), "Unique Authors", "👥"),
                    unsafe_allow_html=True)
    with c4:
        st.markdown(_metric_card("Ready", "Status", "✅"),
                    unsafe_allow_html=True)

    spacing(18)
    _section_header("Configuration", "⚙️")

    _card_start()
    st.markdown("""
    <p style="font-family:'Source Serif 4',Georgia,serif; color:#9E9A8E;
        font-size:14px; margin-bottom:16px; line-height:1.7; font-weight:300;">
        Customise your research paper generation below.
        Leave the topic blank for automatic extraction from paper titles.
    </p>
    """, unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        topic = st.text_input(
            "Research Topic (Optional)",
            placeholder="e.g., Transformer Models for Medical Imaging…",
            help="Leave blank for automatic topic extraction from paper titles"
        )
    with c2:
        st.selectbox(
            "Paper Length",
            ["Short (5–10 pages)", "Medium (10–20 pages)", "Long (20+ pages)"],
            help="Guides the AI on depth — actual length depends on content"
        )

    spacing(8)
    c1, c2 = st.columns(2)
    with c1:
        st.checkbox("Include Abstract",    value=True)
    with c2:
        st.checkbox("Include References",  value=True)

    spacing(14)

    if st.button("📄 Generate Research Paper", use_container_width=True,
                 type="primary", key="gen_button"):
        try:
            papers = st.session_state.get("papers", [])
            gaps   = st.session_state.get(
                "detected_gaps",
                st.session_state.get("interpreted_gaps", {})
            )
            with st.spinner(
                "Generating your research paper draft — this may take 30–60 seconds…"
            ):
                result = generate_research_paper(papers, gaps)

            if result.get("error"):
                st.error(f"❌ {result['error']}")
            else:
                st.session_state.generated_paper      = result
                st.session_state.generation_timestamp = datetime.now()
                st.success("✅ Research paper draft generated successfully!")
                st.balloons()
                st.rerun()

        except Exception as e:
            logger.error(f"Paper generation failed: {e}")
            st.error(f"❌ Error generating paper: {str(e)}")

    _card_end()

    # ── Display generated paper ───────────────────────────────────────────
    if not st.session_state.get("generated_paper"):
        return

    result    = st.session_state.generated_paper
    sections  = result.get("sections", {})
    timestamp = st.session_state.get("generation_timestamp", datetime.now())

    spacing(16)
    _card_start("28px")

    st.markdown(f"""
    <div style="border-bottom:1px solid #2A2820; padding-bottom:14px; margin-bottom:18px;">
        <div style="font-family:'Playfair Display',Georgia,serif;
            font-size:19px; font-weight:700; color:#E8E4DC;
            margin:0 0 8px 0; letter-spacing:-0.01em; line-height:1.35;">
            {result.get('title', 'Research Paper')}
        </div>
        <span style="font-family:'JetBrains Mono',monospace; font-size:11px;
            color:#6E6A5E; letter-spacing:0.04em;">
            {timestamp.strftime('%B %d, %Y')} &nbsp;·&nbsp;
            {result['metadata'].get('num_papers','')} papers analysed
        </span>
    </div>
    """, unsafe_allow_html=True)

    spacing(8)

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📋 Abstract",
        "📖 Introduction",
        "📚 Literature Review",
        "🔬 Gap Analysis",
        "✅ Conclusion"
    ])

    def _render_section(content: str):
        _render_ai_output(content)

    with tab1:
        _render_section(sections.get("abstract", "Not available."))
    with tab2:
        _render_section(sections.get("introduction", "Not available."))
    with tab3:
        _render_section(sections.get("literature_review", "Not available."))
    with tab4:
        _render_section(sections.get("gap_analysis", "Not available."))
    with tab5:
        _render_section(sections.get("conclusion", "Not available."))

    _card_end()

    # References
    with st.expander("📚 References", expanded=False):
        for i, ref in enumerate(result.get("references", []), 1):
            st.markdown(
                f"<p style='font-family:\"Source Serif 4\",Georgia,serif; "
                f"font-size:13px; color:#9E9A8E; line-height:1.7; "
                f"font-weight:300; margin-bottom:6px;'>{i}. {ref}</p>",
                unsafe_allow_html=True
            )

    # Downloads
    spacing(18)
    st.markdown("""
    <div style="font-family:'Playfair Display',Georgia,serif;
        font-size:17px; font-weight:700; color:#E8E4DC; margin-bottom:12px;">
        📥 Download Draft
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)

    try:
        md_content = format_paper_as_markdown(result)
        with c1:
            st.download_button(
                "📄 Markdown (.md)", md_content,
                file_name=f"paper_{timestamp.strftime('%Y%m%d_%H%M%S')}.md",
                mime="text/markdown", use_container_width=True
            )
    except Exception as e:
        logger.error(f"Markdown download error: {e}")

    try:
        txt_content = format_paper_as_text(result)
        with c2:
            st.download_button(
                "📝 Plain Text (.txt)", txt_content,
                file_name=f"paper_{timestamp.strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain", use_container_width=True
            )
    except Exception as e:
        logger.error(f"Text download error: {e}")

    with c3:
        if st.button("📋 Copy to Clipboard", use_container_width=True):
            st.info("✅ Paper content ready — use Ctrl+V / Cmd+V to paste.")

    # Action buttons
    spacing(14)
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("🔄 Regenerate Paper", use_container_width=True):
            st.session_state.generated_paper = None
            st.rerun()
    with c2:
        if st.button("✏️ Edit Topic", use_container_width=True):
            st.session_state.generated_paper = None
            st.rerun()
    with c3:
        if st.button("📤 Share Paper", use_container_width=True):
            st.info("🔗 Share link would be generated here")


if __name__ == "__main__":
    render_proposal_page()